# Automated CasaRay deployment without SSH: plan

Status: proposal. Nothing here is installed yet.

## The constraint

GitHub cannot reach the Green. It sits on the home LAN and has no public SSH,
and should not get any. So every workable design has something **inside the
LAN that reaches out**: it polls or long-polls GitHub, and nothing listens for
inbound connections.

## Option 1 (recommended): self-hosted GitHub Actions runner on a small LAN box

- **Hardware.** Any always-on Linux machine on the LAN: a Raspberry Pi 4/5,
  an old mini PC, or a NAS that can run Docker. Not the Green itself: Home
  Assistant OS does not support running an Actions runner, and a runner with
  write access to `/config` inside the Green is a large attack surface.
- **Connection.** The runner opens an outbound HTTPS long-poll to GitHub. No
  ports are opened and no public SSH is needed.
- **How it deploys.** Both paths already exist and need no new privileges:
  - **Files:** writes into Home Assistant's `/config` over the **Samba
    add-on share**, the same access Owlfiles uses. The share is mounted
    read-write for one service account.
  - **Home Assistant actions:** calls Home Assistant's REST API on the LAN
    (`http://homeassistant.local:8123/api/...`) with a **dedicated
    non-owner admin user's long-lived token**. That user exists only for
    deployment and can be revoked alone. The token is stored as a **GitHub
    environment secret** on a `production` environment.
- **The pipeline** reuses the existing scripts:
  1. On a PR into `ha-deploy`: `scripts/ha_validate.sh` and
     `dashboard_check.py` run on GitHub-hosted runners. No secrets are
     involved and nothing touches the home.
  2. On merge: a job on the **self-hosted** runner, in the `production`
     environment (which requires the owner's approval for restart-class
     changes):
     - take a backup via the REST API (`hassio/backup/new` service), then
       confirm it appears in the backup list
     - copy `dashboards/casaray_v2.yaml` and the theme over Samba, keeping
       timestamped `.bak` copies (the same rules as
       `sync_casaray_to_config.sh`)
     - call `homeassistant.check_config` and read the result
     - restart only if a registration or `configuration.yaml` change needs
       it (and the environment approval granted it); otherwise the browser
       just refreshes
  3. **Health check:** poll `/api/` and the key entities
     (`input_boolean.chinese_dashboard`, `person.*`, a CasaRay-critical
     sensor). If one fails, restore the `.bak` copies, and on a config
     change restore the pre-deploy `configuration.yaml` and restart.
  4. **Change tracking:** tag each deploy `deploy-YYYYMMDD-HHMM` with the
     commit SHA. Rollback means "deploy the previous tag" through the same
     job.
- **Runner hardening:**
  - enable only for this private repository, and require approval for
    workflow runs from forks
  - use ephemeral jobs (`--ephemeral`) and a dedicated unprivileged OS
    user; that user owns the Samba credentials and nothing else
  - keep the runner software on auto-update

## Option 2 (no new hardware): pull from the Green itself

- A Home Assistant automation on a schedule, or on a webhook trigger reached
  through Home Assistant Cloud, runs a `shell_command` that calls the
  existing `casaray_safe_deploy.sh`. That script already does fetch →
  validate → backup → deploy → verify → rollback.
- GitHub only needs to notify: a workflow on merge posts to the webhook, with
  a random webhook ID stored as a GitHub secret. Home Assistant pulls; GitHub
  never pushes files.
- **Weaknesses:**
  - the deploy logic runs inside Home Assistant's `shell_command`, which
    has a 60-second timeout and no interactive approval
  - a bad deploy of the deployment config itself can disable the mechanism
  - fine for dashboard-file updates; not suitable for
    `configuration.yaml` changes that need a restart

## Two-agent review (Claude develops, Codex reviews)

- Branch protection on `ha-deploy` requires:
  - one approving review from the **Codex reviewer's** GitHub identity,
    under a separate account or app, with its own review instructions
  - passing `ha_validate.sh` and `dashboard_check.py` checks
  - linear history
- "Dismiss stale approvals on new commits" is on, so a review can never cover
  code it did not see.
- Neither agent can approve its own PR: Claude's identity is the author, and
  Codex's is the only one allowed to approve. Merges into `production` still
  need the owner's environment approval whenever the change touches
  `configuration.yaml` or needs a restart.
- The PR template requires Claude to fill in **what was verified live and
  what was not**. Codex is instructed to reject any PR that claims live
  verification without evidence: a screenshot, or states read from the API.

## First steps when the owner chooses Option 1

1. Pick the box and install the Actions runner as a service
   (`svc.sh install`).
2. In Home Assistant, create the `deploy-bot` admin user and its long-lived
   token, and store the token as a GitHub environment secret. This is an
   owner action; credentials never go through Claude.
3. Add the Samba credentials as a second environment secret.
4. Merge the workflow file. The first run executes in a dry-run mode that
   only reads.
