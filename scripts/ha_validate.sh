#!/usr/bin/env bash
#
# Validation gate for the Deez Smart Home maintenance framework.
#
#   bash scripts/ha_validate.sh
#
# Read-only: never contacts Home Assistant, never modifies a file, never runs
# a git command that writes. Exit 0 = safe to commit and deploy. Exit 1 = do
# not deploy.
#
# SCOPE. These are repository-side checks. Home Assistant's own configuration
# validator is NOT run and is not available from this environment (no /config,
# no `hass`, no reachable API — see DEPLOYMENT_BLOCKERS.md). A pass means the
# change is well-formed and internally consistent. It does not mean a card
# renders or an entity exists.

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

fails=0; n=0
pass() { printf '  \033[32mok\033[0m    %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; fails=$((fails+1)); }
sect() { n=$((n+1)); printf '\n\033[1m[%d] %s\033[0m\n' "$n" "$1"; }

mapfile -t files < <(git ls-files --cached --others --exclude-standard 2>/dev/null)
mapfile -t yamls < <(printf '%s\n' "${files[@]:-}" | grep -E '\.ya?ml$' || true)
mapfile -t dashes < <(printf '%s\n' "${files[@]:-}" | grep -E '^dashboards/.*\.ya?ml$' || true)

sect "YAML syntax and duplicate keys"
if [ "${#yamls[@]}" -eq 0 ]; then pass "no YAML tracked"
elif python3 scripts/yaml_check.py "${yamls[@]}"; then pass "${#yamls[@]} file(s) parsed, no duplicate keys"
else fail "YAML problems above"; fi

sect "Dashboard structure, templates, navigation, mass-damage"
if [ "${#dashes[@]}" -eq 0 ]; then pass "no dashboard files"
elif python3 scripts/dashboard_check.py "${dashes[@]}"; then pass "dashboard checks passed"
else fail "dashboard checks failed"; fi

sect "Protected files must not be modified autonomously"
protected='(^|/)(secrets\.ya?ml|configuration\.yaml|automations\.yaml|scripts\.yaml|scenes\.yaml|known_devices\.yaml|ip_bans\.yaml|auth_provider\..*)$|^\.storage/|(^|/)\.env'
touched=$(git diff --cached --name-only; git diff --name-only)
hits=$(printf '%s\n' "$touched" | sort -u | grep -E "$protected" || true)
if [ -n "$hits" ]; then
  fail "protected path(s) modified — requires explicit owner approval:"
  printf '        %s\n' $hits
else pass "no protected path touched"; fi

sect "Secrets and credentials"
secret_names='(^|/)(secrets\.ya?ml|\.env|id_rsa|id_ed25519|known_hosts|authorized_keys)$|\.(pem|key|p12|pfx|token)$'
tracked=$(git ls-files | grep -E "$secret_names" | grep -v '\.env\.example$' || true)
[ -n "$tracked" ] && { fail "secret-bearing file tracked:"; printf '        %s\n' $tracked; } \
                  || pass "no secret-bearing filenames tracked"
jwt='eyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}'
pk='-----BEGIN[ A-Z]*PRIVATE KEY-----'
url='[a-z]+://[^[:space:]"]*:[^[:space:]"@]*@'
nabu='[a-z0-9-]+\.ui\.nabu\.casa'
# GitHub tokens: the deploy path uses one (see DEPLOY_AUTH.md), so the gate
# must refuse to let one reach a tracked file. Length-bounded so short
# placeholders in documentation do not trip it.
ghtok='gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,}'
hits=0
for f in "${files[@]:-}"; do
  [ -f "$f" ] || continue
  case "$f" in scripts/ha_validate.sh) continue ;; esac
  while IFS=: read -r ln _; do
    [ -n "$ln" ] || continue; printf '        %s:%s\n' "$f" "$ln"; hits=$((hits+1))
  done < <(grep -InE "$jwt|$pk|$url|$nabu|$ghtok" "$f" 2>/dev/null || true)
done
[ "$hits" -gt 0 ] && fail "$hits credential-shaped line(s) (locations only; values not printed)" \
                  || pass "no credential-shaped literals"

sect "Unexpected deletions"
deleted=$(git diff --cached --name-only --diff-filter=D; git diff --name-only --diff-filter=D)
deleted=$(printf '%s\n' "$deleted" | sort -u | sed '/^$/d')
if [ -n "$deleted" ]; then
  fail "file(s) deleted — confirm this is intended before deploying:"
  printf '        %s\n' $deleted
else pass "no files deleted"; fi

sect "Whitespace, conflict markers, binaries"
git diff --check HEAD -- . >/dev/null 2>&1 && pass "git diff --check clean" \
  || { fail "git diff --check:"; git diff --check HEAD -- . 2>&1 | sed 's/^/        /'; }
conf=$(grep -rInE '^(<{7}|={7}|>{7})( |$)' --exclude-dir=.git --exclude=ha_validate.sh . 2>/dev/null || true)
[ -n "$conf" ] && { fail "conflict markers:"; printf '%s\n' "$conf" | sed 's/^/        /'; } \
               || pass "no conflict markers"
bins=""
for f in "${files[@]:-}"; do
  [ -f "$f" ] || continue
  [ -s "$f" ] || continue          # empty files (.gitkeep) are not binary
  grep -qI . "$f" 2>/dev/null || bins="$bins $f"
done
[ -n "$bins" ] && fail "unexpected binary file(s):$bins" || pass "no unexpected binaries"

sect "Home Assistant configuration validation"
if command -v hass >/dev/null 2>&1; then
  hass --script check_config -c . && pass "hass check_config passed" || fail "hass check_config failed"
else
  printf '  \033[33mSKIP\033[0m  UNAVAILABLE — no hass CLI, no /config, no reachable API.\n'
  printf '        Repository checks cannot substitute. Verify in the browser after deploy.\n'
fi

printf '\n'
if [ "$fails" -eq 0 ]; then
  printf '\033[32mVALIDATION PASSED\033[0m (%d sections)\n' "$n"
  printf 'Repository-side only — Home Assistant schema and entity existence NOT verified.\n'
  exit 0
fi
printf '\033[31mVALIDATION FAILED — %d problem(s). Do not deploy.\033[0m\n' "$fails"
exit 1
