#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLATFORM="all"
DRY_RUN=0
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
CURSOR_RULES_DIR="${CURSOR_RULES_DIR:-}"
BACKUP_SUFFIX="doctor-bill-backup-$(date +%Y%m%d%H%M%S)"
SKILLS=(doctor-bill doctor-bill-software doctor-bill-hardware doctor-bill-ai doctor-bill-ops)

usage() {
  cat <<USAGE
Doctor Bill installer

Usage:
  scripts/install.sh [options]

Options:
  --platform codex|claude|cursor|all   Target platform. Default: all
  --codex-home PATH                    Override Codex home. Default: ~/.codex
  --claude-home PATH                   Override Claude home. Default: ~/.claude
  --cursor-rules-dir PATH              Cursor rules directory. Required if default is absent
  --dry-run                            Print actions without writing
  -h, --help                           Show help

Notes:
  - Existing skill directories are backed up before replacement.
  - User entry files are updated inside <!-- DOCTOR-BILL:BEGIN --> blocks.
  - Cursor user-level rules path is product/version dependent; pass --cursor-rules-dir after verifying your Cursor setup.
USAGE
}

log() { printf '%s\n' "$*"; }
run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    printf '[dry-run] %q' "$1"
    shift || true
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
    --cursor-rules-dir) CURSOR_RULES_DIR="${2:?missing path}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

case "$PLATFORM" in codex|claude|cursor|all) ;; *) echo "Invalid platform: $PLATFORM" >&2; exit 2 ;; esac

backup_path() {
  local path="$1"
  [[ -e "$path" ]] || return 0
  local backup="${path}.${BACKUP_SUFFIX}"
  log "Backup: $path -> $backup"
  run mv "$path" "$backup"
}

copy_dir() {
  local src="$1" dest="$2"
  backup_path "$dest"
  run mkdir -p "$(dirname "$dest")"
  run cp -R "$src" "$dest"
}

install_root_skill() {
  local dest="$1"
  local tmp
  tmp="$(mktemp -d)"
  mkdir -p "$tmp/doctor-bill"
  cp "$ROOT_DIR/SKILL.md" "$ROOT_DIR/persona.md" "$ROOT_DIR/work.md" "$ROOT_DIR/README.md" "$ROOT_DIR/meta.json" "$tmp/doctor-bill/"
  cp -R "$ROOT_DIR/agents" "$ROOT_DIR/references" "$tmp/doctor-bill/"
  copy_dir "$tmp/doctor-bill" "$dest/doctor-bill"
  rm -rf "$tmp"
}

install_skill_set() {
  local skills_dir="$1"
  run mkdir -p "$skills_dir"
  install_root_skill "$skills_dir"
  for skill in doctor-bill-software doctor-bill-hardware doctor-bill-ai doctor-bill-ops; do
    copy_dir "$ROOT_DIR/skills/$skill" "$skills_dir/$skill"
  done
}

update_marked_block() {
  local src="$1" target="$2"
  run mkdir -p "$(dirname "$target")"
  if [[ -e "$target" ]]; then
    local backup="${target}.${BACKUP_SUFFIX}"
    log "Backup: $target -> $backup"
    run cp "$target" "$backup"
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    log "[dry-run] update DOCTOR-BILL block in $target from $src"
    return 0
  fi
  python3 - "$src" "$target" <<'PY'
from pathlib import Path
import re
import sys
src = Path(sys.argv[1])
target = Path(sys.argv[2])
block = src.read_text(encoding='utf-8').strip() + '\n'
old = target.read_text(encoding='utf-8') if target.exists() else ''
pattern = re.compile(r'<!-- DOCTOR-BILL:BEGIN -->.*?<!-- DOCTOR-BILL:END -->\n?', re.S)
if pattern.search(old):
    new = pattern.sub(block, old)
else:
    sep = '' if not old or old.endswith('\n') else '\n'
    new = old + sep + block

target.write_text(new, encoding='utf-8')
PY
}

install_codex() {
  log "Installing Codex skills to $CODEX_HOME/skills"
  install_skill_set "$CODEX_HOME/skills"
  update_marked_block "$ROOT_DIR/adapters/codex/AGENTS.md" "$CODEX_HOME/AGENTS.md"
}

install_claude() {
  log "Installing Claude skills to $CLAUDE_HOME/skills"
  install_skill_set "$CLAUDE_HOME/skills"
  update_marked_block "$ROOT_DIR/adapters/claude/CLAUDE.md" "$CLAUDE_HOME/CLAUDE.md"
}

install_cursor() {
  if [[ -z "$CURSOR_RULES_DIR" ]]; then
    if [[ -d "$HOME/.cursor/rules" ]]; then
      CURSOR_RULES_DIR="$HOME/.cursor/rules"
      log "Using existing Cursor rules dir: $CURSOR_RULES_DIR"
    else
      log "Cursor rules dir not known. Pass --cursor-rules-dir after verifying your Cursor user rules path. Skipping Cursor."
      return 0
    fi
  fi
  log "Installing Cursor rules to $CURSOR_RULES_DIR"
  run mkdir -p "$CURSOR_RULES_DIR"
  for file in "$ROOT_DIR"/adapters/cursor/*.mdc; do
    local dest="$CURSOR_RULES_DIR/$(basename "$file")"
    backup_path "$dest"
    run cp "$file" "$dest"
  done
}

if [[ "$PLATFORM" == "codex" || "$PLATFORM" == "all" ]]; then install_codex; fi
if [[ "$PLATFORM" == "claude" || "$PLATFORM" == "all" ]]; then install_claude; fi
if [[ "$PLATFORM" == "cursor" || "$PLATFORM" == "all" ]]; then install_cursor; fi

log "Doctor Bill install complete. Run scripts/validate-install.py with matching paths to verify artifacts."
