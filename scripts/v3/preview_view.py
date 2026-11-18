#!/usr/bin/env python3
"""Offline preview of a CasaRay V3 native view.  DEVELOPMENT ONLY — NOT DEPLOYED.

    python3 scripts/v3/preview_view.py home --out DIR [--dashboard PATH]
            [--scenario normal|dark] [--icons DIR] [--label TEXT] [--shots]
    python3 scripts/v3/preview_view.py --side-by-side BEFORE.png AFTER.png OUT.png
            [--captions "Before" "After"] [--crop-height PX]

Writes DIR/<view>.html: the view's sections laid out with Home Assistant's own
sections-view CSS (frontend 20260826.7, see ha_layout.py). Every card sits at
the size the frontend would give it — the card's own minimums applied, a
two-column band on 24 units — and every template is rendered against the
offline fixture (render_check.py).

What it is NOT: a screenshot of Home Assistant. The GEOMETRY is the
frontend's; the pixels INSIDE each card are drawn here to approximate the
native card (tile, button, markdown, heading, weather, camera, to-do). Fonts,
icon sizes and the camera image differ from the device. Values are the
fixture's synthetic states, never live readings.

--shots captures the wall iPad (1180 x 820) and a phone (390 x 844), full
page, with Chromium through Playwright (node). --icons points at a folder of
Material Design Icons SVGs named <icon>.svg; without one, icons are dots.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ha_layout as L  # noqa: E402
import render_check as R  # noqa: E402

ROOT = HERE.parents[1]
VIEWPORTS = {"ipad": (1180, 820), "phone": (390, 844)}

# Demo attributes for the preview only, shown where the fixture has no
# attribute; never read from a device. Values are illustrative.
DEMO_ATTRS = {
    "weather.forecast_home": {"temperature": 10, "humidity": 96, "temperature_unit": "°C"},
    "sensor.casa_monitored_power": {"unit_of_measurement": "W"},
    "sensor.casa_solar_expected_today": {"unit_of_measurement": "kWh"},
    "sensor.g_monitor_freezer_p110m_current_consumption": {"unit_of_measurement": "W"},
    "sensor.r_energy_monitor_p110m_current_consumption": {"unit_of_measurement": "W"},
    "sensor.powerpal_gateway_powerpal_daily_energy": {"unit_of_measurement": "kWh"},
    "sensor.primo_5_0_1_1_energy_day": {"unit_of_measurement": "kWh"},
    "sensor.living_room_living_room_temperature": {"unit_of_measurement": "°C"},
    "sensor.kitchen_electrolux_fridge_temperature": {"unit_of_measurement": "°C"},
}

ACTIVE = {"on", "home", "open", "opening", "playing", "streaming", "recording", "cool", "heat",
          "dry", "fan_only", "auto", "heat_cool", "detected"}
WEATHER = {"partlycloudy": "Partly cloudy", "cloudy": "Cloudy", "sunny": "Sunny", "rainy": "Rainy",
           "clear-night": "Clear, night", "pouring": "Pouring", "fog": "Fog", "windy": "Windy"}


# ------------------------------------------------------------------ markdown

def _inline(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md_to_html(text):
    """The subset of marked (GFM, breaks on) V3 templates emit: ATX headings,
    '-' lists, paragraphs, single newlines as <br>, inline HTML passed through."""
    out, para, items = [], [], []

    def flush():
        if para:
            out.append("<p>" + "<br>".join(_inline(x) for x in para) + "</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join("<li>" + "<br>".join(_inline(y) for y in it) + "</li>"
                                        for it in items) + "</ul>")
            items.clear()

    for line in text.split("\n"):
        if not line.strip():
            flush()
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush()
            n = len(m.group(1))
            out.append(f"<h{n}>{_inline(m.group(2))}</h{n}>")
        elif re.match(r"^[-*]\s+", line):
            if para:
                flush()
            items.append([re.sub(r"^[-*]\s+", "", line)])
        elif items:
            items[-1].append(line)
        else:
            para.append(line)
    flush()
    return "".join(out)


# ------------------------------------------------------------------ state

def friendly(e, names):
    return names.get(e) or e.split(".", 1)[1].replace("_", " ").capitalize()


def state_text(e, s, attrs):
    dom = e.split(".")[0]
    if s == "unavailable":
        return "Unavailable"
    if s in ("unknown", "none", ""):
        return "Unknown"
    if dom == "person":
        return {"home": "Home", "not_home": "Away"}.get(s, s.replace("_", " ").capitalize())
    if dom == "binary_sensor":
        if "door" in e:
            return {"on": "Open", "off": "Closed"}.get(s, s)
        if "motion" in e or "occup" in e:
            return {"on": "Detected", "off": "Clear"}.get(s, s)
        if "connection" in e or "wan_status" in e:
            return {"on": "Connected", "off": "Disconnected"}.get(s, s)
        return {"on": "On", "off": "Off"}.get(s, s)
    if dom == "weather":
        return WEATHER.get(s, s.capitalize())
    if R._is_number(s):
        u = (attrs.get(e) or {}).get("unit_of_measurement")
        return f"{s} {u}" if u else s
    return s.replace("_", " ").capitalize()


def icon_for(card, e, s):
    if card.get("icon"):
        return card["icon"].split(":", 1)[1]
    dom = e.split(".")[0] if e else ""
    if dom == "person":
        return "account"
    if dom == "light":
        return "lightbulb" if s == "on" else "lightbulb-outline"
    if dom == "binary_sensor":
        if "door" in e:
            return "door-open" if s == "on" else "door-closed"
        if "motion" in e or "occup" in e:
            return "motion-sensor" if s == "on" else "motion-sensor-off"
        return "check-circle-outline"
    if dom == "sensor":
        if "temperature" in e:
            return "thermometer"
        if "rising" in e:
            return "weather-sunset-up"
        if "setting" in e:
            return "weather-sunset-down"
        if "power" in e or "consumption" in e or "energy" in e:
            return "flash"
        return "eye"
    if dom == "climate":
        return "air-conditioner"
    if dom == "cover":
        return "blinds"
    if dom == "switch":
        return "power-plug" if s == "on" else "power-plug-off-outline"
    if dom == "camera":
        return "video" if s not in ("unavailable",) else "video-off"
    return "eye"


class Icons:
    def __init__(self, folder):
        self.folder = Path(folder) if folder else None

    def svg(self, name, cls="ic"):
        if self.folder:
            p = self.folder / f"{name}.svg"
            if p.is_file():
                m = re.search(r'<path[^>]*\sd="([^"]+)"', p.read_text(encoding="utf-8"))
                if m:
                    return f'<svg class="{cls}" viewBox="0 0 24 24"><path d="{m.group(1)}"/></svg>'
        return f'<svg class="{cls}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/></svg>'


# ------------------------------------------------------------------ cards

def shown(card, states):
    return L.visible(card, states)


def render_card(card, ctx):
    t = card.get("type")
    states, attrs, names, icons, env = ctx["states"], ctx["attrs"], ctx["names"], ctx["icons"], ctx["env"]
    tappable = " tap" if (card.get("tap_action") or {}).get("action") not in (None, "none") else ""
    if t == "markdown":
        body = md_to_html(env.from_string(card["content"]).render())
        plain = " text-only" if card.get("text_only") else ""
        return f'<div class="ha-card md{plain}{tappable}">{body}</div>'
    if t == "heading":
        cls = "heading sub" if card.get("heading_style") == "subtitle" else "heading"
        return f'<div class="{cls}"><span>{html.escape(card.get("heading", ""))}</span></div>'
    if t == "tile":
        e = card["entity"]
        s = states.get(e, "unknown")
        name = card.get("name") or friendly(e, names)
        st = state_text(e, s, attrs)
        sc = card.get("state_content")
        if isinstance(sc, list) and "last_changed" in sc:
            st += ' · <span class="ph">time since change</span>'
        tone = "off" if s in ("unavailable", "unknown") else ("on" if s in ACTIVE else "")
        vert = " vertical" if card.get("vertical") else ""
        feat = '<div class="feature"><div class="bar"></div></div>' if card.get("features") else ""
        return (f'<div class="ha-card tile{vert}{tappable}"><div class="tc"><div class="ib {tone}">'
                f'{icons.svg(icon_for(card, e, s))}</div><div class="tx"><div class="nm">'
                f'{html.escape(str(name))}</div><div class="st">{st}</div></div></div>{feat}</div>')
    if t == "button":
        name = html.escape(str(card.get("name", ""))) if card.get("show_name", True) else ""
        ic = icons.svg(card["icon"].split(":", 1)[1], "bic") if card.get("icon") and card.get("show_icon", True) else ""
        nm = f'<div class="bn">{name}</div>' if name else ""
        tint = " accent" if card.get("color") in ("accent", "primary", "amber") else ""
        return f'<div class="ha-card btn{tint}{tappable}">{ic}{nm}</div>'
    if t == "weather-forecast":
        e = card["entity"]
        s = states.get(e, "unknown")
        a = attrs.get(e) or {}
        temp = f'{a["temperature"]}°' if "temperature" in a else "—"
        hum = f' · humidity {a["humidity"]}%' if "humidity" in a else ""
        return (f'<div class="ha-card weather"><div class="wi">{icons.svg("weather-partly-cloudy", "wic")}</div>'
                f'<div><div class="wt">{temp}</div><div class="ws">{state_text(e, s, attrs)}{hum}</div></div></div>')
    if t == "picture-entity":
        e = card["entity"]
        s = states.get(e, "unknown")
        off = s in ("unavailable", "unknown")
        # Home Assistant draws a dark camera as a broken image or a spinner,
        # with no state word (hui-image.ts, 20260826.7): the annotation is the
        # preview's, not the card's.
        badge = "preview note: HA shows a broken image, no word" if off else "camera image — not rendered offline"
        return (f'<div class="ha-card cam{" camoff" if off else ""}{tappable}">{icons.svg("cctv", "cic")}'
                f'<div class="cbadge">{badge}</div><div class="cname">{html.escape(str(card.get("name", "")))}</div></div>')
    if t == "todo-list":
        n = states.get(card["entity"], "0")
        k = int(float(n)) if R._is_number(n) else 0
        rows = "".join(f'<div class="ti"><span class="cb"></span><span class="ph">item {i + 1} — names not in the fixture</span></div>'
                       for i in range(min(k, 5)))
        return f'<div class="ha-card todo"><div class="add">Add item</div>{rows}</div>'
    return f'<div class="ha-card md"><p class="ph">{html.escape(str(t))} — not drawn offline</p></div>'


CSS = """
:root{--v3-page:#0d1114;--v3-card:#161b1f;--v3-elevated:#1a1f25;--v3-border:rgba(160,190,220,.14);
--v3-text:#eef2f7;--v3-text-2:#a9b4c3;--v3-accent:#e8a33d;--v3-ok:#5fd39a;--v3-alert:#f07a7a;--v3-muted:#9aa3ae}
html,body{margin:0}
body{background:radial-gradient(120% 80% at 50% -10%,rgba(70,110,160,.22),transparent 60%),#0d1114;
background-attachment:scroll;color:var(--v3-text);font-family:Inter,-apple-system,'Segoe UI','Noto Sans SC','IPAGothic',sans-serif;
font-size:14px;line-height:1.55;min-height:100vh}
.view{--row-gap:24px;--column-gap:32px;--column-max-width:500px;display:block}
@media (max-width:600px){.view{--column-gap:8px}}
.wrapper{display:flex;flex-direction:column;padding:0 var(--column-gap);box-sizing:content-box;margin:0 auto;
max-width:calc(var(--column-count)*var(--column-max-width) + (var(--column-count) - 1)*var(--column-gap))}
.container{display:grid;grid-template-columns:repeat(var(--content-column-count),1fr);gap:var(--row-gap) var(--column-gap);
padding:var(--row-gap) 0;align-items:flex-start}
.section{grid-column:span var(--column-span);min-width:0}
.grid{--grid-column-count:calc(12*var(--column-span));display:grid;grid-template-columns:repeat(var(--grid-column-count),minmax(0,1fr));
grid-auto-rows:auto;row-gap:8px;column-gap:8px}
.card{position:relative;grid-row:span var(--row-size,1);grid-column:span min(var(--column-size,1),var(--grid-column-count));min-width:0}
.card.fit-rows{height:calc(var(--row-size,1)*(56px + 8px) - 8px)}
.card.full-width{grid-column:1/-1}
.ha-card{background:var(--v3-card);border:1px solid var(--v3-border);border-radius:18px;box-sizing:border-box;height:100%;overflow:hidden}
.md{padding:16px;overflow-y:auto;word-wrap:break-word}
.md>*:first-child{margin-top:0}.md>*:last-child{margin-bottom:0}
.md p{margin:1em 0}.md h2{font-size:20px;font-weight:700;line-height:normal;margin:.83em 0}
.md h3{font-size:1.17em;font-weight:700;line-height:normal;margin:1em 0}.md ul{margin:1em 0;padding-left:40px}
.md small{color:var(--v3-text-2)}.md strong{font-weight:700}
.md.text-only{background:none;border:none;padding:2px 4px}
.heading{display:flex;align-items:flex-end;min-height:24px;height:100%;padding:0 4px;font-size:16px}
.heading.sub{font-size:14px;color:var(--v3-text-2)}
.tile{display:flex;flex-direction:column;justify-content:center}
.tc{display:flex;align-items:center;gap:10px;padding:10px;min-height:54px;box-sizing:border-box}
.tile.vertical .tc{flex-direction:column;justify-content:center;text-align:center;gap:6px;height:100%}
.ib{width:36px;height:36px;border-radius:50%;flex:none;display:flex;align-items:center;justify-content:center;
background:rgba(169,180,195,.12);fill:var(--v3-text-2)}
.ib.on{background:rgba(232,163,61,.2);fill:var(--v3-accent)}.ib.off{background:rgba(154,163,174,.12);fill:var(--v3-muted)}
.ic{width:22px;height:22px}.tx{min-width:0}.nm{font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.st{font-size:12px;color:var(--v3-text-2);line-height:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.feature{padding:0 10px 10px}.bar{height:34px;border-radius:12px;background:rgba(232,163,61,.18)}
/* hui-button-card at 20260826.7: label --ha-font-size-l at line-height 1.2, no padding and no ellipsis
   (ha-card clips it); icon 40% of the card's width, at most 80% of its height; `color` tints the icon */
.btn{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:4% 0;font-size:16px;line-height:1.2;
fill:var(--v3-text-2);position:relative}.btn.accent{fill:var(--v3-accent)}
.bic{width:40%;max-height:80%;height:auto;aspect-ratio:1}.bn{margin-top:8px;text-align:center}
.weather{display:flex;align-items:center;gap:16px;padding:16px}.wic{width:64px;height:64px;fill:var(--v3-text-2)}
.wt{font-size:28px;line-height:1.2}.ws{color:var(--v3-text-2)}
.cam{display:flex;align-items:center;justify-content:center;background:linear-gradient(160deg,#25313b,#10161b);position:relative}
.camoff{background:#1b1f23}.cic{width:56px;height:56px;fill:rgba(169,180,195,.35)}
.cbadge{position:absolute;top:10px;right:10px;font-size:11px;color:var(--v3-text-2);border:1px solid var(--v3-border);
border-radius:999px;padding:2px 8px;background:rgba(0,0,0,.25)}
.cname{position:absolute;left:0;right:0;bottom:0;padding:10px 16px;background:rgba(0,0,0,.35);font-weight:500}
.todo{padding:12px 16px}.add{border:1px solid var(--v3-border);border-radius:10px;padding:8px 12px;color:var(--v3-text-2);margin-bottom:8px}
.ti{display:flex;gap:10px;align-items:center;padding:6px 0}.cb{width:16px;height:16px;border:2px solid var(--v3-text-2);border-radius:4px;flex:none}
.ph{color:var(--v3-muted);font-style:italic}
.tag{position:absolute;top:6px;right:8px;z-index:9;font-size:10px;line-height:1.3;color:#ffd38a;background:rgba(40,28,8,.85);
border:1px solid rgba(232,163,61,.5);border-radius:6px;padding:3px 6px;max-width:300px;text-align:right}
"""

JS = """
(function(){
  var view=document.querySelector('.view'), maxc=+view.dataset.maxColumns, spans=JSON.parse(view.dataset.spans);
  function layout(){
    var w=document.documentElement.clientWidth, gap=w<=600?8:32;
    var cols=Math.max(Math.floor((w-2*gap+gap)/(320+gap)),1);
    cols=Math.min(Math.max(cols,1),maxc);
    var total=spans.reduce(function(a,b){return a+b},0), cc=Math.max(Math.min(cols,total),1);
    var wr=document.querySelector('.wrapper');
    wr.style.setProperty('--column-count',cc); wr.style.setProperty('--content-column-count',cc);
    document.querySelectorAll('.section').forEach(function(s){
      s.style.setProperty('--column-span',Math.min(+s.dataset.span,cc));});
    document.body.dataset.columns=cc;
  }
  layout(); window.addEventListener('resize',layout);
})();
"""


def page(view, states, attrs, names, icons, label):
    env = R.env_for(states, attrs)
    ctx = {"states": states, "attrs": attrs, "names": names, "icons": icons, "env": env}
    secs = []
    spans = []
    for s in view["sections"]:
        span = s.get("column_span", 1)
        spans.append(span)
        cards = []
        for c in s.get("cards", []):
            if not shown(c, states):
                continue
            cols, rows = L.effective(c)
            style, cls = [], ["card"]
            if cols == "full":
                cls.append("full-width")
            else:
                style.append(f"--column-size:{cols}")
            if isinstance(rows, (int, float)):
                style.append(f"--row-size:{int(rows)}")
                cls.append("fit-rows")
            cards.append(f'<div class="{" ".join(cls)}" style="{";".join(style)}">{render_card(c, ctx)}</div>')
        secs.append(f'<div class="section" data-span="{span}" style="--column-span:{span}">'
                    f'<div class="grid">{"".join(cards)}</div></div>')
    tag = f'<div class="tag">{html.escape(label)}</div>' if label else ""
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(view.get('title', ''))} — offline preview</title><style>{CSS}</style></head>"
            f"<body>{tag}<div class='view' data-max-columns='{view.get('max_columns', 4)}' data-spans='{json.dumps(spans)}'>"
            f"<div class='wrapper'><div class='container'>{''.join(secs)}</div></div></div>"
            f"<script>{JS}</script></body></html>")


SHOOT = r"""
const {chromium} = require('playwright');
(async () => {
  const [file, out, w, h] = process.argv.slice(1);
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: +w, height: +h}, deviceScaleFactor: 2});
  await p.goto('file://' + file);
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({path: out, fullPage: true});
  const info = await p.evaluate(() => {
    // Measured in the simulated layout only: sections sharing a row (a band) and how much
    // shorter each is than the tallest beside it; button labels wider than their card (the
    // button card clips, it never ellipsises); fixed-height cards whose content overruns.
    const secs = [...document.querySelectorAll('.section')].map((s, i) => {
      const r = s.getBoundingClientRect(); return {i, top: Math.round(r.top), h: Math.round(r.height)}; });
    const rows = {}; secs.forEach(s => (rows[s.top] = rows[s.top] || []).push(s));
    const holes = Object.values(rows).filter(g => g.length > 1).map(g => ({sections: g.map(s => s.i),
      heights: g.map(s => s.h), hole: Math.max(...g.map(s => s.h)) - Math.min(...g.map(s => s.h))}))
      .filter(b => b.hole > 0);
    const clipped = [...document.querySelectorAll('.btn .bn')].filter(n =>
      n.scrollWidth > n.parentElement.clientWidth).map(n => n.textContent);
    const overflow = [...document.querySelectorAll('.card.fit-rows .ha-card')].filter(c =>
      c.scrollHeight > c.clientHeight + 1).map(c => c.textContent.trim().slice(0, 40));
    return {cols: document.body.dataset.columns, height: document.documentElement.scrollHeight,
            holes, clipped, overflow};
  });
  console.log(JSON.stringify(info));
  await b.close();
})();
"""


def shoot(html_path, out_png, size):
    node = shutil.which("node") or "/opt/node22/bin/node"
    r = subprocess.run([node, "-e", SHOOT, str(html_path), str(out_png), str(size[0]), str(size[1])],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise SystemExit(f"capture failed: {r.stderr.strip()[:400]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def side_by_side(before, after, out, captions=("Before", "After"), crop_height=None, scale=0.5):
    from PIL import Image, ImageDraw, ImageFont
    a, b = Image.open(before).convert("RGB"), Image.open(after).convert("RGB")
    if crop_height:
        a = a.crop((0, 0, a.width, min(a.height, crop_height)))
        b = b.crop((0, 0, b.width, min(b.height, crop_height)))
    if scale != 1:
        a = a.resize((int(a.width * scale), int(a.height * scale)), Image.LANCZOS)
        b = b.resize((int(b.width * scale), int(b.height * scale)), Image.LANCZOS)
    pad, head, foot = 24, 64, 56
    W = a.width + b.width + pad * 3
    H = head + max(a.height, b.height) + foot + pad
    img = Image.new("RGB", (W, H), (8, 10, 12))
    img.paste(a, (pad, head))
    img.paste(b, (pad * 2 + a.width, head))
    d = ImageDraw.Draw(img)
    font = _font(26)
    small = _font(17)
    d.text((pad, 18), captions[0], fill=(238, 242, 247), font=font)
    d.text((pad * 2 + a.width, 18), captions[1], fill=(238, 242, 247), font=font)
    d.text((pad, H - foot), "Offline preview, not a Home Assistant screenshot: layout from Home Assistant's "
           "sections-view CSS (frontend 20260826.7); card interiors approximated; fixture states, not live readings.",
           fill=(232, 163, 61), font=small)
    img.save(out, optimize=True)
    return img.size


def _font(size):
    from PIL import ImageFont
    try:
        path = subprocess.run(["fc-match", "-f", "%{file}", "Inter"], capture_output=True, text=True).stdout
        return ImageFont.truetype(path, size)
    except Exception:  # noqa: BLE001
        return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("view", nargs="?")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--dashboard", type=Path, default=ROOT / "dashboards/casaray_v3.yaml")
    ap.add_argument("--scenario", choices=["normal", "dark"], default="normal")
    ap.add_argument("--icons", type=Path)
    ap.add_argument("--label", default="Offline preview — not Home Assistant")
    ap.add_argument("--shots", action="store_true")
    ap.add_argument("--side-by-side", nargs=3, metavar=("BEFORE", "AFTER", "OUT"))
    ap.add_argument("--captions", nargs=2, default=["Before", "After"])
    ap.add_argument("--crop-height", type=int)
    ap.add_argument("--scale", type=float, default=0.5)
    a = ap.parse_args()
    if a.side_by_side:
        size = side_by_side(*a.side_by_side, captions=a.captions, crop_height=a.crop_height, scale=a.scale)
        print(f"wrote {a.side_by_side[2]} {size[0]}x{size[1]}")
        return 0
    if not a.view or not a.out:
        ap.error("a view and --out are required")
    dash = yaml.safe_load(a.dashboard.read_text(encoding="utf-8"))
    view = next((v for v in dash["views"] if v["path"] == a.view), None)
    if view is None:
        raise SystemExit(f"no view {a.view!r} in {a.dashboard}")
    states, attrs = R.scenarios()[a.scenario]
    if a.scenario == "normal":
        attrs = {**{k: dict(v) for k, v in DEMO_ATTRS.items()}, **attrs}
    names = json.loads((ROOT / "docs/live/fixture_states.json").read_text(encoding="utf-8"))["_meta"]["names"]
    a.out.mkdir(parents=True, exist_ok=True)
    out = a.out / f"{a.view}.html"
    out.write_text(page(view, states, attrs, names, Icons(a.icons), a.label), encoding="utf-8")
    print(f"wrote {out}")
    if a.shots:
        for dev, size in VIEWPORTS.items():
            png = a.out / f"{a.view}_{dev}.png"
            info = shoot(out.resolve(), png, size)
            print(f"wrote {png}  {size[0]}x{size[1]} viewport: {info['cols']} column(s), page {info['height']} px tall")
            print("  measured (simulated): band holes " + json.dumps(info["holes"], ensure_ascii=False)
                  + " | clipped labels " + json.dumps(info["clipped"], ensure_ascii=False)
                  + " | overflowing fixed-height cards " + json.dumps(info["overflow"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
