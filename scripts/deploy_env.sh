#!/bin/sh
# deploy_env.sh — execution-environment and credential preamble for
# /config/deploy_deez_dashboard.sh
#
# Install at /config/deploy_env.sh and source it from the FIRST lines of the
# deploy script:
#
#     . /config/deploy_env.sh
#
# Why this exists
# ---------------
# Studio Code Server and Home Assistant Core are SEPARATE CONTAINERS. They
# share /config and nothing else. Git credentials, ~/.gitconfig and ~/.ssh set
# up in the Studio Code Server terminal live in that container's filesystem and
# are invisible to the Home Assistant process that runs shell_command. A manual
# deploy therefore authenticates and a scheduled one does not.
#
# Everything this file configures is anchored under /config, which both
# containers can see, so the scheduled and manual paths behave identically.
#
# NO SECRET IS STORED IN THIS FILE. The token is read at runtime from
# /config/.deez_deploy.env (mode 600, not in the repository).

# --- 1. Deterministic PATH -------------------------------------------------
# shell_command inherits Home Assistant's environment, not a login shell's.
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PATH

# --- 2. HOME must exist ----------------------------------------------------
# Git reads ~/.gitconfig and the credential store relative to HOME. If HOME is
# unset git silently loses all user configuration.
[ -n "${HOME:-}" ] || HOME=/root
export HOME

# --- 3. Git config that both containers can see ----------------------------
# GIT_CONFIG_GLOBAL (git >= 2.32) pins the global config to a shared file, so
# the scheduled run reads the same settings as a manual one.
DEEZ_GITCONFIG=/config/.deez_gitconfig
if [ ! -f "$DEEZ_GITCONFIG" ]; then
    : > "$DEEZ_GITCONFIG"
    chmod 600 "$DEEZ_GITCONFIG" 2>/dev/null || true
fi
GIT_CONFIG_GLOBAL="$DEEZ_GITCONFIG"
export GIT_CONFIG_GLOBAL

# safe.directory: git >= 2.35.2 refuses to operate on a repository owned by a
# different uid ("detected dubious ownership"), which is exactly what happens
# when one container clones and another fetches. Any git new enough to enforce
# that rule also honours GIT_CONFIG_GLOBAL, so setting it here is sufficient.
if ! git config --global --get-all safe.directory 2>/dev/null | grep -qx '\*'; then
    git config --global --add safe.directory '*' 2>/dev/null || true
fi

# --- 4. Never hang on a credential prompt ----------------------------------
# Without this a missing credential makes git block on a tty that does not
# exist. Home Assistant kills shell_command at 60s and reports a generic
# failure, which hides the real cause. With it, git fails immediately and says
# why.
GIT_TERMINAL_PROMPT=0
export GIT_TERMINAL_PROMPT

# --- 5. Credentials --------------------------------------------------------
# Preferred: HTTPS + a fine-grained token supplied through GIT_ASKPASS, so the
# token never enters the remote URL, .git/config, the reflog, the process
# argument list, or this repository.
if [ -r /config/.deez_deploy.env ]; then
    # shellcheck disable=SC1091
    . /config/.deez_deploy.env
fi
if [ -n "${DEEZ_GH_TOKEN:-}" ] && [ -x /config/deploy_askpass.sh ]; then
    export DEEZ_GH_TOKEN
    GIT_ASKPASS=/config/deploy_askpass.sh
    export GIT_ASKPASS
fi

# Alternative: a read-only SSH deploy key, if the remote is an SSH URL and the
# Home Assistant container actually ships an ssh client (check: command -v ssh).
if [ -r /config/.ssh/deez_deploy_ed25519 ]; then
    GIT_SSH_COMMAND="ssh -i /config/.ssh/deez_deploy_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes -o UserKnownHostsFile=/config/.ssh/known_hosts -o StrictHostKeyChecking=yes"
    export GIT_SSH_COMMAND
fi
