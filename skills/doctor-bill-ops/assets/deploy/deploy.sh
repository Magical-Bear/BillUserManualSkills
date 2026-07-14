#!/usr/bin/env bash
set -Eeuo pipefail

# GitHub Actions passes values as base64 to avoid remote-shell quoting bugs.
decode_b64_into() {
  local target="$1" encoded_name encoded decoded
  encoded_name="${target}_B64"
  encoded="${!encoded_name:-}"
  if [[ -n "$encoded" ]]; then
    decoded="$(printf '%s' "$encoded" | base64 --decode)"
    export "$target=$decoded"
  fi
}
for variable in APP_DIR SERVICE_MODE SERVICE_NAME HEALTH_URL HEALTH_ATTEMPTS HEALTH_INTERVAL_SECONDS HEALTH_TIMEOUT_SECONDS MIGRATION_COMMAND; do
  decode_b64_into "$variable"
done

: "${APP_DIR:?APP_DIR is required}"
: "${SERVICE_NAME:?SERVICE_NAME is required}"
: "${HEALTH_URL:?HEALTH_URL is required}"

SERVICE_MODE="${SERVICE_MODE:-user}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
HEALTH_ATTEMPTS="${HEALTH_ATTEMPTS:-12}"
HEALTH_INTERVAL_SECONDS="${HEALTH_INTERVAL_SECONDS:-5}"
HEALTH_TIMEOUT_SECONDS="${HEALTH_TIMEOUT_SECONDS:-5}"
MIGRATION_COMMAND="${MIGRATION_COMMAND:-}"

case "$SERVICE_MODE" in
  user) SYSTEMCTL=(systemctl --user); JOURNALCTL=(journalctl --user) ;;
  system) SYSTEMCTL=(sudo -n systemctl); JOURNALCTL=(sudo -n journalctl) ;;
  *) echo "SERVICE_MODE must be user or system" >&2; exit 2 ;;
esac

log() { printf '[doctor-bill-deploy] %s\n' "$*"; }
service_restart() { "${SYSTEMCTL[@]}" restart "$SERVICE_NAME"; }
service_status() { "${SYSTEMCTL[@]}" status "$SERVICE_NAME" --no-pager || true; }
service_logs() { "${JOURNALCTL[@]}" -u "$SERVICE_NAME" -n 200 --no-pager || true; }
sync_dependencies() {
  if [[ -f uv.lock ]]; then
    uv sync --frozen
  elif [[ -f package-lock.json ]]; then
    npm ci
  else
    log "no recognized lock file; dependency synchronization skipped"
  fi
}
health_check() {
  local attempt
  for ((attempt=1; attempt<=HEALTH_ATTEMPTS; attempt++)); do
    if curl --fail --silent --show-error --max-time "$HEALTH_TIMEOUT_SECONDS" "$HEALTH_URL" >/dev/null; then
      log "health check passed on attempt $attempt"
      return 0
    fi
    log "health check failed on attempt $attempt/$HEALTH_ATTEMPTS"
    sleep "$HEALTH_INTERVAL_SECONDS"
  done
  return 1
}

cd "$APP_DIR"
if [[ ! -d .git ]]; then
  echo "APP_DIR is not a Git repository: $APP_DIR" >&2
  exit 1
fi
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Refusing deployment because server worktree is dirty" >&2
  git status --short --branch >&2
  exit 1
fi

current_branch="$(git branch --show-current)"
if [[ "$current_branch" != "$DEPLOY_BRANCH" ]]; then
  echo "Expected branch $DEPLOY_BRANCH, found $current_branch" >&2
  exit 1
fi

previous_commit="$(git rev-parse HEAD)"
rollback_needed=0
rollback() {
  local deploy_exit=$?
  local reset_status=0 dependency_status=0 restart_status=0 health_status=0
  trap - ERR
  set +e

  if [[ "$rollback_needed" -eq 1 ]]; then
    log "deployment failed; collecting status and logs"
    service_status
    service_logs
    if [[ -n "$MIGRATION_COMMAND" ]]; then
      log "WARNING: database migration is not rolled back automatically; verify schema compatibility and recovery state"
    fi

    log "rolling code back to $previous_commit"
    git reset --hard "$previous_commit"
    reset_status=$?
    sync_dependencies
    dependency_status=$?
    service_restart
    restart_status=$?
    health_check
    health_status=$?

    log "rollback result: git_reset=$reset_status dependencies=$dependency_status service_restart=$restart_status health=$health_status"
    if (( reset_status != 0 || dependency_status != 0 || restart_status != 0 || health_status != 0 )); then
      log "CRITICAL: rollback did not fully restore a healthy service; manual intervention is required"
    else
      log "rollback restored commit $previous_commit and the health check passed"
    fi
  fi
  exit "$deploy_exit"
}
trap rollback ERR

log "fetching origin/$DEPLOY_BRANCH"
git fetch --prune origin "$DEPLOY_BRANCH"
git pull --ff-only origin "$DEPLOY_BRANCH"
new_commit="$(git rev-parse HEAD)"
rollback_needed=1
log "updated $previous_commit -> $new_commit"

sync_dependencies

if [[ -n "$MIGRATION_COMMAND" ]]; then
  log "running user-approved migration command"
  bash -lc "$MIGRATION_COMMAND"
else
  log "MIGRATION_COMMAND is empty; migration skipped"
fi

service_restart
service_status
health_check
rollback_needed=0
trap - ERR
log "deployment completed at $new_commit"
