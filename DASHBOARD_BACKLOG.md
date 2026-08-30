# Dashboard Backlog

Ranked implementation queue maintained by the Entity & Feature Scout
routine. Kept selective — high-value, evidence-based opportunities only.

Status note: as of 2026-08-30, no `dashboards/deez_smart_home.yaml` exists
in this repository yet. Every item below is a forward-looking opportunity
for whichever routine builds the initial dashboard, not a change to an
existing view. Entities are referenced by verified friendly name/domain
from a live, read-only Home Assistant pull (`GetLiveContext`); no
entity_id has been invented — exact entity_ids still need Stage 2
verification per `docs/entity_inventory.md`.

---

## FEAT-001

- **Priority:** HIGH
- **Owning routine:** Main CasaRay
- **Affected view:** All views (cross-cutting)
- **Verified entities involved:** Home-wide — 105 of 426 live
  entities/devices (~25%) currently report `unavailable`, spread across
  most areas and domains (e.g. `binary_sensor` contact sensors in
  Backyard/Living Room/Parents Room, several `light` entities in Dining
  and Living Room, TP-Link Tapo camera streams in Network, TP-Link P100
  smart plugs in Kitchen/Guest Room).
- **Current problem/opportunity:** No dashboard exists yet, so there is no
  established pattern for how a card should render when its backing
  entity is `unavailable`. With a quarter of live entities in this state
  at any given time, retrofitting graceful handling later will touch
  nearly every view.
- **Recommended implementation:** Decide the unavailable-state convention
  up front (e.g. greyed Tile with a subdued icon and "Unavailable" text
  instead of a stale last-known value, or conditional-card hiding for
  device_class-based sensors) before building out area/room views, so
  every subsequent card follows the same pattern.
- **Expected benefit:** Avoids dashboard-wide visual inconsistency and
  rework; directly serves "graceful unavailable-state handling."
- **Dependencies/blockers:** None — can be decided independently of any
  specific view.

## FEAT-002

- **Priority:** MEDIUM
- **Owning routine:** Main CasaRay
- **Affected view:** Living Room / media control
- **Verified entities involved:** Two `media_player` entities for the
  same physical TV — friendly names `Samsung Q9 Series (65)` and
  `'[TV] Samsung Q9 Series (65)'` — both in Living Room, plus a
  `remote` entity and multiple `media_player` states for `55" QLED 4k AI`
  (3 separate state records across Parents Room / Ray Bedroom areas).
- **Current problem/opportunity:** More than one integration is exposing
  control surfaces for what appears to be the same physical television,
  which risks duplicate/confusing cards if each is added individually.
- **Recommended implementation:** When building the Living Room and
  bedroom media cards, verify via entity_id (once Stage 2 inventory is
  done) which entity is the canonical, most capable control surface for
  each physical TV and use only that one; do not add both.
- **Expected benefit:** Elimination of redundant controls; cleaner card
  count per room.
- **Dependencies/blockers:** Needs entity_id-level verification
  (`docs/entity_inventory.md` Stage 2) to confirm which entities map to
  which physical devices before implementation.

## FEAT-003

- **Priority:** MEDIUM
- **Owning routine:** Main CasaRay
- **Affected view:** Home (top-level contextual summary)
- **Verified entities involved:** `person` domain (3 entities, e.g. one
  seen `not_home`), `device_tracker` domain (6 entities: Ai's iPhone,
  CasaRay iPad, Deez x2, Raymond's iPad, Vinh's phone), and
  `input_select` "Family Location" (verified state `Raymond Du`).
- **Current problem/opportunity:** There's enough real, verified presence
  data (who's home, whose devices are on the network, a manually-set
  family location helper) to support a genuinely informative "who's
  home" contextual summary, but no dashboard uses it yet.
- **Recommended implementation:** A compact presence card on the Home
  view combining `person` states with the `Family Location` input_select,
  rather than one static/manual field.
- **Expected benefit:** Whole-home usefulness and information hierarchy —
  real state instead of a card someone has to remember to update by hand.
- **Dependencies/blockers:** None functionally; benefits from Stage 2
  entity_id verification for exact person/device_tracker wiring.

## FEAT-004

- **Priority:** MEDIUM
- **Owning routine:** Main CasaRay
- **Affected view:** Security
- **Verified entities involved:** `camera` domain — 6 verified cameras:
  Front Door Live view (idle, Living Room), Smart Pet Feeder (idle,
  Dining), and 4 TP-Link Tapo streams in the Network area (Tapo C200
  Stockroom, Tapo C420 South Wall, Tapo C420 East Wall — all 3
  currently `unavailable`, and Tapo C425 North Wall — idle/available).
  Also `binary_sensor` contact sensors for doors in Backyard, Living
  Room, and Parents Room.
- **Current problem/opportunity:** No Security view exists yet, but the
  entity coverage (cameras + door contact sensors) is already sufficient
  for a genuinely useful one, including handling the fact that half the
  Tapo streams are currently unavailable.
- **Recommended implementation:** A Security view with camera glance
  cards plus door-contact-sensor state, applying the FEAT-001
  unavailable-state convention to the 3 currently-offline Tapo streams
  rather than showing a broken/frozen stream.
- **Expected benefit:** Consolidates already-available security-relevant
  entities into one coherent view instead of leaving them unused.
- **Dependencies/blockers:** Should follow FEAT-001 (unavailable-state
  convention) so the offline cameras render consistently with the rest
  of the dashboard.

## FEAT-005 (queued for Billing Dashboard Routine)

- **Priority:** HIGH (for the Billing routine's own queue)
- **Owning routine:** Billing Dashboard Routine
- **Affected view:** Billing/Energy
- **Verified entities involved:** `input_number` "Gas Bill Usage MJ"
  (verified live state `9437.04`).
- **Current problem/opportunity:** A manually-maintained gas usage helper
  already exists live, suggesting billing/utility tracking has at least
  one real, verified data point to build from rather than starting from
  nothing.
- **Recommended implementation:** Left to the Billing Dashboard Routine —
  not implemented here per ownership boundaries.
- **Expected benefit:** Real utility usage figure instead of a
  placeholder, if/when a billing view is built.
- **Dependencies/blockers:** Owned entirely by the Billing Dashboard
  Routine; this entry only records that the entity exists and is
  verified.

## FEAT-006

- **Priority:** LOW
- **Owning routine:** Main CasaRay
- **Affected view:** Living Room, Dining, Ray Bedroom (lighting)
- **Verified entities involved:** Same-name, same-area entity pairs
  appearing twice in the live pull: `Hue ambiance spot 1` (light, Living
  Room, both unavailable), `Living room` (light, Living Room), `Dining`
  (light, Dining), `NightLight` (light, Ray Bedroom).
- **Current problem/opportunity:** These look like duplicate device
  registrations (e.g. the same physical light re-added under two
  integrations), which would otherwise produce duplicate lighting cards.
  This cannot be confirmed from friendly names alone — no entity_id is
  available yet to verify.
- **Recommended implementation:** During Stage 2 entity_id verification,
  check whether each pair maps to two distinct entity_ids for the same
  device; if so, pick one canonical entity per physical light when
  building room views.
- **Expected benefit:** Prevents duplicate lighting controls per room;
  reduction of unnecessary custom/duplicate card complexity.
- **Dependencies/blockers:** Blocked on `docs/entity_inventory.md` Stage 2
  (entity_id-level registry pull) — cannot be resolved from friendly
  names alone.
