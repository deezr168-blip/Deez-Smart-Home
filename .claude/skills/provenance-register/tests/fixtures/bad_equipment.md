# EXAMPLE ONLY

Fictional data for testing the linter. Every row below is wrong in exactly one way, except the first.
Expected: errors E2 E3 E4 E5 E6 E7, and warning W1.

| ID | Item | Location | Owner | Rating (kW) | Status | Source | Verified on | Verified by | Notes |
|---|---|---|---|---|---|---|---|---|---|
| EX-001 | Example pump | Example shed | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | fine |
| EX-002 | Example fan | Example garage | Example Person A | 0.5 | ASSUMED | UNKNOWN | UNKNOWN | UNKNOWN | guess |
| EX-003 | Example heater | | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | blank location |
| EX-003 | Example light | Example hall | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | duplicate id |
| EX-004 | Example saw | Example shed | Example Person B | 2.2 | VERIFIED | UNKNOWN | 2026-01-05 | Example Person B | no source |
| EX-005 | Example drill | Example shed | UNKNOWN | UNKNOWN | CHECKED | data plate | UNKNOWN | UNKNOWN | odd status |
| EX-006 | Example lamp | Example hall | UNKNOWN | UNKNOWN | VERIFIED | data plate | soon | Example Person B | tbc |
