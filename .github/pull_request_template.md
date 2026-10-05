## What changed and why

<!-- One logical change per PR. State what was wrong, what changed, and why this fix and not another. -->

## Verified offline

- [ ] `bash scripts/ha_validate.sh` — exit 0
- [ ] `python3 -m unittest discover -s tests` — green
- [ ] `python3 scripts/audit_casaray.py --check --strict` — clean
- [ ] `python3 scripts/review_packet.py` attached or linked

## Verified live

<!-- "Committed" is not "deployed". List ONLY what was seen on the running instance, each with evidence (screenshot, or states read from the API). If nothing, write "Nothing verified live." -->

## NOT verified

<!-- Everything visual, every width, every entity availability, anything that needs the host. Be specific. -->

## Risk and rollback

- [ ] Touches no protected path (`MAINTENANCE.md`), no secrets, no authentication
- [ ] Takes no physical-house or security action; reduces no protection
- [ ] No gate, test or check was weakened, skipped or removed
- [ ] Rollback is `git revert` of a single commit, or: …

## Owner actions raised

<!-- Link the rows added to docs/OWNER_ACTION_QUEUE.md, or "none". -->
