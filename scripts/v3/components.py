"""CasaRay V3 reusable components.  DEVELOPMENT ONLY — NOT DEPLOYED.

Every function returns plain Lovelace card or section dicts built only from
native card types (heading, markdown, tile, button, picture-entity,
weather-forecast, todo-list, history-graph). Strings come from the locale catalogue through
`ctx`, so a component never holds copy of its own.

Honesty rules, enforced here and tested in tests/v3:
  * a value that is unavailable / unknown / missing renders "No data" (or
    "Offline" / "State unknown"), never a sentinel number;
  * a count states what ANSWERED ("2 of 3 reporting"), not the list length;
  * a reassuring line ("nothing needs attention") is only written when every
    check behind it answered, otherwise the not-reporting count is stated;
  * HVAC is read-only (V3-008), camera privacy / detection switches and
    bulb-power wall switches are read-only (approval boundary).
"""
from __future__ import annotations

BAD = "['unavailable','unknown','none','']"


def jstr(s: str) -> str:
    """A Jinja string literal."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ---------------------------------------------------------------- primitives

def grid(columns, rows="auto"):
    return {"columns": columns, "rows": rows}


def heading(ctx, key, style="title"):
    return {"type": "heading", "heading": ctx.t(key), "heading_style": style,
            "grid_options": grid(12)}


def nav_button(ctx, label_key, icon, target, columns=3, rows=1, show_name=True, current=False):
    btn = {"type": "button", "name": ctx.t(label_key), "icon": icon,
           "show_name": show_name, "show_icon": True,
           "tap_action": {"action": "none"} if current else
           {"action": "navigate", "navigation_path": ctx.link(target)},
           "grid_options": grid(columns, rows)}
    return btn


def action_button(ctx, label_key, icon, action, target, data=None, columns=3, rows=2):
    tap = {"action": "perform-action", "perform_action": action,
           "target": {"entity_id": target}}
    if data:
        tap["data"] = data
    ctx.use(target)
    return {"type": "button", "name": ctx.t(label_key), "icon": icon,
            "show_name": True, "show_icon": True, "tap_action": tap,
            "hold_action": {"action": "none"}, "grid_options": grid(columns, rows)}


def markdown(content, columns=12, rows="auto"):
    # Every template starts with `{%-`-trimmed preambles or literal text, so
    # CommonMark never sees four leading spaces (V2 rule, tested).
    return {"type": "markdown", "content": content.strip("\n"),
            "grid_options": grid(columns, rows)}


def note(ctx, key, columns=12):
    return markdown("<small>" + ctx.t(key) + "</small>", columns)


# ---------------------------------------------------------------- tiles

def light_tile(ctx, entity, name=None, columns=6, brightness=True):
    ctx.use(entity)
    t = {"type": "tile", "entity": entity, "vertical": False,
         "grid_options": grid(columns, 2 if brightness else 1)}
    if name:
        t["name"] = name
    if brightness:
        t["features"] = [{"type": "light-brightness"}]
        t["features_position"] = "bottom"
    return t


def readonly_tile(ctx, entity, name=None, columns=6, nav=None):
    """State shown, nothing toggled: neither tap nor icon tap can act."""
    ctx.use(entity)
    t = {"type": "tile", "entity": entity,
         "tap_action": {"action": "navigate", "navigation_path": ctx.link(nav)} if nav
         else {"action": "none"},
         "icon_tap_action": {"action": "none"},
         "hold_action": {"action": "none"},
         "grid_options": grid(columns)}
    if name:
        t["name"] = name
    return t


def sensor_tile(ctx, entity, name=None, columns=6, nav=None):
    return readonly_tile(ctx, entity, name, columns, nav)


def person_tile(ctx, entity, nav="people", columns=4):
    t = readonly_tile(ctx, entity, None, columns, nav)
    t["vertical"] = True
    t["grid_options"] = grid(columns, 2)
    return t


# ---------------------------------------------------------------- chrome

RAIL = [  # (view path, label key, icon) — six glyphs, 2 columns each = 12
    ("home", "nav.home", "mdi:home-variant-outline"),
    ("lighting", "nav.lighting", "mdi:lightbulb-group-outline"),
    ("climate", "nav.climate", "mdi:thermometer"),
    ("cameras", "nav.cameras", "mdi:cctv"),
    ("energy", "nav.energy", "mdi:lightning-bolt-outline"),
    ("security", "nav.security", "mdi:shield-home-outline"),
]


def topbar(ctx, view_path, title_key):
    """Wordmark/title + clock, then the in-page rail (kiosk hides HA chrome).

    Home and the rail are on every V3 view; the current destination is marked
    by showing its name and making it inert. History-back has no native
    Lovelace action, so Back on a top-level view IS Home (documented)."""
    title = ctx.t("app.name") if view_path == "home" else ctx.t(title_key)
    wordmark = markdown(
        "## " + title + "\n<small>" + ctx.t("app.dev_banner") + "</small>", 6)
    clock = markdown(
        "## {{ now().strftime('%H:%M') }}\n{{ now().strftime('%d/%m/%y') }}", 6)
    cards = [wordmark, clock]
    for path, key, icon in RAIL:
        cur = path == view_path
        cards.append(nav_button(ctx, key, icon, path, columns=2, rows=1,
                                show_name=cur, current=cur))
    return {"type": "grid", "column_span": 2, "cards": cards}


def more_boards(ctx, items, classic_of=None):
    """Named index of every board, four across (12 = 4 x 3, no reflow)."""
    cards = [heading(ctx, "h.more")]
    for path, key, icon in items:
        cards.append(nav_button(ctx, key, icon, path, columns=3, rows=1))
    if classic_of:
        cards.append(nav_button(ctx, "nav.classic", "mdi:history", "v2-" + classic_of,
                                columns=3, rows=1))
    # pad to a multiple of four with nothing: the gate checks the sum instead
    return {"type": "grid", "column_span": 2, "cards": cards}


# ---------------------------------------------------------------- templates

def _count(entities, on_states):
    ids = "[" + ",".join("'" + e + "'" for e in entities) + "]"
    ons = "[" + ",".join("'" + s + "'" for s in on_states) + "]"
    return (
        "{%- set ns = namespace(ok=0, on=0) -%}"
        "{%- for e in " + ids + " -%}"
        "{%- set s = states(e) -%}"
        "{%- if s not in " + BAD + " -%}{%- set ns.ok = ns.ok + 1 -%}"
        "{%- if s in " + ons + " -%}{%- set ns.on = ns.on + 1 -%}{%- endif -%}"
        "{%- endif -%}{%- endfor -%}"
    )


def value_expr(ctx, entity, digits=1, unit=True):
    """Jinja expression: the reading with its own unit, or "No data"."""
    ctx.use(entity)
    ua = "state_attr('" + entity + "','unit_of_measurement')"
    u = (" ~ ((' ' ~ " + ua + ") if " + ua + " else '')") if unit else ""
    rnd = "| round(0) | int" if digits == 0 else "| round(" + str(digits) + ")"
    return ("((states('" + entity + "') | float) " + rnd
            + u + ") if states('" + entity + "') | is_number else "
            + jstr(ctx.t("s.no_data")))


def chip_count(ctx, label_key, entities, on_states):
    ctx.use(entities)
    total = len(entities)
    return (_count(entities, on_states)
            + "{%- if ns.ok == 0 -%}" + ctx.t(label_key) + " **" + ctx.t("s.no_data") + "**"
            + "{%- else -%}" + ctx.t(label_key) + " **{{ ns.on }}**"
            + "{%- if ns.ok < " + str(total) + " %} <small>"
            + "{{ " + ctx.jt("chip.reporting", n="ns.ok", m=str(total)) + " }}</small>{% endif -%}"
            + "{%- endif -%}")


def chip_value(ctx, label_key, entity, digits=0):
    return ctx.t(label_key) + " **{{ " + value_expr(ctx, entity, digits) + " }}**"


def chips(ctx, parts):
    """One full-width markdown strip; parts joined with ' · '."""
    # The separator is an expression, not literal text: each part's `-%}`
    # trims would otherwise eat the spaces around a literal " · ".
    return markdown("{{ ' · ' }}".join(parts))


# ---------------------------------------------------------------- attention

def attention(ctx, checks):
    """Needs attention, honestly.

    checks: list of dicts {entity, when: [states] | 'battery<N', key, name_key?}
    A check whose entity does not answer counts as not reporting, never as
    clear. The all-clear line is only written when every check answered."""
    ents = [c["entity"] for c in checks]
    ctx.use(ents)
    lines = ["{%- set ns = namespace(ok=0, dark=0, hits=[]) -%}"]
    for c in checks:
        e = c["entity"]
        name = ctx.t(c["name_key"]) if c.get("name_key") else ""
        msg_key = c["key"]
        lines.append("{%- set s = states('" + e + "') -%}")
        when = c["when"]
        if when == "offline":
            # The question is "is it offline?": unavailable answers it (a hit);
            # unknown does not answer it (not reporting).
            lines.append("{%- if s == 'unavailable' -%}{%- set ns.ok = ns.ok + 1 -%}"
                         "{%- set ns.hits = ns.hits + [" + ctx.jt(msg_key, name=jstr(name)) + "] -%}"
                         "{%- elif s in " + BAD + " -%}{%- set ns.dark = ns.dark + 1 -%}"
                         "{%- else -%}{%- set ns.ok = ns.ok + 1 -%}{%- endif -%}")
            continue
        lines.append("{%- if s in " + BAD + " -%}{%- set ns.dark = ns.dark + 1 -%}{%- else -%}"
                     "{%- set ns.ok = ns.ok + 1 -%}")
        if isinstance(when, str) and when.startswith("battery<"):
            lim = when.split("<")[1]
            lines.append("{%- if s | is_number and (s | float) < " + lim + " -%}"
                         "{%- set ns.hits = ns.hits + [" +
                         ctx.jt(msg_key, name=jstr(name), v="(s | float) | round(0) | int") +
                         "] -%}{%- endif -%}")
        else:
            st = "[" + ",".join("'" + w + "'" for w in when) + "]"
            lines.append("{%- if s in " + st + " -%}{%- set ns.hits = ns.hits + [" +
                         ctx.jt(msg_key, name=jstr(name)) + "] -%}{%- endif -%}")
        lines.append("{%- endif -%}")
    total = len(checks)
    lines.append(
        "{%- if ns.hits | count > 0 -%}"
        "{%- for h in ns.hits %}\n- **{{ h }}**{% endfor %}"
        "{%- if ns.dark > 0 %}\n\n<small>{{ " + ctx.jt("s.not_reporting", n="ns.dark") + " }}</small>{% endif -%}"
        "{%- elif ns.ok == 0 -%}" + ctx.t("att.all_dark") +
        "{%- elif ns.dark > 0 -%}{{ " + ctx.jt("att.clear_partial", n="ns.ok", m="ns.dark") + " }}" +
        "{%- else -%}{{ " + ctx.jt("att.all_clear", n=str(total)) + " }}" +
        "{%- endif -%}")
    return markdown("".join(lines))


# ---------------------------------------------------------------- climate

AC_MODES = ["off", "cool", "heat", "fan_only", "dry", "auto", "heat_cool"]


def ac_mode_expr(ctx, entity):
    """Jinja expression naming the reported mode; an unnamed mode is shown raw."""
    m = "{" + ",".join("'" + k + "':" + jstr(ctx.t("ac.mode_" + k)) for k in AC_MODES) + "}"
    return "(" + m + ").get(states('" + entity + "'), states('" + entity + "'))"


def ac_summary(ctx, entity, nav=None, columns=12):
    """Read-only air-con card (V3-008 R1/R7): mode as reported, room and
    target from the entity's own attributes, "No data" otherwise."""
    ctx.use(entity)
    nd = jstr(ctx.t("s.no_data"))

    def temp(attr):
        v = "state_attr('" + entity + "','" + attr + "')"
        return ("{{ ((" + v + " | float) | round(1) ~ '°') if " + v + " is number or ("
                + v + " | is_number) else " + nd + " }}")
    body = ("{%- set s = states('" + entity + "') -%}"
            "{%- if s == 'unavailable' -%}**" + ctx.t("s.offline") + "** · " + ctx.t("s.no_data")
            + "{%- elif s in ['unknown','none',''] -%}**" + ctx.t("s.state_unknown") + "** · " + ctx.t("s.no_data")
            + "{%- else -%}**{{ " + ctx.jt("ac.current", mode=ac_mode_expr(ctx, entity)) + " }}**\n\n"
            + ctx.t("ac.room") + " " + temp("current_temperature") + " · "
            + ctx.t("ac.target") + " " + temp("temperature")
            + "{%- endif -%}")
    card = markdown(body, columns)
    if nav:
        card["tap_action"] = {"action": "navigate", "navigation_path": ctx.link(nav)}
    return card


# ---------------------------------------------------------------- cameras

def camera_state_expr(ctx, entity):
    ctx.use(entity)
    return ("(" + jstr(ctx.t("s.offline")) + " if states('" + entity + "') == 'unavailable' else ("
            + jstr(ctx.t("s.state_unknown")) + " if states('" + entity + "') in ['unknown','none',''] else "
            + jstr(ctx.t("s.online")) + "))")


def camera_summary(ctx, cams):
    ents = [c["entity"] for c in cams]
    ctx.use(ents)
    ids = "[" + ",".join("'" + e + "'" for e in ents) + "]"
    head = ("{%- set ns = namespace(a=0, b=0, c=0) -%}{%- for e in " + ids + " -%}"
            "{%- set s = states(e) -%}{%- if s == 'unavailable' -%}{%- set ns.b = ns.b + 1 -%}"
            "{%- elif s in ['unknown','none',''] -%}{%- set ns.c = ns.c + 1 -%}"
            "{%- else -%}{%- set ns.a = ns.a + 1 -%}{%- endif -%}{%- endfor -%}")
    rows = "".join("\n- " + ctx.t(c["name_key"]) + " — **{{ " + camera_state_expr(ctx, c["entity"]) + " }}**"
                   for c in cams)
    return markdown(head + "**{{ " + ctx.jt("cam.summary", a="ns.a", b="ns.b", c="ns.c") + " }}**\n" + rows)


def camera_card(ctx, entity, name_key, subview, columns=6, rows=4):
    ctx.use(entity)
    return {"type": "picture-entity", "entity": entity, "name": ctx.t(name_key),
            "camera_view": "auto", "show_state": False, "show_name": True,
            "tap_action": {"action": "navigate", "navigation_path": ctx.link(subview)},
            "hold_action": {"action": "none"},
            "grid_options": grid(columns, rows)}


def chip_cameras(ctx, ents):
    ctx.use(ents)
    return chip_count(ctx, "chip.cameras", ents, ["idle", "streaming", "recording"])


# ---------------------------------------------------------------- misc

def weather(ctx, entity, forecast=False, columns=12):
    ctx.use(entity)
    c = {"type": "weather-forecast", "entity": entity, "show_current": True,
         "show_forecast": forecast, "grid_options": grid(columns)}
    if forecast:
        c["forecast_type"] = "daily"
    return c


def history(ctx, entities, hours=24, rows=4):
    """Native history-graph; HA itself draws gaps where an entity was dark."""
    ctx.use(entities)
    return {"type": "history-graph", "entities": [{"entity": e} for e in entities],
            "hours_to_show": hours, "grid_options": grid(12, rows)}


def todo(ctx, entity, rows=6):
    ctx.use(entity)
    return {"type": "todo-list", "entity": entity, "grid_options": grid(12, rows)}


def scene_buttons(ctx, scenes, prefix):
    """Scene buttons labelled from the states export's own friendly names."""
    out = []
    for sid in scenes:
        name = ctx.friendly(sid)
        if name.startswith(prefix):
            name = name[len(prefix):].strip()
        ctx.use(sid)
        out.append({"type": "button", "name": name, "icon": "mdi:palette-outline",
                    "show_name": True, "show_icon": True,
                    "tap_action": {"action": "perform-action", "perform_action": "scene.turn_on",
                                   "target": {"entity_id": sid}},
                    "hold_action": {"action": "none"}, "grid_options": grid(3, 1)})
    return out
