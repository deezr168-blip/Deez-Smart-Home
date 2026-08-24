# Home Assistant — architecture and deployment

**Read this before changing anything about how config reaches the instance.**

These are settled decisions, not defaults waiting to be improved. They are
written down here because each one looks like an easy "upgrade" to anyone
arriving fresh, and each one would break a working setup.

---

## Settled decisions

### The `deez_smart_home` dashboard is storage mode

Edited through the Home Assistant UI. Its definition lives in the instance's
`.storage` directory, which is **not** in this repository and is not reachable
from a Claude session (see `docs/access_verification.md`).

**Do not convert it to YAML mode.** Storage mode is the adopted approach
because it keeps the dashboard editable from a phone or iPad, which is a hard
requirement — administration has to stay practical from a handheld device, not
only from a desktop with a git client.

### Deployment is manual, and Git Pull is deliberately not used

The HACS *Git Pull* style of automatic dashboard deployment is **intentionally
not relied upon**. This is a deliberate choice, not an unfinished migration and
not an oversight.

Automatic pull from a branch means a bad commit reaches the live house with no
human in the loop. Manual deployment keeps a person between a change and the
appliances. Do not introduce automatic deployment, and do not "finish the job"
by wiring one up.

### Navigation paths are load-bearing

Existing `/deez-smart-home/...` paths must keep working. They are bookmarked on
devices and referenced from dashboard cards. Changing a dashboard `url_path`
silently breaks every one of those and is on the approval-required list.

### Entity IDs are never invented

`docs/entity_inventory.md` records friendly names, not entity IDs, because the
available access path does not expose IDs. Anything referencing an `entity_id`
must have that ID confirmed against the live entity registry first. Slugifying
a friendly name is not confirmation — friendly names in this instance are not
even unique.

---

## What lives in this directory

Staged Home Assistant configuration: YAML intended for the instance, kept in
git for review, diffing and rollback before a human applies it.

It is **not** a mirror of the live instance and must not be read as one. Claude
cannot read the instance's config files, so nothing here is automatically
verified against what is actually running. When this directory and the live
instance disagree, **the live instance is right.**

If you add YAML here, run `bash scripts/validate.sh` before committing.

## Deploying a change

1. Stage the YAML in this directory and commit it, so there is a diff to review
   and a commit to roll back to.
2. Run `bash scripts/validate.sh` — parse errors, duplicate keys and stray secrets
   are cheaper to find here than in the instance.
3. Apply it to Home Assistant by hand.
4. Validate **in Home Assistant** (Developer Tools → YAML → Check
   Configuration). The checks in this repository are text-level only; they
   cannot confirm that an entity exists, that a service call is valid, or that
   an automation does what it should.
5. Reload the affected domain, or restart if the change requires it.
6. Confirm the result on the instance before considering the change done.

Rollback is `git revert` here, then re-apply step 3 with the previous content.

## Before touching an automation

Automations in this house control real appliances. Beyond the repository-level
checks:

- Do not assume an appliance is safe to cycle.
- Check for trigger loops and repeated firing.
- Add conditions that prevent activation while occupants are asleep or away.
- Preserve manual override.
- Do not make safe behaviour depend on a single sensor that can fail — note
  that 65 entities were `unavailable` at the last capture, so sensor failure
  here is an observed condition, not a hypothetical one.
- Never disable an existing safety interlock.
