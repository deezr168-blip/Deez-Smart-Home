#!/bin/sh
# deploy_askpass.sh — GIT_ASKPASS helper. Install at /config/deploy_askpass.sh,
# chmod 700. Contains NO secret: it echoes a value held in the environment,
# which deploy_env.sh loads from /config/.deez_deploy.env at runtime.
case "$1" in
    Username*) printf '%s\n' 'x-access-token' ;;
    Password*) printf '%s\n' "${DEEZ_GH_TOKEN}" ;;
    *)         printf '\n' ;;
esac
