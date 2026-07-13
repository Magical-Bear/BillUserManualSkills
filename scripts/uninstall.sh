#!/usr/bin/env bash
set -euo pipefail

PLATFORM="all"
DRY_RUN=0
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
CURSOR_HOME="${CURSOR_HOME:-$HOME/.cursor}"
CURSOR_RULES_DIR="${CURSOR_RULES_DIR:-}"
CURSOR_SKILLS_DIR="${CURSOR_SKILLS_DIR:-}"
BACKUP_SUFFIX="doctor-bill-uninstall-$(date +%Y%m%d%H%M%S)"
SKILLS=(doctor-bill doctor-bill-software doctor-bill-hardware doctor-bill-ai doctor-bill-ops)

usage() {
  cat <<USAGE
Doctor Bill uninstaller

Usage: scripts/uninstall.sh [options]

Options:
  --platform codex|claude|cursor|all
  --codex-home PATH
  --claude-home PATH
  --cursor-home PATH
  --cursor-rules-dir PATH
  --cursor-skills-dir PATH
  --dry-run
  -h, --help

Uninstall moves installed Skill directories/rules to timestamped backups and
removes the marked Doctor Bill block from AGENTS.md or CLAUDE.md.
USAGE
}

log() { printf '%s\n' "$*"; }
run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    printf '[dry-run] %q' "$1"; shift || true
    for arg in "$@"; do printf ' %q' "$arg"; done
    printf '\n'
  else
    "$@"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform) PLATFORM="${2:?missing platform}"; shift 2 ;;
    --codex-home) CODEX_HOME="${2:?missing path}"; shift 2 ;;
    --claude-home) CLAUDE_HOME="${2:?missing path}"; shift 2 ;;
    --cursor-home) CURSOR_HOME="${2:?missing path}"; shift 2 ;;
    --cursor-rules-dir) CURSOR_RULES_DIR="${2:?missing path}"; shift 2 ;;
    --cursor-skills-dir) CURSOR_SKILLS_DIR="${2:?missing path}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done
case "$PLATFORM" in codex|claude|cursor|all) ;; *) echo "Invalid platform: $PLATFORM" >&2; exit 2 ;; esac
CURSOR_RULES_DIR="${CURSOR_RULES_DIR:-$CURSOR_HOME/rules}"
CURSOR_SKILLS_DIR="${CURSOR_SKILLS_DIR:-$CURSOR_HOME/skills}"

move_to_backup() {
  local path="$1"
  [[ -e "$path" ]] || return 0
  local backup="${path}.${BACKUP_SUFFIX}"
  log "Move to backup: $path -> $backup"
  run mv "$path" "$backup"
}

remove_marked_block() {
  local target="$1"
  [[ -e "$target" ]] || return 0
  local backup="${target}.${BACKUP_SUFFIX}"
  log "Backup: $target -> $backup"
  run cp "$target" "$backup"
  if [[ "$DRY_RUN" == "1" ]]; then return 0; fi
  python3 - "$target" <<'PY'
from pathlib import Path
import re
import sys
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = re.sub(r"<!-- DOCTOR-BILL:BEGIN -->.*?<!-- DOCTOR-BILL:END -->\n?", "", text, flags=re.S)
path.write_text(text, encoding="utf-8")
PY
}

uninstall_skill_set() {
  local skills_dir="$1" skill
  for skill in "${SKILLS[@]}"; do move_to_backup "$skills_dir/$skill"; done
}

uninstall_codex() { uninstall_skill_set "$CODEX_HOME/skills"; remove_marked_block "$CODEX_HOME/AGENTS.md"; }
uninstall_claude() { uninstall_skill_set "$CLAUDE_HOME/skills"; remove_marked_block "$CLAUDE_HOME/CLAUDE.md"; }
uninstall_cursor() { uninstall_skill_set "$CURSOR_SKILLS_DIR"; move_to_backup "$CURSOR_RULES_DIR/doctor-bill.mdc"; }

if [[ "$PLATFORM" == "codex" || "$PLATFORM" == "all" ]]; then uninstall_codex; fi
if [[ "$PLATFORM" == "claude" || "$PLATFORM" == "all" ]]; then uninstall_claude; fi
if [[ "$PLATFORM" == "cursor" || "$PLATFORM" == "all" ]]; then uninstall_cursor; fi
log "Doctor Bill uninstall complete. Backups kept with suffix $BACKUP_SUFFIX."
