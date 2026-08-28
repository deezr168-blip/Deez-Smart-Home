#!/bin/sh
# deploy_diagnose.sh — read-only diagnosis of why `git fetch` fails when the
# deploy script runs from Home Assistant but succeeds from Studio Code Server.
#
# THE POINT OF THIS SCRIPT IS *WHERE* IT IS RUN. Run it through a Home
# Assistant shell_command, not from the Studio Code Server terminal — the whole
# question is what differs between those two environments, and running it in
# the terminal answers the wrong one. See DEPLOY_AUTH.md.
#
# Read-only: the only network call is `git fetch --dry-run`. Nothing is
# written except the log. Output is sanitized so a token embedded in a remote
# URL is not printed.

LOG="${DEEZ_LOG:-/config/deploy_deez_dashboard.log}"
REPO="${DEEZ_REPO:-}"

exec >>"$LOG" 2>&1

redact() {
    sed -E -e 's#(https?://)[^/@[:space:]]+@#\1REDACTED@#g' \
           -e 's#gh[pousr]_[A-Za-z0-9]+#REDACTED#g' \
           -e 's#github_pat_[A-Za-z0-9_]+#REDACTED#g'
}

echo
echo "================================================================"
echo "deploy_diagnose  $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"

echo "--- 1. execution context ---"
echo "uid/gid    : $(id 2>&1)"
echo "HOME       : ${HOME:-<UNSET>}"
echo "PATH       : ${PATH:-<UNSET>}"
echo "PWD        : $(pwd 2>&1)"
echo "shell      : ${0}"
echo "tty        : $(tty 2>&1)"

echo "--- 2. tooling ---"
echo "git        : $(command -v git 2>&1 || echo '*** NOT ON PATH ***')"
echo "git version: $(git --version 2>&1)"
echo "ssh        : $(command -v ssh 2>&1 || echo 'absent — SSH remotes cannot work here')"

echo "--- 3. repository ---"
if [ -z "$REPO" ]; then
    for c in /config/deez-smart-home /config/Deez-Smart-Home /config/deez_smart_home /config/repo; do
        [ -d "$c/.git" ] && REPO="$c" && break
    done
fi
if [ -z "$REPO" ] || [ ! -d "$REPO/.git" ]; then
    echo "repo       : *** NOT FOUND *** (set DEEZ_REPO to the clone path)"
    echo "verdict    : cannot continue without the clone path"
    exit 1
fi
echo "repo       : $REPO"
echo "owner      : $(ls -ld "$REPO/.git" 2>&1 | awk '{print $3":"$4}')"
echo "remote     :"
git -C "$REPO" remote -v 2>&1 | redact | sed 's/^/             /'
echo "status     :"
git -C "$REPO" status --short --branch 2>&1 | redact | sed 's/^/             /'

echo "--- 4. effective git config (origin-annotated) ---"
git -C "$REPO" config --list --show-origin 2>&1 \
    | grep -Ei 'safe\.directory|credential|url\.|http\.|core\.sshcommand|user\.' \
    | redact | sed 's/^/             /' || echo "             (none relevant)"

echo "--- 5. credential material visible from HERE ---"
for f in /config/.deez_deploy.env /config/deploy_askpass.sh /config/.deez_gitconfig \
         "$HOME/.gitconfig" "$HOME/.git-credentials" "$HOME/.ssh/id_ed25519" \
         /config/.ssh/deez_deploy_ed25519; do
    if [ -e "$f" ]; then
        echo "  present  $(ls -ld "$f" 2>&1 | awk '{print $1, $3":"$4, $NF}')"
    else
        echo "  absent   $f"
    fi
done
echo "  GIT_ASKPASS         : ${GIT_ASKPASS:-<unset>}"
echo "  GIT_SSH_COMMAND     : ${GIT_SSH_COMMAND:-<unset>}"
echo "  GIT_TERMINAL_PROMPT : ${GIT_TERMINAL_PROMPT:-<unset>}"
echo "  DEEZ_GH_TOKEN       : $([ -n "${DEEZ_GH_TOKEN:-}" ] && echo 'set (value not printed)' || echo '<unset>')"

echo "--- 6. network reachability ---"
echo "  DNS github.com : $(getent hosts github.com 2>&1 | head -1 || echo 'FAILED — no resolution')"

echo "--- 7. THE ACTUAL FETCH (dry run, full stderr) ---"
GIT_TERMINAL_PROMPT=0 git -C "$REPO" fetch --dry-run --verbose origin ha-deploy 2>&1 | redact | sed 's/^/             /'
rc=$?
echo "  git fetch exit code: $rc"

echo "--- 8. verdict ---"
if [ "$rc" -eq 0 ]; then
    echo "  FETCH SUCCEEDED from this execution context."
else
    echo "  FETCH FAILED (exit $rc). Match the stderr in section 7 against:"
    echo "    'could not read Username' / 'terminal prompts disabled'"
    echo "        -> no credential in THIS container. Section 5 will show the"
    echo "           credential files exist only under a HOME this process"
    echo "           cannot see. Fix: /config/.deez_deploy.env + deploy_env.sh."
    echo "    'Authentication failed' / 403"
    echo "        -> a credential was offered and rejected: token expired,"
    echo "           revoked, or lacks Contents:Read on this repository."
    echo "    'detected dubious ownership'"
    echo "        -> uid mismatch between the cloning and fetching containers."
    echo "           Fix: safe.directory, set by deploy_env.sh."
    echo "    'git: not found' / exit 127"
    echo "        -> PATH, not authentication. Fix: PATH, set by deploy_env.sh."
    echo "    'Could not resolve host' / TLS error"
    echo "        -> networking or CA bundle in the HA container, not auth."
fi
echo "================================================================"
exit "$rc"
