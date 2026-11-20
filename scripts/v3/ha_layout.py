"""Home Assistant's sections-view geometry, as the installed frontend computes it.
DEVELOPMENT ONLY — NOT DEPLOYED.

Read from the home-assistant/frontend source at tag 20260826.7, the frontend
Core 2026.9.2 pins (read 14/11/26):

  * src/panels/lovelace/views/hui-sections-view.ts — how many columns a view
    resolves, and that a section's `column_span` is clamped to that count and
    handed to the section as `--column-span`;
  * src/panels/lovelace/sections/hui-grid-section.ts — a section's card grid
    has 12 x column-span units, so a band spanning two resolved columns lays
    its cards out on **24** units: `columns: 12` there is HALF the band, and
    only `columns: full` spans it. On a phone one column resolves, the span
    clamps to 1 and the same band has 12 units;
  * src/panels/lovelace/cards/hui-card.ts + common/compute-card-grid-size.ts —
    a card's own grid options are merged UNDER the dashboard's and clamped to
    the card's minimums, so a tile asked for 3 columns draws 6, and a button
    showing an icon and a name asked for 1 row draws 2.

Nothing here contacts Home Assistant. It is arithmetic over the YAML, used by
the validation gate (band packing) and by preview_view.py (the offline
preview). Whether a card renders is still only provable on the device.
"""
from __future__ import annotations

FRONTEND = "20260826.7"
ROW_HEIGHT = 56          # --row-height (section grid)
CARD_GAP = 8             # --row-gap / --column-gap inside a section
SECTION_GAP = 24         # --row-gap between sections
COLUMN_GAP = 32          # --column-gap between sections (8 below 600 px)
NARROW_GAP = 8
COLUMN_MIN = 320         # --column-min-width
COLUMN_MAX = 500         # --column-max-width


def element_grid(card):
    """The grid options a card type supplies itself (getGridOptions)."""
    t = card.get("type")
    if t == "tile":
        n = len(card.get("features") or [])
        pos = card.get("features_position", "bottom")
        rows, min_columns = 1, 6
        if n:
            if pos == "inline":
                min_columns = 12
            else:
                rows += n
        if card.get("vertical"):
            rows += 1
            min_columns = 3
        return {"columns": 6, "rows": rows, "min_columns": min_columns, "min_rows": rows}
    if t == "button":
        icon = card.get("show_icon", True)
        if icon and (card.get("show_name", True) or card.get("show_state", False)):
            return {"rows": 2, "columns": 6, "min_columns": 2, "min_rows": 2}
        return {"rows": 1, "columns": 3, "min_columns": 2, "min_rows": 1}
    if t == "heading":
        return {"columns": "full", "rows": "auto", "min_columns": 3}
    if t == "weather-forecast":
        current = card.get("show_current", True) is not False
        forecast = card.get("show_forecast", True) is not False
        rows = min_rows = 1
        if current:
            rows, min_rows = rows + 1, min_rows + 1
        if forecast:
            rows, min_rows = rows + 1, min_rows + 1
            if card.get("forecast_type") == "daily":
                rows += 1
        return {"columns": 12, "rows": rows, "min_columns": 5 if current and forecast else 4,
                "min_rows": min_rows}
    return {}   # markdown, picture-entity, todo-list, history-graph, ...: no own options


def _clamp(v, lo, hi):
    if lo is not None:
        v = max(v, lo)
    if hi is not None:
        v = min(v, hi)
    return v


def effective(card):
    """(columns, rows) the frontend actually uses: the card's own options,
    overridden by the dashboard's grid_options, clamped to the minimums."""
    o = {**element_grid(card), **(card.get("grid_options") or {})}
    cols, rows = o.get("columns", 12), o.get("rows", "auto")
    if isinstance(cols, (int, float)):
        cols = _clamp(cols, o.get("min_columns"), o.get("max_columns"))
    if isinstance(rows, (int, float)):
        rows = _clamp(rows, o.get("min_rows"), o.get("max_rows"))
    return cols, rows


def configured(card):
    g = card.get("grid_options") or {}
    return g.get("columns", 12), g.get("rows", "auto")


def resolved_columns(width, max_columns, spans):
    """Columns a sections view resolves at `width` CSS px (no sidebar)."""
    gap = NARROW_GAP if width <= 600 else COLUMN_GAP
    cols = max(int((width - 2 * gap + gap) // (COLUMN_MIN + gap)), 1)
    cols = min(cols, max_columns)
    return max(min(cols, sum(spans)), 1)


def units(column_span, resolved):
    """Card-grid units of a section: 12 per column it actually spans."""
    return 12 * min(max(column_span or 1, 1), resolved)


def place(sizes, n_units):
    """CSS grid sparse auto-placement of (columns, rows) items on `n_units`.
    Returns (placements, rows_used, holes): holes are empty cells in rows the
    band occupies — on the wall that is a gap the eye reads as a missing card."""
    occ, out = set(), []
    cr, cc = 0, 0
    for cols, rows in sizes:
        span = n_units if cols == "full" else min(int(cols), n_units)
        rs = rows if isinstance(rows, int) else 1
        if cols == "full":
            r = cr + (1 if cc > 0 else 0)
            while any((r + dr, x) in occ for dr in range(rs) for x in range(n_units)):
                r += 1
            c = 0
        else:
            r, c = cr, cc
            while True:
                if c + span > n_units:
                    r, c = r + 1, 0
                    continue
                if not any((r + dr, c + dc) in occ for dr in range(rs) for dc in range(span)):
                    break
                c += 1
        for dr in range(rs):
            for dc in range(span):
                occ.add((r + dr, c + dc))
        out.append((r, c, span, rs))
        cr, cc = r, c + span
    used = (max(r for r, _ in occ) + 1) if occ else 0
    holes = sum(1 for r in range(used) for c in range(n_units) if (r, c) not in occ)
    return out, used, holes


def visible(card, states):
    """A card's `visibility` conditions, as the frontend evaluates them, against
    a {entity: state} map (a missing entity reads 'unknown'). Screen and user
    conditions pass: a preview has no screen size or user to test."""
    def ok(c):
        k = c.get("condition")
        s = states.get(c.get("entity"), "unknown") if c.get("entity") else None
        if k == "state":
            if "state" in c:
                want = c["state"] if isinstance(c["state"], list) else [c["state"]]
                return s in [str(x) for x in want]
            if "state_not" in c:
                no = c["state_not"] if isinstance(c["state_not"], list) else [c["state_not"]]
                return s not in [str(x) for x in no]
            return True
        if k == "numeric_state":
            try:
                v = float(s)
            except (TypeError, ValueError):
                return False
            return (c.get("above") is None or v > c["above"]) and (c.get("below") is None or v < c["below"])
        if k == "and":
            return all(ok(x) for x in c["conditions"])
        if k == "or":
            return any(ok(x) for x in c["conditions"])
        if k == "not":
            return not all(ok(x) for x in c["conditions"])
        return True
    return all(ok(c) for c in card.get("visibility") or [])


def section_holes(section, n_units, states=None):
    """Empty cells left by one section's cards. With `states`, cards whose
    visibility conditions fail take no space, as on the device."""
    cards = [c for c in section.get("cards", []) if states is None or visible(c, states)]
    return place([effective(c) for c in cards], n_units)[2]
