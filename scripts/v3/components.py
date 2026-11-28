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


def heading(ctx, key, style="title", columns=12):
    return {"type": "heading", "heading": ctx.t(key), "heading_style": style,
            "grid_options": grid(columns)}


def nav_button(ctx, label_key, icon, target, columns=3, rows=1, show_name=True, current=False):
    # NB Home Assistant gives a button showing an icon AND a name at least two
    # rows (hui-button-card getGridOptions); rows=1 here draws two (ha_layout.py).
    btn = {"type": "button", "name": ctx.t(label_key), "icon": icon,
           "show_name": show_name, "show_icon": True,
           "tap_action": {"action": "none"} if current else
           {"action": "navigate", "navigation_path": ctx.link(target)},
           "grid_options": grid(columns, rows)}
    if current:
        # The current destination is marked, not only inert (V3 CLAUDE.md: "always marked in
        # the navigation"). Read from the pinned frontend (20260826.7, hui-button-card.ts
        # _computeColor): with no entity, `color` sets --state-color, which tints the icon;
        # computeCssColor("accent") is var(--accent-color), which the CasaRay V3 theme maps to
        # --v3-accent — amber, "selected" in the semantic colours. No theme change needed.
        btn["color"] = "accent"
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


def prose(ctx, key, columns=12):
    """A static explanation that may hold a list (not wrapped in <small>, which
    would stop the bullets rendering)."""
    return markdown(ctx.t(key), columns)


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


def readonly_tile(ctx, entity, name=None, columns=6, nav=None, state_content=None, vertical=False):
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
    if state_content:
        t["state_content"] = state_content
    if vertical:   # a vertical tile is two rows at least (hui-tile-card getGridOptions)
        t["vertical"] = True
        t["grid_options"] = grid(columns, 2)
    return t


# Domains whose more-info dialog only shows state, history and attributes.
READ_ONLY_DOMAINS = {"sensor", "binary_sensor", "weather", "sun", "person", "device_tracker", "zone"}


def sensor_tile(ctx, entity, name=None, columns=6, nav=None, state_content=None, vertical=False, rows=None):
    """A reading. Without `nav`, a tap opens its details (history), as a V2
    tile does; only for read-only domains, whose dialog has no control."""
    t = readonly_tile(ctx, entity, name, columns, nav, state_content, vertical)
    if rows:
        t["grid_options"]["rows"] = rows
    if not nav and entity.split(".")[0] in READ_ONLY_DOMAINS:
        t["tap_action"] = {"action": "more-info"}
    return t


def person_tile(ctx, entity, nav="people", columns=4, rows=2):
    t = readonly_tile(ctx, entity, None, columns, nav)
    t["vertical"] = True
    t["grid_options"] = grid(columns, rows)
    return t


# ---------------------------------------------------------------- chrome

RAIL = [  # (view path, label key, icon) — six named buttons, 3 units each (V3-024)
    ("home", "nav.home", "mdi:home-variant-outline"),
    ("lighting", "nav.lighting", "mdi:lightbulb-group-outline"),
    ("climate", "nav.climate", "mdi:thermometer"),
    ("cameras", "nav.cameras", "mdi:cctv"),
    ("energy", "nav.energy", "mdi:lightning-bolt-outline"),
    ("security", "nav.security", "mdi:shield-home-outline"),
]


TOPBAR_HEADER = (6, 2)   # header cell: units, rows
TOPBAR_BUTTON = (3, 2)   # each rail button: units, rows (a named button is never under 2 rows)


def topbar(ctx, view_path, title_key):
    """Header cell, then the in-page rail (kiosk hides HA chrome). One bar on
    every native view, so Home sits in the same place on every page.

    History-back has no native Lovelace action, so Back on a top-level view IS
    Home (documented).

    V3-024 (release preview): readable, named navigation on both devices,
    sized from the pinned frontend's grid (ha_layout.py) so every cell has ONE
    height — a button showing an icon and a name is never under two rows:
      * wall iPad, 24 units: header 6 + six buttons x 3 = one 120 px row;
      * phone, 12 units: header 6 + 3 + 3, then 3 x 4 = two 120 px rows.
    It replaces V3-014's icon-only rail (no word on any button) and the older
    bar where only the current button was named and twice the height of the
    rest. The header holds the title, then the time above the DD/MM/YY date
    and "Preview" — text only, so it reads as a title, not a card. The current
    destination is inert and its icon amber (nav_button)."""
    title = ctx.t("app.name") if view_path == "home" else ctx.t(title_key)
    header = {"type": "markdown", "text_only": True,
              "content": "## " + title + "\n**{{ now().strftime('%H:%M') }}**<br><small>"
                         "{{ now().strftime('%d/%m/%y') }} · " + ctx.t("app.preview_banner") + "</small>",
              "grid_options": grid(*TOPBAR_HEADER)}
    cards = [header]
    for path, key, icon in RAIL:
        cards.append(nav_button(ctx, key, icon, path, columns=TOPBAR_BUTTON[0], rows=TOPBAR_BUTTON[1],
                                current=path == view_path))
    return {"type": "grid", "column_span": 2, "cards": cards}


def more_boards(ctx, items, classic_of=None, band24=False):
    """Named index of every board.

    band24: sized for the 24-unit grid Home Assistant gives a two-column band
    (ha_layout.py): a full-width heading, then four across at 6 units and the
    two rows a named button really takes — two across on a phone.

    Otherwise (V3-024) 4 units and the 2 rows the button draws anyway: six
    across on the wall iPad, three on a phone (~119 px). At 3 units a phone
    label had ~87 px, which clipped "Entertainment" (a button clips, it never
    ellipsises)."""
    cols, rows = (6, 2) if band24 else (4, 2)
    cards = [heading(ctx, "h.more", columns="full" if band24 else 12)]
    for path, key, icon in items:
        cards.append(nav_button(ctx, key, icon, path, columns=cols, rows=rows))
    if classic_of:
        cards.append(nav_button(ctx, "nav.classic", "mdi:history", "v2-" + classic_of,
                                columns=cols, rows=rows))
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


def chips(ctx, parts, columns=12):
    """One full-width markdown strip; parts joined with ' · '."""
    # The separator is an expression, not literal text: each part's `-%}`
    # trims would otherwise eat the spaces around a literal " · ".
    return markdown("{{ ' · ' }}".join(parts), columns)


def deg_expr(ctx, entity, digits=1, attr=None):
    """Jinja expression: a temperature as '19.7°' (the mockups' form), or "No
    data". With `attr`, the reading is that attribute (a weather entity's
    temperature), which is None while the entity is dark."""
    ctx.use(entity)
    v = ("state_attr('" + entity + "','" + attr + "')") if attr else ("states('" + entity + "')")
    rnd = "| round(0) | int" if digits == 0 else "| round(" + str(digits) + ")"
    return "(((" + v + " | float) " + rnd + ") ~ '°') if " + v + " | is_number else " + jstr(ctx.t("s.no_data"))


def chip_temp(ctx, label_key, entity, digits=1, attr=None):
    return ctx.t(label_key) + " **{{ " + deg_expr(ctx, entity, digits, attr) + " }}**"


def _plugs(ctx, total, plugs, digits=1):
    """(preamble, value expr, note expr) for a total the instance computes from
    `plugs`. The total is shown only while every plug it sums answers: a
    template that adds a dark plug as zero reads low without measuring
    anything (root rule: a summary whose inputs are down is a sentinel)."""
    ctx.use([total] + list(plugs))
    ids = "[" + ",".join("'" + e + "'" for e in plugs) + "]"
    pre = ("{%- set pp = namespace(ok=0) -%}{%- for e in " + ids + " -%}"
           "{%- if states(e) | is_number -%}{%- set pp.ok = pp.ok + 1 -%}{%- endif -%}{%- endfor -%}")
    n = str(len(plugs))
    val = ("(" + value_expr(ctx, total, digits) + ") if pp.ok == " + n + " else " + jstr(ctx.t("s.no_data")))
    note = ("(' <small>' ~ " + ctx.jt("chip.reporting", n="pp.ok", m=n) + " ~ '</small>') if (pp.ok > 0 and pp.ok < "
            + n + ") else ''")
    return pre, val, note


def chip_plugs(ctx, label_key, total, plugs, digits=1):
    pre, val, note = _plugs(ctx, total, plugs, digits)
    return pre + ctx.t(label_key) + " **{{ " + val + " }}**{{ " + note + " }}"


def plugs_card(ctx, label_key, total, plugs, detail_key, nav=None, columns=12, digits=1, note_key=None):
    """The mockups' Monitored power card: the two-plug total, which plugs, and
    how many answered; a tap opens the board that shows each plug.

    note_key (V3-023): the footnote that qualifies the figure, inside the card
    it qualifies, as the render draws it, rather than as a card of its own."""
    pre, val, note = _plugs(ctx, total, plugs, digits)
    foot = ("\n<small>" + ctx.t(note_key) + "</small>") if note_key else ""
    card = markdown(pre + "**" + ctx.t(label_key) + "**\n{{ " + val + " }} · " + ctx.t(detail_key)
                    + "{{ " + note + " }}" + foot, columns)
    if nav:
        card["tap_action"] = {"action": "navigate", "navigation_path": ctx.link(nav)}
    return card


def room_tile(ctx, name_key, target, parts, columns=6, rows="auto"):
    """A room as the wall render draws it: its name, one line of what its
    sensors say, and a tap that opens the room (V2 Home's room cards, ported).

    parts, each one reading:
      {entity, words: {state: key}}  the state in words; any other live state raw
      {entity, deg: digits}          a temperature, '19.7°'
      {entity, value: digits, key?}  a number with its own unit, optionally in
                                     a phrase ('Freezer {v}')
      {entity, ac: true}             the air-con's reported mode ('Air-con cool')
    A reading that does not answer is counted, never shown as a value: the line
    ends 'n not reporting', and says No data when nothing answered."""
    if not parts:   # an index tile (All rooms): its name and the tap, nothing to read
        card = markdown("**" + ctx.t(name_key) + "**", columns, rows)
        card["tap_action"] = {"action": "navigate", "navigation_path": ctx.link(target)}
        return card
    nd = jstr(ctx.t("s.no_data"))
    pre = ["{%- set ns = namespace(p=[], d=0) -%}"]
    for p in parts:
        e = p["entity"]
        ctx.use(e)
        s = "states('" + e + "')"
        dark = "{%- else -%}{%- set ns.d = ns.d + 1 -%}{%- endif -%}"
        if "words" in p:
            m = "{" + ",".join(jstr(k) + ":" + jstr(ctx.t(v)) for k, v in p["words"].items()) + "}"
            pre.append("{%- set s = " + s + " -%}{%- if s in " + m + " -%}{%- set ns.p = ns.p + [(" + m + ")[s]] -%}"
                       "{%- elif s in " + BAD + " -%}{%- set ns.d = ns.d + 1 -%}"
                       "{%- else -%}{%- set ns.p = ns.p + [s] -%}{%- endif -%}")
        elif p.get("ac"):
            pre.append("{%- if " + s + " not in " + BAD + " -%}{%- set ns.p = ns.p + [" +
                       ctx.jt("rs.ac", mode="(" + ac_mode_expr(ctx, e) + ") | lower") + "] -%}" + dark)
        elif "deg" in p:
            pre.append("{%- if " + s + " | is_number -%}{%- set ns.p = ns.p + [" +
                       deg_expr(ctx, e, p["deg"]) + "] -%}" + dark)
        elif "value" in p:
            v = value_expr(ctx, e, p["value"])
            if p.get("key"):
                v = ctx.jt(p["key"], v=v)
            pre.append("{%- if " + s + " | is_number -%}{%- set ns.p = ns.p + [" + v + "] -%}" + dark)
        else:
            raise SystemExit(f"room_tile: part for {e} has no kind (words / deg / value / ac)")
    line = ("{{ (ns.p | join(' · ')) if ns.p else " + nd + " }}"
            "{{ (' · ' ~ " + ctx.jt("s.not_reporting", n="ns.d") + ") if (ns.p and ns.d) else '' }}")
    card = markdown("".join(pre) + "**" + ctx.t(name_key) + "**\n" + line, columns, rows)
    card["tap_action"] = {"action": "navigate", "navigation_path": ctx.link(target)}
    return card


# ---------------------------------------------------------------- attention

def attention(ctx, checks, columns=12):
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
        if when == "on_ok":
            # Only 'on' is fine (a link, an emergency button): 'off' is raised as
            # `key`; anything else, dark or unexpected, as `dark_key`. Never clear.
            lines.append("{%- if s == 'on' -%}{%- set ns.ok = ns.ok + 1 -%}"
                         "{%- elif s == 'off' -%}{%- set ns.ok = ns.ok + 1 -%}{%- set ns.hits = ns.hits + [" +
                         ctx.jt(msg_key, name=jstr(name)) + "] -%}"
                         "{%- else -%}{%- set ns.hits = ns.hits + [" + ctx.jt(c["dark_key"], name=jstr(name)) +
                         "] -%}{%- endif -%}")
            continue
        if c.get("dark_key"):
            # Silence is itself the alert here (an emergency button, the internet
            # link): a dark sensor is raised in its own words, never counted clear.
            lines.append("{%- if s in " + BAD + " -%}{%- set ns.hits = ns.hits + [" +
                         ctx.jt(c["dark_key"], name=jstr(name)) + "] -%}{%- else -%}")
        if when == "offline":
            # The question is "is it offline?": unavailable answers it (a hit);
            # unknown does not answer it (not reporting).
            lines.append("{%- if s == 'unavailable' -%}{%- set ns.ok = ns.ok + 1 -%}"
                         "{%- set ns.hits = ns.hits + [" + ctx.jt(msg_key, name=jstr(name)) + "] -%}"
                         "{%- elif s in " + BAD + " -%}{%- set ns.dark = ns.dark + 1 -%}"
                         "{%- else -%}{%- set ns.ok = ns.ok + 1 -%}{%- endif -%}")
            if c.get("dark_key"):
                lines.append("{%- endif -%}")
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
            if c.get("dark_key"):
                lines.append("{%- endif -%}")
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
        if c.get("dark_key"):
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
    return markdown("".join(lines), columns)


# ---------------------------------------------------------------- climate

AC_MODES = ["off", "cool", "heat", "fan_only", "dry", "auto", "heat_cool"]


def ac_mode_expr(ctx, entity):
    """Jinja expression naming the reported mode; an unnamed mode is shown raw."""
    m = "{" + ",".join("'" + k + "':" + jstr(ctx.t("ac.mode_" + k)) for k in AC_MODES) + "}"
    return "(" + m + ").get(states('" + entity + "'), states('" + entity + "'))"


def ac_summary(ctx, entity, nav=None, columns=12, rows="auto", name_key=None, compact=False):
    """Read-only air-con card (V3-008 R1/R7): mode as reported, room and
    target from the entity's own attributes, "No data" otherwise.

    name_key (V3-023): a first line naming which air-con this is — the card
    otherwise reads only "Current: Cool". compact: the name, then the mode and
    the room temperature on one line (V3-007's own "Off · room 23.3°" form),
    for a slot the size of a button. Without either, the card is unchanged."""
    ctx.use(entity)
    nd = jstr(ctx.t("s.no_data"))

    def temp(attr):
        v = "state_attr('" + entity + "','" + attr + "')"
        return ("{{ ((" + v + " | float) | round(1) ~ '°') if " + v + " is number or ("
                + v + " | is_number) else " + nd + " }}")
    if name_key or compact:
        head = ("**" + ctx.t(name_key) + "**<br>") if name_key else ""
        if compact:
            live = ("{{ " + ac_mode_expr(ctx, entity) + " }} · " + ctx.t("ac.room") + " "
                    + temp("current_temperature"))
        else:
            live = ("{{ " + ctx.jt("ac.current", mode=ac_mode_expr(ctx, entity)) + " }}\n\n"
                    + ctx.t("ac.room") + " " + temp("current_temperature") + " · "
                    + ctx.t("ac.target") + " " + temp("temperature"))
        body = ("{%- set s = states('" + entity + "') -%}" + head
                + "{%- if s == 'unavailable' -%}" + ctx.t("s.offline") + " · " + ctx.t("s.no_data")
                + "{%- elif s in ['unknown','none',''] -%}" + ctx.t("s.state_unknown") + " · " + ctx.t("s.no_data")
                + "{%- else -%}" + live + "{%- endif -%}")
        card = markdown(body, columns, rows)
        if nav:
            card["tap_action"] = {"action": "navigate", "navigation_path": ctx.link(nav)}
        return card
    body = ("{%- set s = states('" + entity + "') -%}"
            "{%- if s == 'unavailable' -%}**" + ctx.t("s.offline") + "** · " + ctx.t("s.no_data")
            + "{%- elif s in ['unknown','none',''] -%}**" + ctx.t("s.state_unknown") + "** · " + ctx.t("s.no_data")
            + "{%- else -%}**{{ " + ctx.jt("ac.current", mode=ac_mode_expr(ctx, entity)) + " }}**\n\n"
            + ctx.t("ac.room") + " " + temp("current_temperature") + " · "
            + ctx.t("ac.target") + " " + temp("temperature")
            + "{%- endif -%}")
    card = markdown(body, columns, rows)
    if nav:
        card["tap_action"] = {"action": "navigate", "navigation_path": ctx.link(nav)}
    return card


# ---------------------------------------------------------------- cameras

def camera_state_expr(ctx, entity):
    ctx.use(entity)
    return ("(" + jstr(ctx.t("s.offline")) + " if states('" + entity + "') == 'unavailable' else ("
            + jstr(ctx.t("s.state_unknown")) + " if states('" + entity + "') in ['unknown','none',''] else "
            + jstr(ctx.t("s.online")) + "))")


def camera_summary(ctx, cams, columns=12, rows="auto"):
    ents = [c["entity"] for c in cams]
    ctx.use(ents)
    ids = "[" + ",".join("'" + e + "'" for e in ents) + "]"
    head = ("{%- set ns = namespace(a=0, b=0, c=0) -%}{%- for e in " + ids + " -%}"
            "{%- set s = states(e) -%}{%- if s == 'unavailable' -%}{%- set ns.b = ns.b + 1 -%}"
            "{%- elif s in ['unknown','none',''] -%}{%- set ns.c = ns.c + 1 -%}"
            "{%- else -%}{%- set ns.a = ns.a + 1 -%}{%- endif -%}{%- endfor -%}")
    lines = "".join("\n- " + ctx.t(c["name_key"]) + " — **{{ " + camera_state_expr(ctx, c["entity"]) + " }}**"
                    for c in cams)
    return markdown(head + "**{{ " + ctx.jt("cam.summary", a="ns.a", b="ns.b", c="ns.c") + " }}**\n" + lines, columns, rows)


def camera_card(ctx, entity, name_key, subview=None, columns=6, rows=4, full_screen="subview",
                offline=False, battery=None):
    """A camera's picture. full_screen: 'subview' opens its V2 page (the
    custom:webrtc-camera card); 'more-info' opens Home Assistant's own camera
    dialog, whose live stream needs no custom card.

    offline: Home Assistant draws a dark camera as a broken image with no word
    (hui-image.ts), so the slot gets a twin of the same size that says Offline
    in words, and shows instead of the picture while the camera entity is
    unavailable. Exactly one of the two is visible, so the grid keeps its
    shape. `battery` adds the camera's battery reading to that card: a camera
    whose battery answers while its stream does not is a stream problem, not
    a dead camera.

    V3-030: the twin also covers `unknown`, and says "State unknown" there
    rather than Offline. hui-image still fetches an unknown camera's image (a
    broken image, no word). Offline and unknown are different states and say
    different words (V3 rule: four camera states, never colour alone).
    A camera entity that does not exist at all: frontend 20260826.7 reads it
    as `unknown`, so the twin shows; the newer frontend seen on the Green on
    20/11/26 sends the condition to Core, which errors, and BOTH cards hide
    (ha_layout.visible). Camera health still names that camera."""
    ctx.use(entity)
    tap = ({"action": "more-info"} if full_screen == "more-info" else
           {"action": "navigate", "navigation_path": ctx.link(subview)})
    pic = {"type": "picture-entity", "entity": entity, "name": ctx.t(name_key),
           "camera_view": "auto", "show_state": False, "show_name": True,
           "tap_action": tap, "hold_action": {"action": "none"},
           "grid_options": grid(columns, rows)}
    if not offline:
        return pic
    dark = ["unavailable", "unknown"]
    pic["visibility"] = [{"condition": "state", "entity": entity, "state_not": list(dark)}]
    word = ("{{ " + jstr(ctx.t("s.offline")) + " if states('" + entity + "') == 'unavailable' else "
            + jstr(ctx.t("s.state_unknown")) + " }}")
    body = "**" + ctx.t(name_key) + "** · **" + word + "**\n" + ctx.t("cam.no_stream")
    if battery:
        ctx.use(battery)
        b = "states('" + battery + "')"
        body += (" · {{ (" + ctx.jt("cam.battery", v="(" + b + " | float) | round(0) | int") + ") if "
                 + b + " | is_number else " + jstr(ctx.t("cam.no_battery")) + " }}")
    twin = markdown(body, columns, rows)
    twin["visibility"] = [{"condition": "state", "entity": entity, "state": list(dark)}]
    return [pic, twin]


def chip_cameras(ctx, ents):
    ctx.use(ents)
    return chip_count(ctx, "chip.cameras", ents, ["idle", "streaming", "recording"])


# ---------------------------------------------------------------- misc

def weather(ctx, entity, forecast=False, columns=12, forecast_type="daily", current=True, rows=None):
    """Native weather-forecast card. forecast_type is the pinned frontend's own
    set (20260826.7, data/weather.ts: hourly | daily | twice_daily); a forecast
    the entity does not provide is the card's own "no forecast", never invented."""
    if forecast_type not in ("hourly", "daily", "twice_daily"):
        raise SystemExit(f"weather: forecast_type {forecast_type!r} is not one the frontend knows")
    ctx.use(entity)
    c = {"type": "weather-forecast", "entity": entity, "show_current": current,
         "show_forecast": forecast, "grid_options": grid(columns)}
    if forecast:
        c["forecast_type"] = forecast_type
    if rows:
        c["grid_options"]["rows"] = rows
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


def _check_expr(c):
    """(hit, dark) Jinja boolean expressions for one attention-style check, the
    same semantics attention() uses, so a count strip and its lists agree."""
    e = c["entity"]
    s = "states('" + e + "')"
    when = c["when"]
    if when == "on_ok":
        return s + " != 'on'", "false"
    if when == "offline":
        hit, dark = s + " == 'unavailable'", s + " in ['unknown','none','']"
    elif isinstance(when, str) and when.startswith("battery<"):
        lim = when.split("<")[1]
        hit = "(" + s + " | is_number and (" + s + " | float) < " + lim + ")"
        dark = "(" + s + " in " + BAD + " or not (" + s + " | is_number))"
    else:
        st = "[" + ",".join("'" + w + "'" for w in when) + "]"
        hit, dark = s + " in " + st, s + " in " + BAD
    if c.get("dark_key"):
        hit, dark = "(" + hit + " or " + s + " in " + BAD + ")", "false"
    return hit, dark


def alert_counts(ctx, groups):
    """One chip per severity: hits among the checks that answered, and how many
    did not. A group where nothing answered says No data, never 0."""
    parts = []
    for gi, g in enumerate(groups):
        ctx.use([c["entity"] for c in g["checks"]])
        v = f"a{gi}"
        pre = "{%- set " + v + " = namespace(hit=0, dark=0) -%}"
        for c in g["checks"]:
            hit, dark = _check_expr(c)
            pre += ("{%- if " + hit + " -%}{%- set " + v + ".hit = " + v + ".hit + 1 -%}"
                    "{%- elif " + dark + " -%}{%- set " + v + ".dark = " + v + ".dark + 1 -%}{%- endif -%}")
        n = len(g["checks"])
        parts.append(pre + ctx.t(g["label_key"]) + " **{%- if " + v + ".dark == " + str(n) + " and " + v
                     + ".hit == 0 -%}" + ctx.t("s.no_data") + "{%- else -%}{{ " + v + ".hit }}{%- endif -%}**"
                     + "{%- if " + v + ".dark and " + v + ".dark < " + str(n) + " %} <small>{{ "
                     + ctx.jt("s.not_reporting", n=v + ".dark") + " }}</small>{% endif -%}")
    return chips(ctx, parts)


def presence(ctx, people):
    """Who is home, honestly. Home and away are only what a person entity says;
    one that is not reporting is counted as such and never as away. "Nobody is
    home" is only said when every person answered and none is home.
    people: [{entity, name}] — names as V2 shows them (proper nouns, not translated)."""
    ents = [x["entity"] for x in people]
    ctx.use(ents)
    ids = "[" + ",".join("'" + p + "'" for p in ents) + "]"
    names = "{" + ",".join("'" + x["entity"] + "':" + jstr(x["name"]) for x in people) + "}"
    head = ("{%- set ns = namespace(home=[], away=[], dark=0) -%}{%- for p in " + ids + " -%}"
            "{%- set s = states(p) -%}{%- if s == 'home' -%}{%- set ns.home = ns.home + [(" + names + ")[p]] -%}"
            "{%- elif s in " + BAD + " -%}{%- set ns.dark = ns.dark + 1 -%}"
            "{%- else -%}{%- set ns.away = ns.away + [(" + names + ")[p]] -%}{%- endif -%}{%- endfor -%}")
    sep = jstr(ctx.t("list.sep"))
    body = ("**" + ctx.t("pp.at_home") + "** {%- if ns.home %} " + "{{ ns.home | join(" + sep + ") }}"
            "{%- elif ns.dark == " + str(len(people)) + " %} " + ctx.t("pp.nobody_reporting")
            + "{%- elif ns.dark %} " + ctx.t("pp.none_confirmed")
            + "{%- else %} " + ctx.t("pp.nobody_home") + "{%- endif %}\n\n"
            "**" + ctx.t("pp.away") + "** {%- if ns.away %} {{ ns.away | join(" + sep + ") }}{%- else %} —{%- endif %}"
            "{%- if ns.dark %} · {{ " + ctx.jt("pp.location_unknown", n="ns.dark") + " }}{%- endif %}")
    return markdown(head + body)


def zone_presence(ctx, zone, people):
    """Home Assistant's own zone count, beside the people. A count of zero is
    only stated as such when every person answered: while any is dark, a zero
    zone cannot tell 'nobody home' from 'nobody reporting'."""
    ctx.use([zone] + list(people))
    z = "states('" + zone + "')"
    ids = "[" + ",".join("'" + p + "'" for p in people) + "]"
    head = ("{%- set ns = namespace(dark=0, home=0) -%}{%- for p in " + ids + " -%}"
            "{%- if states(p) in " + BAD + " -%}{%- set ns.dark = ns.dark + 1 -%}"
            "{%- elif states(p) == 'home' -%}{%- set ns.home = ns.home + 1 -%}{%- endif -%}{%- endfor -%}")
    n = "((" + z + " | float) | round(0) | int)"
    differs = ("(' <small>' ~ " + ctx.jt("pp.zone_differs", n="ns.home") + " ~ '</small>') if (ns.dark == 0 and "
               + n + " != ns.home) else ''")
    # One expression, no {% %} tags, so no trim can eat the spaces or the note's line break.
    value = ("{{ " + jstr(ctx.t("s.no_data")) + " if not (" + z + " | is_number) else ("
             "(" + jstr(ctx.t("pp.unconfirmed")) + " ~ ' <small>' ~ "
             + ctx.jt("pp.people_dark", n="ns.dark", m=str(len(people))) + " ~ '</small>')"
             " if ((" + z + " | float) == 0 and ns.dark) else (" + n + " ~ (" + differs + "))) }}")
    body = "**" + ctx.t("pp.zone") + "** " + value + "\n\n<small>" + ctx.t("pp.zone_note") + "</small>"
    return markdown(head + body)


def battery_summary(ctx, items, threshold=None):
    """Lowest battery and who, how many report, and (with a threshold) which are
    under it. Nothing reporting says so; no level is guessed."""
    ctx.use([i["entity"] for i in items])
    pairs = "[" + ",".join("('" + i["entity"] + "'," + jstr(ctx.t(i["name_key"])) + ")" for i in items) + "]"
    head = ("{%- set ns = namespace(low=none, who='', n=0, under=[]) -%}{%- for e, nm in " + pairs + " -%}"
            "{%- if states(e) | is_number -%}{%- set v = states(e) | float -%}{%- set ns.n = ns.n + 1 -%}"
            "{%- if ns.low is none or v < ns.low -%}{%- set ns.low = v -%}{%- set ns.who = nm -%}{%- endif -%}")
    if threshold is not None:
        head += "{%- if v < " + str(threshold) + " -%}{%- set ns.under = ns.under + [nm] -%}{%- endif -%}"
    head += "{%- endif -%}{%- endfor -%}"
    m = str(len(items))
    body = ("{%- if ns.low is none -%}**" + ctx.t("bat.none_reporting") + "**"
            "{%- else -%}**{{ " + ctx.jt("bat.lowest", v="(ns.low | round(0) | int)", name="ns.who") + " }}**"
            " · {{ " + ctx.jt("chip.reporting", n="ns.n", m=m) + " }}{%- endif -%}")
    if threshold is not None:
        body += ("{%- if ns.under %}\n\n**{{ " + ctx.jt("bat.under", t=str(threshold)) + " }}** "
                 "{{ ns.under | join(" + jstr(ctx.t("list.sep")) + ") }}{%- endif -%}")
    return markdown(head + body)


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


# ---------------------------------------------------------------- bilingual preview (V3-025)
# The 19/11/26 bilingual mockups, as a SEPARATE preview dashboard (build_preview).
# Every label is two-level — 中文 strong, English small — from ctx.pair(), so
# these components only run with the build's BiCtx. Native cards only; each
# rendering trick below was read in the pinned frontend (20260826.7):
#   * markdown raw HTML: table[role=presentation] is styled borderless by
#     ha-markdown; td align/valign, b, small, big, br and <ha-icon icon> pass
#     its sanitiser (xss default whitelist + table role + ha-icon);
#   * GitHub alert blocks (> [!WARNING]) become ha-alert: warning uses
#     --warning-color (the V3 theme's amber), caution --error-color (red);
#   * the sections view's own `footer` is sticky at the bottom of the screen;
#   * a button's `color` tints its icon with no entity (the current tab).

def _pair(ctx, key):
    if not hasattr(ctx, "pair"):
        raise SystemExit("preview components need the build's bilingual BiCtx")
    return ctx.pair(key)


def _two(ctx, key, strong=True):
    """'<b>中文</b><br><small>English</small>' — the mockups' two-level label."""
    a, b = _pair(ctx, key)
    return ("<b>" + a + "</b>" if strong else a) + ("<br><small>" + b + "</small>" if b != a else "")


def _words(ctx, entity, words, which):
    """Jinja expression: the state in words in ONE language (which: 0 or 1).
    unavailable / unknown are their own branches, never a word from `words`."""
    ctx.use(entity)
    m = "{" + ",".join(jstr(k) + ":" + jstr(_pair(ctx, v)[which]) for k, v in words.items()) + "}"
    s = "states('" + entity + "')"
    return ("(" + jstr(_pair(ctx, "s.no_data")[which]) + " if " + s + " in " + BAD + " else "
            "(" + m + ").get(" + s + ", " + s + "))")


WEATHER_ICONS = {
    "clear-night": "weather-night", "cloudy": "weather-cloudy", "exceptional": "alert-circle-outline",
    "fog": "weather-fog", "hail": "weather-hail", "lightning": "weather-lightning",
    "lightning-rainy": "weather-lightning-rainy", "partlycloudy": "weather-partly-cloudy",
    "pouring": "weather-pouring", "rainy": "weather-rainy", "snowy": "weather-snowy",
    "snowy-rainy": "weather-snowy-rainy", "sunny": "weather-sunny", "windy": "weather-windy",
    "windy-variant": "weather-windy-variant",
}


def _weather_icon(entity):
    m = "{" + ",".join("'" + k + "':'mdi:" + v + "'" for k, v in WEATHER_ICONS.items()) + "}"
    return "(" + m + ").get(states('" + entity + "'), 'mdi:weather-cloudy-alert')"


def _attr_deg(ctx, entity, attr, digits=0):
    """An attribute temperature, only while the ENTITY answers (V3-021: a dark
    entity's leftover attribute is never shown)."""
    ctx.use(entity)
    v = "state_attr('" + entity + "','" + attr + "')"
    rnd = "| round(0) | int" if digits == 0 else "| round(" + str(digits) + ")"
    return ("(((" + v + " | float) " + rnd + ") ~ '°C') if (states('" + entity + "') not in " + BAD
            + " and " + v + " | is_number) else " + jstr(_pair(ctx, "s.no_data")[0]))


def preview_header(ctx, title_key, weather="weather.forecast_home"):
    """The mockups' header band: CasaRay｜page, the preview badge, the weather,
    then the time above the date (DD/MM/YY, repository rule; the mockup's 18/11
    drops the year) with the weekday in both languages."""
    a, b = _pair(ctx, title_key)
    ba, bb = _pair(ctx, "pv.badge")
    days = "[" + ",".join(jstr(" ".join(dict.fromkeys(_pair(ctx, f"pv.wd{i}")))) for i in range(7)) + "]"
    temp = _attr_deg(ctx, weather, "temperature")
    content = (
        '<table role="presentation" width="100%"><tr>'
        '<td valign="middle"><big><b>CasaRay</b>｜<b>' + a + "</b> " + (b if b != a else "") + "</big>"
        "<br><small>" + ba + " · " + bb + "</small></td>"
        '<td align="right" valign="middle" width="96"><ha-icon icon="{{ ' + _weather_icon(weather) + ' }}"></ha-icon> '
        "<b>{{ " + temp + " }}</b></td>"
        '<td align="right" valign="middle" width="150"><big><b>{{ now().strftime(\'%H:%M\') }}</b></big>'
        "<br><small>{{ " + days + "[now().weekday()] }} · {{ now().strftime('%d/%m/%y') }}</small></td>"
        "</tr></table>")
    return {"type": "grid", "column_span": 2, "cards": [markdown(content, "full")]}


def preview_footer(ctx, tabs, current_tab, view_path, max_width=1032):
    """Home Assistant's sticky sections-view footer holding ONE grid card of the
    mockups' five tabs. The tab whose section this page belongs to is tinted
    amber; it is inert only on the tab's own page (on Climate, More is tinted
    and still opens More, as a tab bar returns to its root). Five fit a phone
    (~68 px each); `icon_height` keeps the bar near the mockups' height."""
    cards = []
    for path, key, icon in tabs:
        here = path == view_path
        btn = {"type": "button", "name": ctx.t(key), "icon": icon, "icon_height": "28px",
               "show_name": True, "show_icon": True,
               "tap_action": {"action": "none"} if here else
               {"action": "navigate", "navigation_path": ctx.link(path)},
               "hold_action": {"action": "none"}, "grid_options": grid(12, 1)}
        if path == current_tab:
            btn["color"] = "accent"
        cards.append(btn)
    return {"card": {"type": "grid", "columns": len(tabs), "square": False, "cards": cards},
            "max_width": max_width}


def preview_greeting(ctx, columns=12, rows=2):
    """早晨，今日屋企點？ by the hour, as the mockup's greeting card."""
    parts = []
    for key, test in (("pv.morning", "h < 12"), ("pv.afternoon", "h < 18"), ("pv.evening", None)):
        a, b = _pair(ctx, key)
        parts.append((test, a, b))
    qa, qb = _pair(ctx, "pv.how_home")
    expr = ("{%- set h = now().hour -%}"
            "{%- if " + parts[0][0] + " -%}{%- set g = [" + jstr(parts[0][1]) + "," + jstr(parts[0][2]) + "] -%}"
            "{%- elif " + parts[1][0] + " -%}{%- set g = [" + jstr(parts[1][1]) + "," + jstr(parts[1][2]) + "] -%}"
            "{%- else -%}{%- set g = [" + jstr(parts[2][1]) + "," + jstr(parts[2][2]) + "] -%}{%- endif -%}")
    return markdown(expr + "## {{ g[0] }}，" + qa + "\n{{ g[1] }}, " + qb, columns, rows)


def preview_weather(ctx, entity="weather.forecast_home", columns=12, rows=2):
    """The mockups' weather card: the temperature large, the condition in both
    languages. While the entity does not answer (or the instance has no such
    entity) it is the named No data card: 天氣 Weather · 無資料 No data."""
    ctx.use(entity)
    conds = {c: f"pv.cond.{c}" for c in WEATHER_ICONS}
    wa, wb = _pair(ctx, "pv.weather")
    da, db = _pair(ctx, "s.no_data")
    s = "states('" + entity + "')"
    return markdown(
        "{%- if " + s + " in " + BAD + " -%}"
        '## <ha-icon icon="mdi:weather-cloudy-alert"></ha-icon> ' + wa + " " + wb + "\n"
        "**" + da + "** <small>" + db + "</small>"
        "{%- else -%}"
        '## <ha-icon icon="{{ ' + _weather_icon(entity) + ' }}"></ha-icon> {{ '
        + _attr_deg(ctx, entity, "temperature") + " }}\n"
        "**{{ " + _words(ctx, entity, conds, 0) + " }}**<br><small>{{ " + _words(ctx, entity, conds, 1) + " }}</small>"
        "{%- endif -%}",
        columns, rows)


def preview_door_banner(ctx, entity, open_key, dark_key, target):
    """The mockups' amber banner while the door is open, and — because a missing
    banner would read as "closed" — a plain one while the sensor is silent.
    Nothing shows only while the door reports closed."""
    ctx.use(entity)
    oa, ob = _pair(ctx, open_key)
    va, vb = _pair(ctx, "pv.view_door")
    da, db = _pair(ctx, dark_key)
    opened = markdown("> [!WARNING]\n> **" + oa + "** " + ob + " · **" + va + "** " + vb + " ›", "full")
    opened["visibility"] = [{"condition": "state", "entity": entity, "state": "on"}]
    opened["tap_action"] = {"action": "navigate", "navigation_path": ctx.link(target)}
    # self-hiding, not a condition: a sensor the instance lacks must still say so
    dark = _self_hiding("{%- if states('" + entity + "') not in ['on', 'off'] -%}**" + da + "** <small>" + db
                        + "</small>{%- endif -%}", "full", "auto")
    return [opened, dark]


def preview_room(ctx, name_key, icon, target, status, columns=12):
    """A row of the mockups' room list: icon, name in both languages, one
    reading in both, a chevron; a tap opens the room. status:
      {entity, label_key, words: {state: key}}   a state in words
      {entity, label_key, deg: digits}           a temperature
      {entity, label_key, value: digits}         a number with its unit"""
    e = status["entity"]
    ctx.use(e)
    la, lb = _pair(ctx, status["label_key"])
    if "words" in status:
        va = "{{ " + _words(ctx, e, status["words"], 0) + " }}"
        vb = ": {{ " + _words(ctx, e, status["words"], 1) + " }}"
    elif "deg" in status:
        va, vb = "{{ " + deg_expr(ctx, e, status["deg"]).replace(jstr(ctx.t("s.no_data")),
                                                                  jstr(_pair(ctx, "s.no_data")[0])) + " }}", ""
    else:
        va, vb = "{{ " + value_expr(ctx, e, status["value"]).replace(jstr(ctx.t("s.no_data")),
                                                                      jstr(_pair(ctx, "s.no_data")[0])) + " }}", ""
    na, nb = _pair(ctx, name_key)
    content = ('<table role="presentation" width="100%"><tr>'
               '<td width="40" valign="middle"><ha-icon icon="' + icon + '"></ha-icon></td>'
               '<td valign="middle"><b>' + na + "</b><br><small>" + nb + "</small></td>"
               '<td align="right" valign="middle">' + la + "：<b>" + va + "</b><br><small>" + lb + vb + "</small></td>"
               '<td width="16" align="right" valign="middle">›</td></tr></table>')
    card = markdown(content, columns)
    # '#hash' opens that Bubble Card pop-up on this page (V3-026); a page name opens the page
    card["tap_action"] = {"action": "navigate",
                          "navigation_path": target if str(target).startswith("#") else ctx.link(target)}
    return card


def preview_mode(ctx, label_key, icon, note_key, action=None, target=None, data=None, columns=12, rows="auto"):
    """A scene-mode card from the mockups. With an action it does exactly what
    its line says (an existing, owner-approved light action); without one it is
    inert and says it is not set up — no scene entity backs it."""
    a, b = _pair(ctx, label_key)
    na, nb = _pair(ctx, note_key)
    card = markdown('<ha-icon icon="' + icon + '"></ha-icon> **' + a + "** " + b
                    + "<br><small>" + na + " · " + nb + "</small>", columns, rows)
    if action:
        ctx.use(target)
        tap = {"action": "perform-action", "perform_action": action, "target": {"entity_id": target}}
        if data:
            tap["data"] = data
        card["tap_action"] = tap
        card["hold_action"] = {"action": "none"}
    return card


def preview_about(ctx, title_key, body_key, columns=12, rows="auto"):
    ta, tb = _pair(ctx, title_key)
    ba, bb = _pair(ctx, body_key)
    return markdown("**" + ta + "** " + tb + "\n\n" + ba + "\n\n<small>" + bb + "</small>", columns, rows)


def preview_ac_status(ctx, entity, nav=None, columns=12, rows="auto"):
    """The mockups' big air-con state, read-only (V3-008): running / off in
    words with the mode, never a control; offline and unknown in their own words."""
    ctx.use(entity)
    va, vb = _pair(ctx, "pv.view_only")
    ra, rb = _pair(ctx, "pv.running")
    oa, ob = _pair(ctx, "pv.ac_off")
    xa, xb = _pair(ctx, "s.offline")
    ua, ub = _pair(ctx, "s.state_unknown")
    modes = {k: "ac.mode_" + k for k in AC_MODES}
    body = ("{%- set s = states('" + entity + "') -%}"
            "{%- if s == 'unavailable' -%}## " + xa + "\n" + xb +
            "{%- elif s in ['unknown','none',''] -%}## " + ua + "\n" + ub +
            "{%- elif s == 'off' -%}## " + oa + "（" + va + "）\n" + ob + " (" + vb + ")" +
            "{%- else -%}## " + ra + "：{{ " + _words(ctx, entity, modes, 0) + " }}（" + va + "）\n"
            + rb + ": {{ " + _words(ctx, entity, modes, 1) + " }} (" + vb + ")" + "{%- endif -%}")
    card = markdown(body, columns, rows)
    if nav:
        card["tap_action"] = {"action": "navigate", "navigation_path": ctx.link(nav)}
    return card


def preview_reading(ctx, label_key, entity, attr=None, columns=4, rows=2):
    """A labelled reading: label in both languages over the value; an attribute
    reading only while its entity answers."""
    ctx.use(entity)
    if attr:
        val = _attr_deg(ctx, entity, attr, digits=0)
    else:
        val = value_expr(ctx, entity, 0).replace(jstr(ctx.t("s.no_data")), jstr(_pair(ctx, "s.no_data")[0]))
    return markdown(_two(ctx, label_key) + "\n## {{ " + val + " }}", columns, rows)


def preview_filter(ctx, flag, last_reset, columns=12):
    """Filter reminder from what is measured: the needs-cleaning flag and the
    last reset. The mockups' "in about 30 days" needs an interval no entity
    gives, so it is not drawn."""
    ctx.use([flag, last_reset])
    words = {"on": "pv.filter_due", "off": "pv.filter_ok"}
    ra, rb = _pair(ctx, "pv.last_reset")
    # Days since the reset, said in both languages. Not relative_time(): Home
    # Assistant returns that in English ("3 days") whatever the dashboard says.
    # as_datetime() raises on a dark sensor's state unless given a default.
    dt = "as_datetime(states('" + last_reset + "'), none)"
    da, db = _pair(ctx, "pv.days_ago")
    nd = _pair(ctx, "s.no_data")
    days = "(now() - " + dt + ").days"
    lr_a = "(" + jstr(da.split("{n}")[0]) + " ~ " + days + " ~ " + jstr(da.split("{n}")[1]) + ") if " + dt + " is not none else " + jstr(nd[0])
    lr_b = "(" + jstr(db.split("{n}")[0]) + " ~ " + days + " ~ " + jstr(db.split("{n}")[1]) + ") if " + dt + " is not none else " + jstr(nd[1])
    return markdown(_two(ctx, "pv.filter") + "\n\n**{{ " + _words(ctx, flag, words, 0) + " }}**<br>"
                    "<small>{{ " + _words(ctx, flag, words, 1) + " }}</small>\n\n"
                    "<small>" + ra + "：{{ " + lr_a + " }} · " + rb + ": {{ " + lr_b + " }}</small>", columns)


def preview_timer(ctx, switch, end, columns=12):
    """The air-con's own timer, read-only: off, or on with its end time. The
    end time is read only while the timer is on (as V2 does)."""
    ctx.use([switch, end])
    na, nb = _pair(ctx, "pv.timer_off")
    ea, eb = _pair(ctx, "pv.timer_on")
    ts = "as_timestamp(states('" + end + "'), none)"   # local time; raises without the default
    t = "(" + ts + " | timestamp_custom('%H:%M')) if " + ts + " is not none else " + jstr(_pair(ctx, "s.no_data")[0])
    s = "states('" + switch + "')"
    da, db = _pair(ctx, "s.no_data")
    # "{% if" (no left trim): a "{%-" here would eat the blank line and run the
    # label into the state ("Timer無資料")
    return markdown(_two(ctx, "pv.timer") + "\n\n"
                    "{% if " + s + " == 'on' -%}**" + ea + " {{ " + t + " }}**<br><small>" + eb + " {{ " + t + " }}</small>"
                    "{%- elif " + s + " == 'off' -%}**" + na + "**<br><small>" + nb + "</small>"
                    "{%- else -%}**" + da + "**<br><small>" + db + "</small>{%- endif -%}", columns)


DARK = ["unavailable", "unknown"]   # states() reads an entity the instance lacks as 'unknown'


def _self_hiding(body, columns, rows):
    """A markdown card that hides itself while `body` renders to nothing
    (`show_empty: false`, hui-markdown-card.ts). Used instead of a visibility
    condition wherever the card must appear for an entity the instance may
    not have: newer frontends evaluate visibility in Home Assistant Core,
    which errors on an unknown entity, and the card is then hidden whatever
    the condition says (the 20/11/26 trial). A template reads that entity as
    'unknown', so the card still shows."""
    card = markdown(body, columns, rows)
    card["show_empty"] = False
    return card


def preview_nodata(ctx, entity, name_key, icon, columns=12, rows=1):
    """The named No data card that stands in a reading's place, at the same size,
    while Home Assistant cannot confirm it: unavailable, unknown, or an entity ID
    the instance does not have. Self-hiding (no visibility condition: see
    _self_hiding). A tile for a missing entity draws an empty warning card whose
    text only admins see (hui-error-card) — the trial's "missing tiles"; its own
    visibility condition hides it in both frontends. One row holds one line, so
    the one-row card carries no icon (an icon outgrows a 56 px row) and sets its
    English small, so the line fits a phone's 56 px row."""
    ctx.use(entity)
    na, nb = _pair(ctx, name_key)
    da, db = _pair(ctx, "s.no_data")
    s = "states('" + entity + "')"
    gate = "{%- if " + s + " in " + str(DARK).replace('"', "'") + " -%}"
    if rows == 1:
        body = "**" + na + "** <small>" + nb + "</small> · **" + da + "** <small>" + db + "</small>"
    else:
        why = ("{{ (" + jstr(ctx.t("s.offline")) + " if " + s + " == 'unavailable' else "
               + jstr(ctx.t("pv.unconfirmed")) + ") }}")
        body = ('<ha-icon icon="' + icon + '"></ha-icon> **' + na + "** " + nb + " · **" + da + "** " + db
                + "<br><small>" + why + "</small>")
    return _self_hiding(gate + body + "{%- endif -%}", columns, rows)


def preview_tile(ctx, entity, name_key, kind="readonly", icon="mdi:lightbulb-outline", columns=12, nav=None,
                 nodata_key=None):
    """A tile while its entity answers, the named No data card of the same size
    while it does not; exactly one shows, so the grid keeps its shape — in both
    frontends: the tile's condition hides it for a dark or missing entity, and
    the No data card hides itself while the entity answers.
    kind: light    V3 Lighting's own controls (details, icon toggle, brightness bar)
          readonly state only; a tap navigates (`nav`), nothing else acts
          sensor   a reading; a tap opens its history (read-only dialog)
    nodata_key: a shorter name for the No data card, where the tile's own name
    (which the tile ellipsises) would not fit one line on a phone."""
    name = ctx.t(name_key)
    if kind == "light":
        t, rows = light_tile(ctx, entity, name, columns), 2
    elif kind == "sensor":
        t, rows = sensor_tile(ctx, entity, name, columns, nav=nav, rows=1), 1
    else:
        t, rows = readonly_tile(ctx, entity, name, columns, nav=nav), 1
        t["grid_options"]["rows"] = 1
    t["visibility"] = [{"condition": "state", "entity": entity, "state_not": list(DARK)}]
    nd = preview_nodata(ctx, entity, nodata_key or name_key, icon, columns, rows)
    if nav:
        nd["tap_action"] = {"action": "navigate", "navigation_path": ctx.link(nav)}
    return [t, nd]


def preview_cam_slot(ctx, entity, name_key, battery=None, columns=12, rows=3):
    """One camera, one slot of one size whatever its state: the picture while
    the camera entity answers (a tap opens Home Assistant's camera dialog, where
    the live stream plays), otherwise a named card in words — Offline, or State
    unknown, which also covers a camera ID the instance does not have (a
    self-hiding card: see _self_hiding). The picture card claims no state: an idle entity is not proof that its stream
    plays, which only the dialog shows. Replaces the 2914b09 pair (a 4-unit name
    cell beside an 8-unit picture) whose two halves read as uneven slots."""
    ctx.use(entity)
    na, nb = _pair(ctx, name_key)
    # name and a chevron: "· 點擊查看畫面 Tap to view" was cut off on the trial iPad
    pic = {"type": "picture-entity", "entity": entity, "name": na + " " + nb + " ›",
           "camera_view": "auto", "show_state": False, "show_name": True,
           "tap_action": {"action": "more-info"}, "hold_action": {"action": "none"},
           "grid_options": grid(columns, rows),
           "visibility": [{"condition": "state", "entity": entity, "state_not": list(DARK)}]}
    s = "states('" + entity + "')"
    bat = ""
    if battery:
        ctx.use(battery)
        b = "states('" + battery + "')"
        bat = (" · {{ (" + ctx.jt("cam.battery", v="(" + b + " | float) | round(0) | int") + ") if "
               + b + " | is_number else " + jstr(ctx.t("cam.no_battery")) + " }}")
    xa, xb = _pair(ctx, "s.offline")
    ua, ub = _pair(ctx, "s.state_unknown")
    head = '<ha-icon icon="mdi:video-off-outline"></ha-icon> **' + na + "** " + nb + " · "
    body = ("{%- if " + s + " == 'unavailable' -%}" + head + "**" + xa + "** " + xb
            + "<br><small>" + ctx.t("cam.no_stream") + bat + "</small>"
            "{%- elif " + s + " == 'unknown' -%}" + head + "**" + ua + "** " + ub
            + "<br><small>" + ctx.t("pv.cam_unreadable") + bat + "</small>{%- endif -%}")
    return [pic, _self_hiding(body, columns, rows)]


def preview_camera(ctx, entity, name_key, battery=None):
    """One cell of the Cameras overview: a full slot (12 units, 3 rows; two
    across on the wall iPad, one on a phone)."""
    return preview_cam_slot(ctx, entity, name_key, battery, columns=12, rows=3)


def preview_link(ctx, label_key, target, icon=None, columns=12, rows=1):
    """A one-row link in both languages (the mockups' 睇門口 View front door).
    One heading-free line, so it fits a 56 px row."""
    a, b = _pair(ctx, label_key)
    card = markdown("**" + a + "** " + b + " ›", columns, rows)   # no icon: it outgrows a 56 px row
    card["tap_action"] = {"action": "navigate", "navigation_path": ctx.link(target)}
    return card


# ---------------------------------------------------------------- custom cards (V3-026)
# Owner decision 20/11/26: the preview may use seven HACS cards (Kiosk Mode,
# Bubble Card, Advanced Camera Card, auto-entities, ApexCharts, Power Flow Card
# Plus, WallPanel). Every option below is in the card's own README or docs/
# (design/casaray-v3/hacs/HACS_RECOMMENDATIONS_2026-11-20.md). Nothing is
# installed by this: until the owner installs each card on the Green, Home
# Assistant draws "Custom element doesn't exist" in its place.

PREVIEW_CUSTOM = {"custom:bubble-card", "custom:advanced-camera-card", "custom:auto-entities",
                  "custom:apexcharts-card", "custom:power-flow-card-plus"}


def _bubble(entity, name, icon=None, kind="state"):
    """A Bubble Card button. kind: 'slider' (a light: the slider sets its
    brightness, the icon toggles it) or 'state' (a reading: a tap on the icon or
    the button opens its details, nothing else acts)."""
    b = {"type": "custom:bubble-card", "card_type": "button", "button_type": kind, "entity": entity, "name": name}
    if icon:
        b["icon"] = icon
    if kind != "slider":
        b["tap_action"] = {"action": "more-info"}
        b["button_action"] = {"tap_action": {"action": "more-info"}}
    return b


def preview_bubble_room(ctx, hash, name_key, icon, lights=(), readings=()):
    """A room's Bubble Card pop-up (standalone format, v3.2.0+): hidden until
    its hash is opened (the Rooms row navigates to it), then a sheet over the
    page with the room's lights as sliders and its readings as state buttons.
    lights: [[entity, name_key], ...]; readings: [[entity, name_key, icon], ...]."""
    if not str(hash).startswith("#"):
        raise SystemExit(f"bubble pop-up hash must start with '#': {hash!r}")
    cards = []
    for e, k in lights:
        if not e.startswith("light."):
            raise SystemExit(f"bubble slider for a non-light: {e}")
        ctx.use(e)
        cards.append(_bubble(e, ctx.t(k), kind="slider"))
    for e, k, ic in readings:
        ctx.use(e)
        cards.append(_bubble(e, ctx.t(k), ic, kind="state"))
    return {"type": "custom:bubble-card", "card_type": "pop-up", "hash": hash, "name": ctx.t(name_key),
            "icon": icon, "cards": cards, "grid_options": grid("full")}


def preview_acc(ctx, cameras, grid_max_columns=3):
    """Advanced Camera Card: every camera live in one fixed grid. A camera whose
    entity is unavailable errors in its own cell (always_error_if_entity_unavailable)
    instead of spinning. cameras: [[camera entity, name_key], ...]."""
    cams = []
    for e, k in cameras:
        ctx.use(e)
        cams.append({"camera_entity": e, "title": ctx.t(k), "always_error_if_entity_unavailable": True})
    return {"type": "custom:advanced-camera-card", "cameras": cams,
            "live": {"display": {"mode": "grid", "grid_max_columns": grid_max_columns}},
            "grid_options": grid("full")}


def preview_power_flow(ctx, solar, grid_import, columns=12):
    """Power Flow Card Plus: solar and grid import. With no home or export entity
    the card adds the sources up for Home, which reads high while the panels
    export (pv.home_caveat says so beside it)."""
    ctx.use([solar, grid_import])
    return {"type": "custom:power-flow-card-plus",
            "entities": {"solar": {"entity": solar, "name": ctx.t("pv.solar")},
                         "grid": {"entity": grid_import, "name": ctx.t("pv.grid_import")},
                         "home": {"name": ctx.t("pv.home_power")}},
            "grid_options": grid(columns)}


def preview_apex_today(ctx, solar, grid_import, columns=12):
    """ApexCharts: today from midnight, solar and grid import as areas."""
    ctx.use([solar, grid_import])
    return {"type": "custom:apexcharts-card", "graph_span": "24h", "span": {"start": "day"},
            "header": {"show": True, "title": ctx.t("pv.today")}, "now": {"show": True},
            "series": [{"entity": solar, "name": ctx.t("pv.solar"), "type": "area"},
                       {"entity": grid_import, "name": ctx.t("pv.grid_import"), "type": "area"}],
            "grid_options": grid(columns)}


def preview_unavailable_list(ctx, title_key, domains, columns=12):
    """auto-entities: every entity of these domains whose state is unavailable,
    in an entities card, by name. With none, its `else` card says so for this
    kind only (a list of what answered, not a reassurance about the house)."""
    na, nb = _pair(ctx, "pv.hh_none")
    return {"type": "custom:auto-entities",
            "card": {"type": "entities", "title": ctx.t(title_key)},
            "filter": {"include": [{"domain": d, "state": "unavailable"} for d in domains]},
            "sort": {"method": "name"},
            "else": markdown("**" + ctx.t(title_key) + "**\n\n" + na + " <small>" + nb + "</small>", columns),
            "grid_options": grid(columns)}


def preview_wallpanel(ctx, idle_time=120, temperature="sensor.bedroom_motion_sensor_temperature",
                      door="binary_sensor.f_contact_sensor_door"):
    """WallPanel (dashboard-level `wallpanel:`): after `idle_time` seconds the
    screen shows the photos in Home Assistant's media folder with an info box —
    the time over DD/MM/YY, the parents' room temperature and the front door.
    It leaves the header and sidebar to Kiosk Mode (hide_* false), so the two
    never fight over them."""
    ctx.use([temperature, door])
    days = "[" + ",".join(jstr(" ".join(dict.fromkeys(_pair(ctx, f"pv.wd{i}")))) for i in range(7)) + "]"
    clock = markdown("# {{ now().strftime('%H:%M') }}\n{{ " + days + "[now().weekday()] }} · {{ now().strftime('%d/%m/%y') }}")
    ta, tb = _pair(ctx, "pv.parents_temp")
    temp = markdown("**" + ta + "** " + tb + "\n## {{ " + deg_expr(ctx, temperature, 1) + " }}")
    da, db = _pair(ctx, "room.front_door")
    words = {"on": "pv.wp_open", "off": "pv.wp_closed"}
    door_card = markdown("**" + da + "** " + db + "\n## {{ " + _words(ctx, door, words, 0) + " }} "
                         "<small>{{ " + _words(ctx, door, words, 1) + " }}</small>")
    for c in (clock, temp, door_card):
        c.pop("grid_options", None)   # the info box lays its cards out itself
    return {"enabled": True, "hide_toolbar": False, "hide_sidebar": False, "fullscreen": False,
            "idle_time": idle_time, "image_url": "media-source://media_source/",
            "cards": [clock, temp, door_card]}


# ---------------------------------------------------------------- custom cards on the working dashboards (V3-027)
# V3-026 approved seven HACS cards and the owner chose "Adopt cards in V3"; V3-027
# brings four of them to the working dashboards, each in its own band AFTER the
# page's native content, with a note saying what it needs. Until a card is
# installed through HACS, Home Assistant draws "Custom element doesn't exist" in
# that band only; every native reading, control and link above it is unchanged.
# Not here, and why (V3-027): Kiosk Mode (removed after the "kiosk mode lockout";
# restoring it on a working dashboard is the owner's call), Bubble Card and
# Advanced Camera Card (bound to six entity IDs not found on the instance).
# Options are exactly those reviewed for the preview (V3-026, PR #27); labels are
# one language per locale, from the working catalogues.

WORKING_CUSTOM = {"energy": {"custom:power-flow-card-plus", "custom:apexcharts-card"},
                  "house-health": {"custom:auto-entities"}}
# the native card auto-entities fills, allowed where auto-entities is
WORKING_INNER = {"house-health": {"entities"}}


def power_flow(ctx, solar, grid_import, columns=12):
    """Power Flow Card Plus: solar and grid import. With no consumption or export
    entity the card adds the sources up for Home, which reads high while the
    panels export; energy.flow_caveat says so beside it."""
    ctx.use([solar, grid_import])
    return {"type": "custom:power-flow-card-plus",
            "entities": {"solar": {"entity": solar, "name": ctx.t("h.solar")},
                         "grid": {"entity": grid_import, "name": ctx.t("energy.flow_grid")},
                         "home": {"name": ctx.t("energy.flow_home")}},
            "grid_options": grid(columns)}


def apex_today(ctx, solar, grid_import, columns=12):
    """ApexCharts: today from midnight, solar and grid import as areas."""
    ctx.use([solar, grid_import])
    return {"type": "custom:apexcharts-card", "graph_span": "24h", "span": {"start": "day"},
            "header": {"show": True, "title": ctx.t("energy.flow_today")}, "now": {"show": True},
            "series": [{"entity": solar, "name": ctx.t("h.solar"), "type": "area"},
                       {"entity": grid_import, "name": ctx.t("energy.flow_grid"), "type": "area"}],
            "grid_options": grid(columns)}


def unavailable_list(ctx, title_key, domains, columns=12):
    """auto-entities: every entity of these domains whose state is unavailable, by
    name, in an entities card. With none, the `else` card says so for this kind
    only: a statement about what reports unavailable, not about the house."""
    return {"type": "custom:auto-entities",
            "card": {"type": "entities", "title": ctx.t(title_key)},
            "filter": {"include": [{"domain": d, "state": "unavailable"} for d in domains]},
            "sort": {"method": "name"},
            "else": markdown("**" + ctx.t(title_key) + "**\n\n<small>" + ctx.t("hh.list_none") + "</small>", columns),
            "grid_options": grid(columns)}


def wallpanel(ctx, idle_time=120, temperature="sensor.bedroom_motion_sensor_temperature",
              door="binary_sensor.f_contact_sensor_door"):
    """WallPanel (dashboard-level `wallpanel:`), the preview's reviewed options:
    after `idle_time` seconds the photos in Home Assistant's media folder, with
    the time over DD/MM/YY, the parents' room temperature and the front door.
    Header and sidebar are left alone (hide_* false). Ignored by Home Assistant
    while the card is not installed; a touch returns to the dashboard."""
    clock = markdown("# {{ now().strftime('%H:%M') }}\n{{ now().strftime('%d/%m/%y') }}")
    temp = markdown("**" + ctx.t("wp.parents_temp") + "**\n## {{ " + deg_expr(ctx, temperature, 1) + " }}")
    door_card = markdown("**" + ctx.t("room.front_door") + "**\n## {{ "
                         + word_expr(ctx, door, {"on": "s.open", "off": "s.closed"}) + " }}")
    for c in (clock, temp, door_card):
        c.pop("grid_options", None)   # the info box lays its cards out itself
    return {"enabled": True, "hide_toolbar": False, "hide_sidebar": False, "fullscreen": False,
            "idle_time": idle_time, "image_url": "media-source://media_source/",
            "cards": [clock, temp, door_card]}


# ---------------------------------------------------------------- Navbar card (V3-028)
# Owner, 21/11/26: "Add in navbar for navigation". Navbar Card is installed on the
# instance (the owner's card picker lists it). Every option below is in the card's
# own docs (joseluis9595/lovelace-navbar-card, docs/content/docs/configuration/*.md
# and advanced/custom-actions.md at main, read 21/11/26); nothing else is set. The
# native top bar stays on every page: if the card fails to load, the page still
# navigates (and Home Assistant shows "Custom element doesn't exist" at its foot).

NAVBAR = "custom:navbar-card"


def navbar(ctx, routes, more):
    """One navbar for a page: the main destinations as labelled routes, the rest
    behind a "More" route that opens the card's popup. A route is drawn selected
    when its url is the page's own path; with reflect_child_state, More is
    selected while one of its pages is open, so the current destination is
    always marked. routes / more: [[path, label_key, icon], ...]."""
    def route(path, key, icon):
        return {"url": ctx.link(path), "icon": icon, "label": ctx.t(key)}
    items = [route(*r) for r in routes]
    items.append({"icon": "mdi:dots-horizontal", "label": ctx.t("nav.more"),
                  "tap_action": {"action": "open-popup"}, "popup": [route(*r) for r in more]})
    return {"type": NAVBAR, "routes": items,
            "desktop": {"show_labels": True},
            "mobile": {"show_labels": True, "safe_area": True},
            "layout": {"reflect_child_state": True},
            "grid_options": grid("full")}


# ---------------------------------------------------------------- Clock Weather Card (V3-029)
# Owner, 21/11/26: "switch weather band to clock weather". Installed on the instance
# (docs/casaray-v3/HACS_INSTALLED.md, the owner's HACS list; the owner's phone shows it
# working). Options from the card's own README and CONTRIBUTING.md at
# pkissling/clock-weather-card main (3.1.0, 01/11/26), read 21/11/26: the v3 `sections`
# schema (v3.0.0, 25/10/26). The header keeps the card's documented default rows, with
# only the two patterns this house needs: time HH:mm over date dd/MM/yy (DD/MM/YY).
# The hourly forecast strip and the daily forecast list are the card's defaults.

CLOCK_WEATHER = "custom:clock-weather-card"
# the card's own translations are en, zh-hant and zh-hans (src/locales/, 21/11/26); for
# any other tag it falls back to English text while dates still format in that language
CWC_LOCALE = {"en": "en-au", "yue": "zh-hant", "zh-Hans": "zh-hans", "km": "km"}


def clock_weather(ctx, entity):
    """Clock Weather Card on one weather entity: icon, temperature and condition, the
    time over DD/MM/YY, the hourly strip (with sunrise/sunset), the daily list."""
    if not entity.startswith("weather."):
        raise SystemExit(f"clock_weather: {entity} is not a weather entity")
    ctx.use(entity)
    rows = [
        {"segments": [{"type": "icon", "icon": "mdi:thermometer"},
                      {"type": "weather", "attribute": "temperature"},
                      {"type": "spacer"}, {"type": "weather"}]},
        {"font_size": "4rem", "alignment": "center", "segments": [{"type": "time", "time_pattern": "HH:mm"}]},
        {"alignment": "center", "segments": [{"type": "icon", "icon": "mdi:calendar"},
                                             {"type": "date", "date_pattern": "dd/MM/yy"}]},
    ]
    return {"type": CLOCK_WEATHER, "entity": entity, "locale": CWC_LOCALE[ctx.locale["code"]],
            "sections": {"header": {"rows": rows}}, "grid_options": grid("full")}
