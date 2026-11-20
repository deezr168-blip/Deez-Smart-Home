"""HACS recommendation mockups for CasaRay V3 (20/11/26). DESIGN MOCKUPS ONLY.

Illustrations of what each recommended custom card would add, drawn in the
CasaRay V3 dark-glass style with labelled sample values. Not renders of the
cards and not Home Assistant screenshots. Every card shown uses only options
its own documentation lists (see HACS_RECOMMENDATIONS_2026-11-20.md).

    python3 make_mockups.py OUT_DIR icons CAMERA_SHEET_PNG
    node shoot.cjs OUT_DIR          # PNGs at deviceScaleFactor 2 (Playwright)

CAMERA_SHEET_PNG is the owner's 19/11/26 mockup sheet
(docs/mockups/2026-11-19_bilingual_2_cameras.png, on PR #26's branch); its camera
illustrations stand in for camera pictures, labelled as sample images. Icons:
Material Design Icons (Apache-2.0). Renders are not committed (../../.gitignore).
"""
import base64
import io
import re
import sys
from pathlib import Path

OUT, ICONS, SHEET = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)


def ic(name, cls="ic"):
    m = re.search(r'\sd="([^"]+)"', (ICONS / f"{name}.svg").read_text())
    return f'<svg class="{cls}" viewBox="0 0 24 24"><path d="{m.group(1)}"/></svg>'


def crop(box):
    from PIL import Image
    im = Image.open(SHEET).convert("RGB").crop(tuple(box))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


CSS = """
:root{--page:#0d1114;--card:#161b1f;--elev:#1a1f25;--line:rgba(160,190,220,.14);--t1:#eef2f7;--t2:#a9b4c3;
--amber:#e8a33d;--green:#5fd39a;--red:#f07a7a;--grey:#8a95a3;--blue:#5aa9e6}
*{box-sizing:border-box}html,body{margin:0}
body{background:radial-gradient(120% 80% at 50% -10%,rgba(70,110,160,.22),transparent 60%),#0d1114;color:var(--t1);
font-family:Inter,'IPAGothic',sans-serif;font-size:14px;line-height:1.45;min-height:100vh;overflow:hidden}
.ic{width:22px;height:22px;fill:currentColor;flex:none}
.wrap{max-width:1032px;margin:0 auto;padding:16px 32px 0}
.card{background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.02)),var(--card);border:1px solid var(--line);
border-radius:18px;padding:14px 16px;position:relative}
.row{display:flex;gap:12px;align-items:center}.col{display:flex;flex-direction:column}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:32px}.stack{display:flex;flex-direction:column;gap:8px}
h3{margin:0 0 8px;font-size:17px;font-weight:600}.sub{color:var(--t2);font-size:12px}
.big{font-size:22px;font-weight:700}.zh{font-weight:700}.en{color:var(--t2);font-size:12px}
.tag{position:absolute;top:-9px;right:12px;font-size:10.5px;font-weight:600;letter-spacing:.2px;color:#1a1206;
background:var(--amber);border-radius:999px;padding:2px 9px;z-index:5;white-space:nowrap}
.tag.native{background:#9fb3c8}
.mock{position:fixed;top:0;left:0;right:0;z-index:50;font-size:11px;color:#ffd38a;background:rgba(30,21,6,.96);
border-bottom:1px solid rgba(232,163,61,.5);padding:5px 14px;text-align:center;line-height:1.35}
body{padding-top:40px}
.header{display:flex;align-items:center;justify-content:space-between}
.header .t{font-size:19px;font-weight:700}.header .r{display:flex;gap:26px;align-items:center}
.clock{text-align:right}.clock b{font-size:20px}
.footer{position:fixed;left:50%;transform:translateX(-50%);bottom:18px;width:min(1032px,calc(100% - 64px));
display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.footer .b{background:var(--elev);border:1px solid var(--line);border-radius:16px;height:64px;display:flex;flex-direction:column;
align-items:center;justify-content:center;gap:2px;font-size:14px;box-shadow:0 6px 18px rgba(0,0,0,.45)}
.footer .b .ic{width:24px;height:24px}.footer .b.on{color:var(--amber)}
.pill{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:3px 10px;font-size:12px;
background:rgba(255,255,255,.06);border:1px solid var(--line)}
.ok{color:var(--green)}.warn{color:var(--amber)}.bad{color:var(--red)}.mute{color:var(--grey)}
"""


def page(body, label, w, extra_css=""):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}{extra_css}</style></head><body>"
            f"<div class='mock'>{label}</div>{body}</body></html>")


LABEL = ("MOCKUP · 示意圖 — not a Home Assistant screenshot · sample values · "
         "every custom-card option shown is in that card's own documentation")


def header(title_zh, title_en, extra=""):
    return (f"<div class='card header'><div><div class='t'>CasaRay｜{title_zh} <span style='font-weight:500'>{title_en}</span></div>"
            f"<div class='sub'>設計預覽 / Design preview</div></div><div class='r'>{extra}"
            f"<div class='clock'><b>07:30</b><div class='sub'>星期五 Fri · 20/11/26</div></div></div></div>")


def footer(on):
    tabs = [("home-outline", "主頁 Home"), ("bed-outline", "房間 Rooms"), ("lamp-outline", "燈光 Lighting"),
            ("video-outline", "鏡頭 Camera"), ("dots-horizontal", "更多 More")]
    return "<div class='footer'>" + "".join(
        f"<div class='b{' on' if i == on else ''}'>{ic(n)}<span>{t}</span></div>" for i, (n, t) in enumerate(tabs)) + "</div>"


# ---------------------------------------------------------------- 1 Home + kiosk mode
def m_home():
    body = f"""<div class='wrap stack' style='gap:22px'>
<div style='position:relative'><span class='tag'>Kiosk Mode · hides Home Assistant's header and sidebar</span>{header('主頁', 'Home', "<span class='row mute'>" + ic('weather-cloudy-alert') + " 無資料</span>")}</div>
<div class='grid2'>
 <div class='card'><div class='big'>早晨，今日屋企點？</div><div class='sub' style='font-size:14px'>Good morning, how's home today?</div></div>
 <div class='card'><div class='row' style='font-size:20px;font-weight:700'>{ic('weather-cloudy-alert')} 天氣 Weather</div><div><b>無資料</b> <span class='en'>No data</span></div></div>
</div>
<div class='grid2'>
 <div class='stack'><h3>房間燈光 Room lights</h3>
  <div class='card row'>{ic('lightbulb-outline')}<div><b>客廳</b> <span class='en'>Living room</span><div class='sub'>已關 Off</div></div></div>
  <div class='card row'>{ic('lightbulb-outline')}<div><b>飯廳</b> <span class='en'>Dining</span><div class='sub'>已關 Off</div></div></div>
  <div class='card row'>{ic('lightbulb-outline')}<div><b>Ray 房</b> <span class='en'>Ray room</span><div class='sub'>已關 Off</div></div></div></div>
 <div class='stack'><h3>門口鏡頭 Front door</h3>
  <div class='card' style='padding:0;height:120px;overflow:hidden'><img src='{CAM["front"]}' style='width:100%;height:100%;object-fit:cover;opacity:.9'>
   <div style='position:absolute;left:0;right:0;bottom:0;padding:8px 14px;background:rgba(0,0,0,.45)'>前門 Front door ›</div></div>
  <div class='card'><b>睇門口</b> View front door ›</div></div>
</div>
<div class='card row'>{ic('thermometer')}<div><b>爸媽房溫度</b> Parents room temperature<div class='sub'>23.6 °C</div></div></div>
</div>{footer(0)}"""
    return page(body, LABEL + "<br>Kiosk Mode: <code>kiosk_mode: {kiosk: true}</code> — the trial photos' header and sidebar are gone", 1180)


# ---------------------------------------------------------------- 2 Bubble Card pop-up (iPad)
POP_CSS = """
.dim{position:fixed;inset:0;background:rgba(5,8,10,.55);backdrop-filter:blur(3px);z-index:10}
.sheet{position:fixed;z-index:20;left:50%;transform:translateX(-50%);bottom:0;width:min(640px,100%);
background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.02)),#141a1f;border:1px solid var(--line);
border-bottom:none;border-radius:32px 32px 0 0;padding:16px 18px 26px;box-shadow:0 -16px 40px rgba(0,0,0,.5)}
.grab{width:46px;height:5px;border-radius:3px;background:rgba(255,255,255,.25);margin:0 auto 12px}
.bhead{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.bico{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(232,163,61,.18);color:var(--amber)}
.bclose{margin-left:auto;width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center}
.sl{position:relative;height:62px;border-radius:31px;background:rgba(255,255,255,.06);border:1px solid var(--line);overflow:hidden;margin-bottom:10px}
.sl .fill{position:absolute;inset:0;width:var(--p);background:linear-gradient(90deg,rgba(232,163,61,.55),rgba(232,163,61,.35))}
.sl .in{position:relative;display:flex;align-items:center;gap:12px;height:100%;padding:0 10px}
.sl .bi{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.25)}
.sl .pc{margin-left:auto;padding-right:12px;font-weight:700}
.subs{display:flex;gap:8px;flex-wrap:wrap;margin-top:4px}
.sb{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:7px 12px;background:rgba(255,255,255,.07);border:1px solid var(--line);font-size:13px}
.sb .ic{width:18px;height:18px}
"""


def bubble_sheet(narrow=False):
    return f"""<div class='dim'></div><div class='sheet' style='position:fixed'>
<span class='tag' style='right:24px'>Bubble Card · pop-up (hash #living-room)</span><div class='grab'></div>
<div class='bhead'><div class='bico'>{ic('sofa-outline')}</div><div><div style='font-size:19px;font-weight:700'>客廳 <span style='font-weight:500'>Living room</span></div>
<div class='sub'>1 盞燈已開 · 1 light on</div></div><div class='bclose'>{ic('close')}</div></div>
<div class='sl' style='--p:62%'><div class='fill'></div><div class='in'><div class='bi'>{ic('lightbulb-on')}</div>
<div><b>客廳燈</b> Living room light<div class='sub'>已開 On · 62%</div></div><div class='pc'>62%</div></div></div>
<div class='sl' style='--p:0%'><div class='fill'></div><div class='in'><div class='bi'>{ic('lightbulb-outline')}</div>
<div><b>飯廳燈</b> Dining light<div class='sub'>已關 Off</div></div><div class='pc mute'>0%</div></div></div>
<div class='subs'>
 <span class='sb'>{ic('thermometer')} 溫度 Temperature · <b class='mute'>無資料</b></span>
 <span class='sb'>{ic('motion-sensor')} 動態 Motion · <b class='mute'>無資料</b></span>
 <span class='sb'>{ic('door-closed')} 前門 Front door · <b class='ok'>已關 Closed</b></span>
</div>
<div class='sub' style='margin-top:12px'>示例數值 Sample values · the two lights' entity IDs are to be confirmed first (they are not on the instance today)</div>
</div>"""


def m_bubble_ipad():
    rooms = [("sofa-outline", "客廳", "Living room", "燈光：無資料"), ("lamp-outline", "廚房", "Kitchen", "動態：暫無動作"),
             ("lightbulb-outline", "飯廳", "Dining", "燈光：無資料"), ("bed-outline", "爸媽房", "Parents", "溫度：24°"),
             ("bed-outline", "Ray 房", "Ray room", "燈光：已關"), ("home-outline", "車房", "Garage", "雪櫃：2 W")]
    cells = "".join(f"<div class='card row'>{ic(i)}<div><b>{z}</b><div class='en'>{e}</div></div><div style='margin-left:auto;text-align:right'><b>{s}</b></div>{ic('chevron-right')}</div>"
                    for i, z, e, s in rooms)
    body = f"""<div class='wrap stack' style='gap:22px'>{header('房間', 'Rooms')}
<h3 style='margin:0'>房間一覽 All rooms</h3><div class='grid2' style='gap:10px 32px'>{cells}</div></div>{footer(1)}{bubble_sheet()}"""
    return page(body, LABEL + "<br>Tap a room → its pop-up slides up over the page; nothing navigates away", 1180, POP_CSS)


def m_bubble_phone():
    body = f"""<div style='padding:14px'>{header('房間', 'Rooms')}</div>{bubble_sheet(True)}"""
    css = POP_CSS + ".sheet{width:100%;border-radius:28px 28px 0 0} .header .r{gap:10px} .header .t{font-size:16px}"
    return page(body, "MOCKUP · 示意圖 — not a Home Assistant screenshot · sample values", 390, css)


# ---------------------------------------------------------------- 3 Advanced Camera Card
ACC_CSS = """
.acc{padding:0;overflow:hidden;height:572px;display:flex;flex-direction:column}
.accbar{display:flex;align-items:center;gap:14px;padding:8px 14px;background:rgba(0,0,0,.35);border-bottom:1px solid var(--line)}
.accbar .ic{width:20px;height:20px}
.accgrid{flex:1;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;gap:4px;padding:4px;background:#05080a}
.cell{position:relative;overflow:hidden;border-radius:6px;background:#0b0f12}
.cell img{width:100%;height:100%;object-fit:cover}
.cell .nm{position:absolute;left:8px;bottom:8px;font-size:12.5px;padding:3px 8px;border-radius:6px;background:rgba(0,0,0,.55)}
.cell .live{position:absolute;right:8px;top:8px;font-size:10.5px;font-weight:700;padding:2px 7px;border-radius:5px;background:rgba(240,122,122,.9);color:#fff}
.cell.sel{outline:2px solid var(--amber);outline-offset:-2px}
.cell.err{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;color:var(--t2);text-align:center;padding:10px}
.cell.err .ic{width:34px;height:34px;color:var(--grey)}
.sample{position:absolute;right:8px;bottom:8px;font-size:10px;color:#ffd38a;background:rgba(40,28,8,.8);border-radius:4px;padding:1px 5px}
"""


def m_cameras():
    cams = [("front", True), ("north", False), (None, False), ("south", False), ("stock", False), ("pet", False)]
    cells = ""
    for k, sel in cams:
        if k is None:
            cells += (f"<div class='cell err'>{ic('video-off-outline')}<div><b>東牆 East wall</b></div>"
                      "<div style='font-size:12px'>鏡頭離線 Camera unavailable</div></div>")
        else:
            cells += (f"<div class='cell{' sel' if sel else ''}'><img src='{CAM[k]}'>"
                      f"<span class='sample'>示例圖片 Sample image</span></div>")
    body = f"""<div class='wrap stack' style='gap:22px'>{header('鏡頭', 'Cameras')}
<div style='position:relative'><span class='tag'>Advanced Camera Card · live, display: mode grid, grid_columns 3</span>
<div class='card acc'>
<div class='accbar'><span class='row'>{ic('cctv')}</span><span class='row'>{ic('video-outline')}</span>
<span style='margin-left:auto' class='row'>{ic('view-grid-outline')}{ic('fullscreen')}</span></div>
<div class='accgrid'>{cells}</div>
<div class='sbar'>前門 Front door</div></div></div></div>{footer(3)}"""
    return page(body, LABEL + "<br>Menu: cameras · live · display mode (grid ↔ single) · fullscreen. The status bar names the selected camera; pinch to zoom", 1180,
                ACC_CSS + ".sbar{padding:8px 14px;background:rgba(0,0,0,.45);border-top:1px solid var(--line);font-size:13px}")


# ---------------------------------------------------------------- 4 Power Flow Card Plus + ApexCharts
PF_CSS = """
.pf{height:300px;position:relative}
.circ{position:absolute;width:96px;height:96px;border-radius:50%;border:3px solid;display:flex;flex-direction:column;
align-items:center;justify-content:center;font-size:13px;background:rgba(0,0,0,.15)}
.circ b{font-size:15px}.lbl{position:absolute;font-size:12px;color:var(--t2);text-align:center;width:120px}
svg.lines{position:absolute;inset:0;width:100%;height:100%}
.chart{height:300px;position:relative}
.legend{display:flex;gap:16px;font-size:12px;color:var(--t2)}.sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px}
.caveat{border-left:3px solid var(--amber);padding:6px 10px;background:rgba(232,163,61,.08);border-radius:6px;font-size:12px}
"""


def m_energy():
    # sample evening values: solar 0.4 kW, grid import 1.1 kW, home 1.5 kW (no export: the computed home is right)
    pf = f"""<div class='card'><span class='tag'>Power Flow Card Plus</span><h3>而家用電 Power now</h3><div class='pf'>
<svg class='lines' viewBox='0 0 460 300'>
 <path d='M230 98 Q 300 150 360 180' stroke='#e8a33d' stroke-width='2' fill='none' stroke-dasharray='4 6'/>
 <path d='M126 200 L 312 200' stroke='#5aa9e6' stroke-width='2' fill='none' stroke-dasharray='4 6'/>
 <circle cx='300' cy='148' r='4' fill='#e8a33d'/><circle cx='220' cy='200' r='4' fill='#5aa9e6'/></svg>
<div class='lbl' style='left:170px;top:2px'>太陽能 Solar</div>
<div class='circ' style='left:182px;top:20px;border-color:#e8a33d'>{ic('solar-power-variant')}<b>0.4 kW</b></div>
<div class='lbl' style='left:28px;top:132px'>電網 Grid import</div>
<div class='circ' style='left:40px;top:152px;border-color:#5aa9e6'>{ic('transmission-tower')}<b>1.1 kW</b></div>
<div class='lbl' style='left:322px;top:132px'>屋企 Home</div>
<div class='circ' style='left:334px;top:152px;border-color:#5fd39a'>{ic('home-lightning-bolt-outline')}<b>1.5 kW</b></div>
</div><div class='caveat'>屋企用電 = 太陽能 + 電網入電。冇輸出感應器，所以賣電時呢個數會偏高。<br>
<span class='sub'>Home = solar + grid import. With no export sensor this reads high while the panels export.</span></div></div>"""
    # ApexCharts area chart: today, solar vs grid import (sample curve)
    import math
    xs = list(range(0, 25))
    solar = [max(0, 3.6 * math.sin(math.pi * (h - 6.5) / 12)) if 6.5 < h < 18.5 else 0 for h in xs]
    grid = [0.6 + (0.9 if h in (7, 8, 18, 19, 20) else 0) - min(0.55, solar[h] * .3) for h in xs]
    W, H, X0, Y0 = 440, 220, 34, 240

    def path(v, close=True):
        pts = [(X0 + i * (W - X0) / 24, Y0 - val / 4 * (H - 20)) for i, val in enumerate(v)]
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        return d + (f" L{pts[-1][0]:.1f} {Y0} L{X0} {Y0} Z" if close else "")
    grid_lines = "".join(f"<line x1='{X0}' x2='{W}' y1='{Y0 - k/4*(H-20):.0f}' y2='{Y0 - k/4*(H-20):.0f}' stroke='rgba(160,190,220,.12)'/>"
                         f"<text x='4' y='{Y0 - k/4*(H-20)+4:.0f}' fill='#a9b4c3' font-size='10'>{k} kW</text>" for k in range(5))
    ticks = "".join(f"<text x='{X0 + h*(W-X0)/24 - 8:.0f}' y='{Y0+16}' fill='#a9b4c3' font-size='10'>{h:02d}:00</text>" for h in (0, 6, 12, 18))
    chart = f"""<div class='card'><span class='tag'>ApexCharts Card · area series, span: 1 day</span><h3>今日 Today</h3>
<div class='legend'><span><i class='sw' style='background:#e8a33d'></i>太陽能 Solar (Primo)</span><span><i class='sw' style='background:#5aa9e6'></i>電網入電 Grid import (Powerpal)</span></div>
<svg viewBox='0 0 460 260' style='width:100%;height:300px'>{grid_lines}{ticks}
<path d='{path(solar)}' fill='rgba(232,163,61,.28)' stroke='#e8a33d' stroke-width='2'/>
<path d='{path(grid)}' fill='rgba(90,169,230,.22)' stroke='#5aa9e6' stroke-width='2'/>
<line x1='{X0 + 7.5*(W-X0)/24:.0f}' x2='{X0 + 7.5*(W-X0)/24:.0f}' y1='20' y2='{Y0}' stroke='rgba(255,255,255,.35)' stroke-dasharray='3 4'/>
</svg><div class='sub'>太陽能今日 Solar today 14.2 kWh · 電網入電 Grid import 9.8 kWh</div></div>"""
    body = f"""<div class='wrap stack' style='gap:22px'>{header('用電', 'Energy')}<div class='grid2'>{pf}{chart}</div></div>{footer(4)}"""
    return page(body, LABEL + "<br>Entities: sensor.primo_5_0_1_1_ac_power (solar), sensor.powerpal_gateway_powerpal_power (grid import) — in the 05/09 export; not visible to the read-only connector", 1180, PF_CSS)


# ---------------------------------------------------------------- 5 auto-entities on House health
def m_health():
    # names as the read-only connector read them on 19-20/11/26 (state unavailable)
    groups = [("lightbulb-group-outline", "燈 Lights", ["Living Room Inner Left", "Living Room Inner Right", "Living Room Outter Left",
                                                       "Living Room Outter Right", "Dining Light Left", "Dining Light Right", "Kogan Tv"]),
              ("power-plug-off-outline", "開關 Switches", ["Channel 1 Socket · Living Room", "Channel 2 Socket · Living Room",
                                                          "Channel 3 Socket · Living Room", "Channel 4 Socket · Living Room",
                                                          "Channel 5 Socket · Living Room", "Tapo C425 - North Wall"]),
              ("alert-circle-outline", "感應器 Sensors", ["Freezer P110M Overheated · Garage"])]
    col = []
    for i, t, names in groups:
        rows = "".join(f"<div class='row' style='padding:7px 0;border-top:1px solid var(--line)'>{ic(i)}<span>{n}</span>"
                       f"<span class='pill mute' style='margin-left:auto'>離線 Unavailable</span></div>" for n in names)
        col.append(f"<div class='card'><span class='tag'>auto-entities · domain + state: unavailable</span><h3 class='row'>{ic(i)} {t} <span class='sub' style='margin-left:auto'>{len(names)}</span></h3>{rows}</div>")
    body = f"""<div class='wrap stack' style='gap:22px'>{header('屋企狀況', 'House health')}
<div class='card row' style='gap:18px'><span class='tag native'>native markdown · template count</span>
{ic('heart-pulse')}<div><div class='big'>14 個實體冇回應 <span style='font-weight:500;font-size:18px'>14 entities not answering</span></div>
<div class='sub'>自動列出，唔使人手維護清單 · Listed automatically — no hand-kept list to go stale</div></div></div>
<div class='grid2' style='align-items:start'><div class='stack' style='gap:14px'>{col[0]}</div><div class='stack' style='gap:14px'>{col[1]}{col[2]}</div></div>
</div>{footer(4)}"""
    return page(body, LABEL + "<br>Names are the read-only connector's, 19–20/11/26; a missing entity ID (the six to confirm) is not an entity and cannot be listed", 1180)


# ---------------------------------------------------------------- 6 WallPanel screensaver
WP_CSS = """
.bg{position:fixed;inset:0;background:
radial-gradient(60% 50% at 70% 30%,rgba(90,140,200,.35),transparent 70%),
radial-gradient(50% 40% at 20% 80%,rgba(232,163,61,.18),transparent 70%),
linear-gradient(180deg,#0b1626 0%,#14243a 45%,#2a2a3a 75%,#3a2a24 100%)}
.ph{position:fixed;left:50%;top:44%;transform:translate(-50%,-50%);color:rgba(255,255,255,.35);font-size:14px;text-align:center}
.info{position:fixed;left:48px;bottom:48px;display:flex;gap:14px;align-items:flex-end}
.ibox{background:rgba(10,14,18,.55);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:14px 20px}
.tm{font-size:84px;font-weight:300;line-height:1;letter-spacing:-2px}
"""


def m_wallpanel():
    body = f"""<div class='bg'></div><div class='ph'>你嘅相片 · Your photos<br><span style='font-size:12px'>(Home Assistant media folder, rotating)</span></div>
<div class='info'><div class='ibox' style='position:relative'><span class='tag' style='top:-12px'>WallPanel · screensaver info box (cards)</span>
<div class='tm'>07:30</div><div style='font-size:18px;margin-top:6px'>星期五 Fri · 20/11/26</div></div>
<div class='ibox'><div class='row'>{ic('thermometer')}<div><b>爸媽房</b> Parents room<div class='big'>23.6 °C</div></div></div></div>
<div class='ibox'><div class='row'>{ic('door-closed')}<div><b>前門</b> Front door<div class='big ok'>已關 Closed</div></div></div></div></div>"""
    return page(body, LABEL + "<br>After 2 min idle (idle_time) the wall iPad shows photos with an info box; a touch returns to the dashboard", 1180, WP_CSS)


CAM = {"front": crop([156, 80, 350, 154]), "north": crop([505, 80, 700, 154]), "south": crop([505, 202, 700, 276]),
       "stock": crop([156, 325, 350, 399]), "pet": crop([505, 325, 700, 399])}

PAGES = {"1_home_kiosk_mode": (m_home, 1180, 820), "2_rooms_bubble_popup_ipad": (m_bubble_ipad, 1180, 820),
         "3_rooms_bubble_popup_iphone": (m_bubble_phone, 390, 844), "4_cameras_advanced_camera_card": (m_cameras, 1180, 820),
         "5_energy_power_flow_apexcharts": (m_energy, 1180, 820), "6_house_health_auto_entities": (m_health, 1180, 820),
         "7_wallpanel_screensaver": (m_wallpanel, 1180, 820)}
for name, (fn, w, h) in PAGES.items():
    (OUT / f"{name}.html").write_text(fn(), encoding="utf-8")
    (OUT / f"{name}.size").write_text(f"{w} {h}")
print("\n".join(PAGES))
