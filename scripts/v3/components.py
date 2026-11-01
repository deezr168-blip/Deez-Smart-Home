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


# Domains whose more-info dialog only shows state, history and attributes.
READ_ONLY_DOMAINS = {"sensor", "binary_sensor", "weather", "sun", "person", "device_tracker", "zone"}


def sensor_tile(ctx, entity, name=None, columns=6, nav=None):
    """A reading. Without `nav`, a tap opens its details (history), as a V2
    tile does; only for read-only domains, whose dialog has no control."""
    t = readonly_tile(ctx, entity, name, columns, nav)
    if not nav and entity.split(".")[0] in READ_ONLY_DOMAINS:
        t["tap_action"] = {"action": "more-info"}
    return t


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

    checks: list of dicts {entity, when: [states] | 'battery<N' | 'offline' |
    'count>0', key, name_key?, requires?}
    A check whose entity does not answer counts as not reporting, never as
    clear. The all-clear line is only written when every check answered.

    'count>0' is for a summary count sensor (e.g. unpaid bills): above zero
    is a hit; zero is only an answer when every entity in `requires` (the
    inputs it summarises) answers too, because a count whose inputs are dark
    reads 0 without having measured anything (root rule: a summary sensor
    whose inputs are down is a sentinel)."""
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
        if when == "count>0":
            req = c.get("requires", [])
            ctx.use(req)
            rids = "[" + ",".join("'" + r + "'" for r in req) + "]"
            lines.append("{%- set rq = namespace(dark=0) -%}{%- for r in " + rids + " -%}"
                         "{%- if states(r) in " + BAD + " -%}{%- set rq.dark = rq.dark + 1 -%}{%- endif -%}"
                         "{%- endfor -%}"
                         "{%- if s | is_number and (s | float) > 0 -%}{%- set ns.ok = ns.ok + 1 -%}"
                         "{%- set ns.hits = ns.hits + [" +
                         ctx.jt(msg_key, name=jstr(name), v="(s | float) | round(0) | int") + "] -%}"
                         "{%- elif s | is_number and rq.dark == 0 -%}{%- set ns.ok = ns.ok + 1 -%}"
                         "{%- else -%}{%- set ns.dark = ns.dark + 1 -%}{%- endif -%}")
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


def media(ctx, entity, columns=12):
    """Native media-control card, as V2 uses it (its own play / volume controls)."""
    ctx.use(entity)
    return {"type": "media-control", "entity": entity, "grid_options": grid(columns)}


def fmt(ctx, key, **parts):
    """A localised string with {placeholders} filled at build time (static names)."""
    s = ctx.t(key)
    for k, v in parts.items():
        s = s.replace("{" + k + "}", str(v))
    return s


# ---------------------------------------------------------------- state in words

def word_expr(ctx, entity, words, unavailable="s.offline"):
    """Jinja expression: the state in words. `words` maps states to string keys;
    unavailable -> Offline (or `unavailable`), unknown/none/'' -> State unknown,
    any other state is shown raw rather than guessed."""
    ctx.use(entity)
    m = "{" + ",".join(jstr(k) + ":" + jstr(ctx.t(v)) for k, v in words.items()) + "}"
    s = "states('" + entity + "')"
    return ("(" + jstr(ctx.t(unavailable)) + " if " + s + " == 'unavailable' else ("
            + jstr(ctx.t("s.state_unknown")) + " if " + s + " in ['unknown','none',''] else "
            + "(" + m + ").get(" + s + ", " + s + ")))")


def chip_state(ctx, label_key, entity, words, unavailable="s.offline"):
    return ctx.t(label_key) + " **{{ " + word_expr(ctx, entity, words, unavailable) + " }}**"


# ---------------------------------------------------------------- connectivity

def connectivity(ctx, devices, strip=" Cloud connection"):
    """Per-device connectivity, honestly: 'on' is online, 'off' is offline (an
    answer), anything else is not reporting. Names come from the export's own
    friendly names (device names stay Latin); a signal reading is added only
    when it is a number. The summary counts what answered."""
    ents = [d["entity"] for d in devices]
    ctx.use(ents)
    ids = "[" + ",".join("'" + e + "'" for e in ents) + "]"
    head = ("{%- set ns = namespace(a=0, b=0, c=0) -%}{%- for e in " + ids + " -%}"
            "{%- set s = states(e) -%}{%- if s == 'on' -%}{%- set ns.a = ns.a + 1 -%}"
            "{%- elif s == 'off' -%}{%- set ns.b = ns.b + 1 -%}"
            "{%- else -%}{%- set ns.c = ns.c + 1 -%}{%- endif -%}{%- endfor -%}")
    # No right-trim on the closing tag: the newlines before the list must survive.
    summary = ("{%- if ns.a + ns.b == 0 -%}**" + ctx.t("net.none_reporting") + "**"
               "{%- else -%}**{{ " + ctx.jt("net.summary", a="ns.a", b="ns.b", c="ns.c") + " }}**{%- endif %}")
    rows = []
    for d in devices:
        e = d["entity"]
        name = ctx.friendly(e)
        if name.endswith(strip):
            name = name[: -len(strip)]
        st = ("(" + jstr(ctx.t("s.online")) + " if states('" + e + "') == 'on' else ("
              + jstr(ctx.t("s.offline")) + " if states('" + e + "') == 'off' else "
              + jstr(ctx.t("s.not_reporting_one")) + "))")
        row = "- " + name + " — **{{ " + st + " }}**"
        sig = d.get("signal")
        if sig:
            ctx.use(sig)
            # Expression only (no {% %} tags), so no trim can swallow the line break.
            row += ("{{ (' · " + ctx.t("net.signal") + " ' ~ ((states('" + sig + "') | float) | round(0) | int))"
                    " if states('" + sig + "') | is_number else '' }}")
        rows.append(row)
    return markdown(head + summary + "\n\n" + "\n".join(rows))


def reporting_groups(ctx, groups, note_key=None):
    """'Cameras 4 of 6 reporting' per group: reporting means any state other
    than unavailable / unknown. A group where nothing answers says No data."""
    pre, lines = [], []
    for i, g in enumerate(groups):
        ents = g["entities"]
        ctx.use(ents)
        ids = "[" + ",".join("'" + e + "'" for e in ents) + "]"
        v = f"g{i}"
        pre.append("{%- set " + v + " = namespace(u=0) -%}{%- for e in " + ids + " -%}"
                   "{%- if states(e) not in " + BAD + " -%}{%- set " + v + ".u = " + v + ".u + 1 -%}"
                   "{%- endif -%}{%- endfor -%}")
        lines.append("- " + ctx.t(g["key"]) + " **{{ " + jstr(ctx.t("s.no_data")) + " if " + v + ".u == 0 else ("
                     + ctx.jt("chip.reporting", n=v + ".u", m=str(len(ents))) + ") }}**")
    body = "".join(pre) + "\n".join(lines)
    if note_key:
        body += "\n\n<small>" + ctx.t(note_key) + "</small>"
    return markdown(body)


# ---------------------------------------------------------------- V2 controls kept

# Home Assistant's tile card: an unset icon_tap_action toggles these domains and
# does nothing for every other one (frontend tile-card-helpers.ts,
# getEntityDefaultTileIconAction, read 01/11/26). An unset tap_action opens
# more-info. control_tile writes those effective actions out explicitly.
TILE_TOGGLE_DOMAINS = {"fan", "input_boolean", "light", "switch", "group", "automation",
                       "humidifier", "valve", "button", "input_button", "scene"}


def effective_tile_actions(card):
    """What tapping a tile card actually does: (tap, icon tap)."""
    dom = card["entity"].split(".")[0]
    tap = (card.get("tap_action") or {"action": "more-info"}).get("action")
    icon = (card.get("icon_tap_action")
            or {"action": "toggle" if dom in TILE_TOGGLE_DOMAINS else "none"}).get("action")
    return tap, icon


def control_tile(ctx, entity, name=None, columns=6, rows=None, features=None):
    """A device control kept exactly as its V2 tile behaves: tap opens details,
    the icon toggles only where Home Assistant's tile would. Switches may only
    use this when listed in the manifest's `controls` (gated: provenance on the
    V2 view, never a protected class)."""
    ctx.use(entity)
    dom = entity.split(".")[0]
    t = {"type": "tile", "entity": entity,
         "tap_action": {"action": "more-info"},
         "icon_tap_action": {"action": "toggle" if dom in TILE_TOGGLE_DOMAINS else "none"},
         "grid_options": grid(columns, rows if rows else (2 if features else 1))}
    if name:
        t["name"] = name
    if features:
        t["features"] = [{"type": f} for f in features]
        t["features_position"] = "bottom"
    return t


def v2_verbatim(ctx, view, entities):
    """The V2 card for each entity, copied exactly from the pinned baseline view
    (links rewritten to this locale). Used where behaviour must not change by a
    single key — the sirens. The gate checks the copy is still identical."""
    import copy
    src = ctx.v2_views[view]
    out = []
    for e in entities:
        found = [c for s in src.get("sections", []) for c in s.get("cards", [])
                 if c.get("type") == "tile" and c.get("entity") == e]
        if len(found) != 1:
            raise SystemExit(f"v2_verbatim: {e} has {len(found)} tiles on V2 {view}, need exactly 1")
        ctx.use(e)
        out.append(ctx.rewrite(copy.deepcopy(found[0])))
    return out


def confirm_button(ctx, label_key, icon, action, target, confirm_key, columns=3, rows=1):
    """A button whose service call asks first (V2's filter-reset pattern), with
    the confirmation text localised. Never for a siren or a switch (gated)."""
    ctx.use(target)
    return {"type": "button", "name": ctx.t(label_key), "icon": icon, "show_state": False,
            "show_name": True, "show_icon": True,
            "tap_action": {"action": "perform-action", "perform_action": action,
                           "target": {"entity_id": target},
                           "confirmation": {"text": ctx.t(confirm_key)}},
            "hold_action": {"action": "none"}, "grid_options": grid(columns, rows)}


def shown_when(ctx, card, entity, state):
    """Show `card` only while `entity` is `state` (V2's conditional card, as a
    native visibility condition)."""
    ctx.use(entity)
    c = dict(card)
    c["visibility"] = [{"condition": "state", "entity": entity, "state": state}]
    return c


def room_conditions(ctx, rooms, bare_key):
    """One line per instrumented room: temperature and movement, each with its
    own No data branch; uninstrumented rooms are counted into one closing line
    (V2 Rooms' room conditions)."""
    nd = jstr(ctx.t("s.no_data"))
    rows, bare = [], 0
    for r in rooms:
        t, m = r.get("temp"), r.get("motion")
        if not t and not m:
            bare += 1
            continue
        parts = []
        if t:
            ctx.use(t)
            parts.append("{{ ((states('" + t + "') | float) | round(1) ~ '°') if states('" + t + "') | is_number else "
                         + jstr(ctx.t("rc.temp") + " " + ctx.t("s.no_data")) + " }}")
        if m:
            ctx.use(m)
            parts.append("{{ " + jstr(ctx.t("rc.movement")) + " if states('" + m + "') == 'on' else ("
                         + jstr(ctx.t("rc.quiet")) + " if states('" + m + "') == 'off' else "
                         + jstr(ctx.t("rc.motion") + " " + ctx.t("s.no_data")) + ") }}")
        rows.append("- **" + ctx.t(r["name_key"]) + "** " + " · ".join(parts))
    del nd
    body = "\n".join(rows)
    if bare:
        body += "\n\n<small>" + ctx.t(bare_key).replace("{n}", str(bare)) + "</small>"
    return markdown(body)


def freezer_status(ctx, plug, overload):
    """V2 Garage's freezer line, kept to what the sensors say: overloaded wins;
    'plug on, not overloaded' only when both answer (V2 said 'running normally',
    which nothing here measures); a switched-off plug; otherwise not reporting."""
    ctx.use([plug, overload])
    o, s = "states('" + overload + "')", "states('" + plug + "')"
    return markdown(
        "{%- if " + o + " == 'on' -%}**" + ctx.t("garage.overloaded") + "** " + ctx.t("garage.check_first")
        + "{%- elif " + o + " == 'off' and " + s + " == 'on' -%}" + ctx.t("garage.on_ok")
        + "{%- elif " + s + " == 'off' -%}**" + ctx.t("garage.plug_off") + "**"
        + "{%- else -%}" + ctx.t("garage.not_reporting") + "{%- endif -%}")


def scene_buttons(ctx, scenes, prefix, columns=3):
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
                    "hold_action": {"action": "none"}, "grid_options": grid(columns, 1)})
    return out
