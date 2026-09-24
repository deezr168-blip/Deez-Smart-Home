# Rollback drill

**Ten minutes, once.** Proves that if a deployment goes wrong, the dashboard
can be put back — on *your* host, with *your* paths.

`scripts/test_rollback.sh` already proves the logic: 17 assertions, run in a
throwaway tree in this repository. What it cannot prove is that
`/config/casaray/` exists, that the scripts are installed, that `BACKUP_DIR`
points where you think, and that Home Assistant actually picks up a changed
file. That is what this drill is for.

**Risk:** for about two minutes the wall shows `CasaRay ROLLBACK TEST` instead
of `CasaRay`. Nothing else changes, no entity is touched, no automation runs,
and step 1 is your escape hatch. If you are interrupted and walk away, the
worst case is a silly word on a screen.

**Do not skip step 1.**

---

## Before you start

```sh
sh /config/casaray/casaray_health_check.sh
sh /config/casaray/casaray_rollback.sh --list
```

Expect: health check reports the chain is sound, and the list shows some
backups (or `(none)` — that is fine, step 1 makes one).

If `/config/casaray/` does not exist, the suite was never installed. Run
`scripts/casaray_onboard.sh` first and report back — do not continue.

---

## Step 1 — safety copy, and the backup the drill restores from

```sh
cp /config/dashboards/casaray_v2.yaml ~/casaray_SAFETY.yaml
cp /config/dashboards/casaray_v2.yaml \
   /config/dashboards/backups/casaray_v2.yaml.predeploy.$(date +%Y%m%d-%H%M%S)
```

The first copy is yours and nothing in this suite can touch it. The second is
the one rollback will restore. **If anything at all goes wrong from here on:**

```sh
cp ~/casaray_SAFETY.yaml /config/dashboards/casaray_v2.yaml
```

That single command ends the drill safely at any point.

---

## Step 2 — break it, visibly and harmlessly

```sh
sed -i 's/^        # CasaRay$/        # CasaRay ROLLBACK TEST/' \
    /config/dashboards/casaray_v2.yaml
grep -c 'ROLLBACK TEST' /config/dashboards/casaray_v2.yaml
```

Expect: `1`.

The pattern is anchored to the eight-space indent on purpose. `# CasaRay`
also appears as the file's own first-line header comment, and an unanchored
substitution would rewrite that too — harmless, but it would print `2` here
and leave you wondering which one mattered. Verified against the committed
file: exactly one line matches, the header is untouched, and all 28 views
still parse afterwards.

If it prints `0`, the wordmark is written differently than this assumes —
stop, tell me, and I will give you the right pattern. Do not improvise a
different edit.

---

## Step 3 — confirm Home Assistant picked it up

Open the wall iPad or your phone, go to Home, and **refresh**.

Expect: the wordmark reads `CasaRay ROLLBACK TEST`.

- Still says `CasaRay`? Hard-refresh (pull down, or close and reopen the app).
- **Still `CasaRay` after a hard refresh?** Stop and tell me. That is a real
  finding, and a more important one than the drill: it would mean a deployed
  file does not reach the screen without a reload step nobody has written
  down, and every "deployed" claim this project has made would need revisiting.

---

## Step 4 — roll back

```sh
sh /config/casaray/casaray_rollback.sh
```

Expect, in order:

```
[INFO] === rollback starting: casaray_v2.yaml.predeploy.<timestamp> ===
[INFO] current dashboard saved first: casaray_v2.yaml.predeploy.<newer>
[INFO] restored: casaray_v2.yaml.predeploy.<timestamp> -> /config/dashboards/casaray_v2.yaml
[INFO] === rollback finished: OK ===
```

The middle line matters as much as the others: it means the rollback itself
was reversible, so a rollback to the wrong version is recoverable too.

---

## Step 5 — confirm it is really back

```sh
grep -c 'ROLLBACK TEST' /config/dashboards/casaray_v2.yaml
cmp ~/casaray_SAFETY.yaml /config/dashboards/casaray_v2.yaml && echo "IDENTICAL"
```

Expect: `0`, then `IDENTICAL`.

Then refresh the screen. Expect: `CasaRay`, and the page exactly as it was.

---

## Step 6 — tidy up

```sh
rm ~/casaray_SAFETY.yaml
sh /config/casaray/casaray_rollback.sh --list
```

The drill's backups can stay — the suite keeps the newest 30 and prunes the
rest by itself.

---

## What to tell me

Just the answers to these five:

1. Did step 3 show the marker, and did it need a hard refresh?
2. Did step 4 print the "current dashboard saved first" line?
3. Did step 5 print `IDENTICAL`?
4. Did the page look normal afterwards?
5. Anything that surprised you.

With a clean result, rollback stops being a script nobody has run and becomes
a safety net — which is the thing that has to be true before any deployment
happens without a person watching.

## If it goes wrong

```sh
cp ~/casaray_SAFETY.yaml /config/dashboards/casaray_v2.yaml
```

Then send me the exact output of whatever failed. A failed drill is a good
outcome: it found the problem on a cosmetic marker instead of on a real
deployment.
