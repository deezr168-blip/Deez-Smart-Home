# CasaRay mockups, 14 September 2026 — the current visual target

Owner-supplied, and the reference that supersedes the earlier generic CasaRay
renders for anything they disagree on. These were drawn from **this
instance's real entities** — the Fronius Primo, the two metered circuits, the
four unreachable Hue spots, the two offline C420s, the emergency buttons — so
where a mockup shows a state, that state is reachable rather than invented.

| File | Screen |
|---|---|
| `mockups/2026-09-14_wall_home.png` | Home, wall panel (landscape) |
| `mockups/2026-09-14_mobile_home.png` | Home, phone (portrait) |
| `mockups/2026-09-14_wall_living_room.png` | Living room |
| `mockups/2026-09-14_wall_security.png` | Security |
| `mockups/2026-09-14_wall_energy.png` | Energy |
| `mockups/2026-09-14_dash_home.png` | Home, alternate treatment |
| `mockups/2026-09-14_dash_living_room.png` | Living room, alternate treatment |

## The design language, as drawn

**Headings are sentence case, not uppercase.** "Right now", "Who's home",
"Needs attention", "One tap", "Air & media", "What's using power". Each is
preceded by a small dim icon. This reverses the uppercase treatment CasaRay
carried until now; the mockups are unambiguous about it.

**Page titles are modest.** "Security", "Living room", "Energy" sit at roughly
the weight of the nav row beside them — nothing like the outsized `#` the
dashboard used to render. Sentence case again, not uppercase.

**A chip strip sits under the header**, before any card: pill-shaped, dim
label then bright value — `Outside 10°`, `Inside 19.7°`, `Home 2 of 3`,
`Monitored 147.9 W`. Page-specific: Security shows `Doors All closed`,
`Cameras 4 of 6 online`, `Last doorbell Yesterday 11:22 am`; Energy shows
`Monitored now`, `Forecast today`, `Grid carbon`; Living room shows `Room`,
`Movement`, `Light level`. On the phone only two chips survive.

**Cards are a circular icon, a bold name, and one secondary line.** The
secondary line carries interpreted state, not a raw value: "On · warm white",
"Closed · 6 hours ago", "Quiet · 22 minutes", "On · PM2.5 is 5 µg/m³, good".

**Controls appear as a filled bar inside the card** — the light's brightness
as an amber bar reading `89%`, the purifier's `Speed · high`. These are Home
Assistant tile *features*, not custom cards.

**Amber means on or active.** An active socket, a light that is on, a room
with movement now, the selected mood — amber icon, amber text, amber border.
Everything at rest is grey. Green is reserved for good security states: a
closed door's icon, a camera's `● LIVE` dot.

**Attention is a red-tinted card** with a red circular icon, a bold claim and
a specific detail line: "Batteries need changing / Front doorbell 20% · Ring
chime 20% · North wall camera 22%".

**Unavailable is drawn, never hidden.** A dashed border, muted text and a
`NO DATA` or `OFFLINE` pill — the offline C420s, the unreachable inverter, the
backyard freezer plug. The card keeps its place in the layout.

**Rooms are full-width rows**, not a button grid: icon, room name, an amber
status line, a chevron at the right. `Living room / 1 light on  19.7°`.

**Footnotes explain, in grey, below the section they qualify.** "Two circuits
are metered, so this is monitored load — not the whole house." "SolarNet keeps
publishing 0 W while the inverter is unreachable. Nothing on this page reads
from it — the panel shows 'no data' instead of a zero." These are the same
honesty rules `CLAUDE.md` already requires, given a visual home.

## What is not yet reachable

The **One tap** scene tiles (Evening, Goodnight, Movie, All lights off) need
whole-home scenes, which this instance does not have — see `CR-233`. Nothing
else on these screens requires an entity the instance lacks.
