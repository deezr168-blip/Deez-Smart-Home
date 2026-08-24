#!/usr/bin/env bash
#
# Pre-deployment checks for the Deez Smart Home repository.
#
# Read-only: never contacts Home Assistant, never modifies a file, never runs a
# git command that writes. Safe to run at any time.
#
#   ./scripts/validate.sh
#
# Exits 0 if everything passes, 1 if any check fails.
#
# SCOPE — read this before trusting a green run.
# These are text-level checks on this repository. They CANNOT tell you that an
# entity exists, that a service call is valid, that a dashboard renders, or
# that an automation is safe. Home Assistant's own Check Configuration, run on
# the instance, remains the authority. A pass here means "worth applying", not
# "known good".

set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

failures=0
run=0

pass() { printf '  \033[32mok\033[0m    %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; failures=$((failures + 1)); }
head2() { run=$((run + 1)); printf '\n\033[1m[%d] %s\033[0m\n' "$run" "$1"; }

# Files git knows about: tracked, plus untracked ones that .gitignore does not
# exclude. That is exactly the set that could reach a commit.
mapfile -t candidates < <(git ls-files --cached --others --exclude-standard 2>/dev/null)

# ---------------------------------------------------------------------------
head2 "YAML syntax and duplicate keys"

mapfile -t yaml_files < <(printf '%s\n' "${candidates[@]:-}" | grep -E '\.ya?ml$' || true)

if [ "${#yaml_files[@]}" -eq 0 ]; then
  pass "no YAML files in the repository yet — nothing to parse"
else
  if python3 scripts/yaml_check.py "${yaml_files[@]}"; then
    pass "${#yaml_files[@]} YAML file(s) parsed, no duplicate keys"
  else
    fail "YAML problems above"
  fi
fi

# ---------------------------------------------------------------------------
head2 "Sensitive files must not be committed"

secret_names='(^|/)(secrets\.ya?ml|\.env|\.env\..*|id_rsa|id_ed25519|known_hosts)$|\.(pem|key|p12|pfx)$'
tracked_secrets=$(git ls-files 2>/dev/null | grep -E "$secret_names" | grep -v '\.env\.example$' || true)

if [ -n "$tracked_secrets" ]; then
  fail "these are tracked by git and should not be:"
  printf '        %s\n' $tracked_secrets
else
  pass "no secret-bearing filenames tracked"
fi

# ---------------------------------------------------------------------------
head2 "Secret-shaped content"

# Deliberately narrow: an assignment with a literal value that looks like a
# real credential. Prose about tokens, and `!secret` indirection, are fine.
# Report the file and line number only — never the matched value.
placeholder='(!secret|!env_var|YOUR_|CHANGE_?ME|REPLACE|EXAMPLE|PLACEHOLDER|REDACTED|xxxx|\.\.\.|<[^>]+>|\$\{)'
assignment='(password|passwd|token|api_?key|secret_?key|client_secret|access_key|auth)[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9_/+.-]{16,}'
jwt='eyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}'
privkey='-----BEGIN[ A-Z]*PRIVATE KEY-----'
awskey='(AKIA|ASIA)[0-9A-Z]{16}'

hits=0
for f in "${candidates[@]:-}"; do
  [ -f "$f" ] || continue
  # -I skips binaries. Exclude this script, whose own patterns would match.
  [ "$f" = "scripts/validate.sh" ] && continue
  while IFS=: read -r lineno _rest; do
    [ -n "$lineno" ] || continue
    printf '        %s:%s\n' "$f" "$lineno"
    hits=$((hits + 1))
  done < <(grep -InE "$jwt|$privkey|$awskey|$assignment" "$f" 2>/dev/null \
             | grep -ivE "$placeholder" || true)
done

if [ "$hits" -gt 0 ]; then
  fail "$hits line(s) look like a literal credential (locations above; values not printed)"
else
  pass "no credential-shaped literals found"
fi

# ---------------------------------------------------------------------------
head2 "Whitespace errors and conflict markers"

if git diff --check HEAD -- . >/dev/null 2>&1; then
  pass "git diff --check clean"
else
  fail "git diff --check reported problems:"
  git diff --check HEAD -- . 2>&1 | sed 's/^/        /'
fi

conflicts=$(grep -rInE '^(<{7}|={7}|>{7})( |$)' --exclude-dir=.git . 2>/dev/null \
            | grep -v '^\./scripts/validate\.sh:' || true)
if [ -n "$conflicts" ]; then
  fail "unresolved merge conflict markers:"
  printf '%s\n' "$conflicts" | sed 's/^/        /'
else
  pass "no merge conflict markers"
fi

# ---------------------------------------------------------------------------
head2 "Internal documentation links"

broken=0
for f in "${candidates[@]:-}"; do
  case "$f" in *.md) ;; *) continue ;; esac
  [ -f "$f" ] || continue
  # Relative markdown links only: skip http(s), anchors and mailto.
  while read -r target; do
    [ -n "$target" ] || continue
    resolved="$(dirname "$f")/${target%%#*}"
    if [ ! -e "$resolved" ]; then
      printf '        %s -> %s (missing)\n' "$f" "$target"
      broken=$((broken + 1))
    fi
  done < <(grep -oE '\]\([^)#][^)]*\)' "$f" 2>/dev/null \
             | sed -E 's/^\]\(//; s/\)$//' \
             | grep -vE '^(https?:|mailto:|#)' || true)
done

if [ "$broken" -gt 0 ]; then
  fail "$broken broken relative link(s)"
else
  pass "relative documentation links resolve"
fi

# ---------------------------------------------------------------------------
printf '\n'
if [ "$failures" -eq 0 ]; then
  printf '\033[32mAll %d checks passed.\033[0m\n' "$run"
  printf 'Text-level only — validate in Home Assistant before relying on this.\n'
  exit 0
fi
printf '\033[31m%d problem(s) found across %d checks.\033[0m\n' "$failures" "$run"
exit 1
