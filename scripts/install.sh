#!/usr/bin/env bash
set -euo pipefail

PLATFORM="all"
DRY_RUN=0
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
CURSOR_HOME="${CURSOR_HOME:-$HOME/.cursor}"
CURSOR_RULES_DIR="${CURSOR_RULES_DIR:-}"
CURSOR_SKILLS_DIR="${CURSOR_SKILLS_DIR:-}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_TAG="doctor-bill-backup"
SKILLS=(doctor-bill doctor-bill-software doctor-bill-hardware doctor-bill-ai doctor-bill-ops)

usage() {
  cat <<USAGE
Doctor Bill installer

Usage:
  scripts/install.sh [options]

Options:
  --platform codex|claude|cursor|all   Target platform. Default: all
  --codex-home PATH                    Default: ~/.codex
  --claude-home PATH                   Default: ~/.claude
  --cursor-home PATH                   Default: ~/.cursor
  --cursor-rules-dir PATH              Default: <cursor-home>/rules
  --cursor-skills-dir PATH             Default: <cursor-home>/skills
  --dry-run
  -h, --help

The installer installs the complete five-Skill set for every selected platform.
It updates user-level AGENTS.md/CLAUDE.md or installs the Cursor MDC entry.
Verify Cursor's actual user rules and Skills directories for the installed version;
use the override options when they differ from the defaults.
USAGE
}

log() { printf '%s\n' "$*"; }
unique_backup_path() {
  local path="$1" stamp candidate counter=0
  stamp="$(date +%Y%m%d%H%M%S)-$$"
  candidate="${path}.${BACKUP_TAG}-${stamp}"
  while [[ -e "$candidate" ]]; do
    counter=$((counter + 1))
    candidate="${path}.${BACKUP_TAG}-${stamp}-${counter}"
  done
  printf '%s\n' "$candidate"
}
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

copy_dir_with_backup() {
  local src="$1" dest="$2"
  if [[ -e "$dest" ]]; then
    local backup
    backup="$(unique_backup_path "$dest")"
    log "Backup: $dest -> $backup"
    run mv "$dest" "$backup"
  fi
  run mkdir -p "$(dirname "$dest")"
  run cp -R "$src" "$dest"
}

install_root_skill() {
  local skills_dir="$1"
  local tmp
  tmp="$(mktemp -d)"
  mkdir -p "$tmp/doctor-bill/agents"
  cp "$ROOT_DIR/SKILL.md" "$tmp/doctor-bill/SKILL.md"
  cp "$ROOT_DIR/agents/openai.yaml" "$tmp/doctor-bill/agents/openai.yaml"
  copy_dir_with_backup "$tmp/doctor-bill" "$skills_dir/doctor-bill"
  rm -rf "$tmp"
}

install_skill_set() {
  local skills_dir="$1"
  run mkdir -p "$skills_dir"
  install_root_skill "$skills_dir"
  local skill
  for skill in doctor-bill-software doctor-bill-hardware doctor-bill-ai doctor-bill-ops; do
    copy_dir_with_backup "$ROOT_DIR/skills/$skill" "$skills_dir/$skill"
  done
}

update_marked_block() {
  local source="$1" target="$2"
  local begin='<!-- DOCTOR-BILL:BEGIN -->'
  local end='<!-- DOCTOR-BILL:END -->'
  run mkdir -p "$(dirname "$target")"
  if [[ -e "$target" ]]; then
    local backup
    backup="$(unique_backup_path "$target")"
    log "Backup: $target -> $backup"
    run cp "$target" "$backup"
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    log "[dry-run] update Doctor Bill marked block in $target from $source"
    return 0
  fi
  python3 - "$source" "$target" "$begin" "$end" <<'PY'
from pathlib import Path
import re
import sys
source = Path(sys.argv[1])
target = Path(sys.argv[2])
begin = sys.argv[3]
end = sys.argv[4]
block = source.read_text(encoding="utf-8").strip() + "\n"
text = target.read_text(encoding="utf-8") if target.exists() else ""
pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end) + r"\n?", re.S)
if pattern.search(text):
    text = pattern.sub(block, text)
else:
    if text and not text.endswith("\n"):
        text += "\n"
    if text.strip():
        text += "\n"
    text += block
target.write_text(text, encoding="utf-8")
PY
}

install_codex() {
  log "Installing Codex Skills to $CODEX_HOME/skills"
  install_skill_set "$CODEX_HOME/skills"
  update_marked_block "$ROOT_DIR/adapters/codex/AGENTS.md" "$CODEX_HOME/AGENTS.md"
}

install_claude() {
  log "Installing Claude Code Skills to $CLAUDE_HOME/skills"
  install_skill_set "$CLAUDE_HOME/skills"
  update_marked_block "$ROOT_DIR/adapters/claude/CLAUDE.md" "$CLAUDE_HOME/CLAUDE.md"
}

install_cursor() {
  log "Installing Cursor Skills to $CURSOR_SKILLS_DIR"
  install_skill_set "$CURSOR_SKILLS_DIR"
  run mkdir -p "$CURSOR_RULES_DIR"
  local target="$CURSOR_RULES_DIR/doctor-bill.mdc"
  if [[ -e "$target" ]]; then
    local backup
    backup="$(unique_backup_path "$target")"
    log "Backup: $target -> $backup"
    run mv "$target" "$backup"
  fi
  run cp "$ROOT_DIR/adapters/cursor/doctor-bill.mdc" "$target"
}

if [[ "$PLATFORM" == "codex" || "$PLATFORM" == "all" ]]; then install_codex; fi
if [[ "$PLATFORM" == "claude" || "$PLATFORM" == "all" ]]; then install_claude; fi
if [[ "$PLATFORM" == "cursor" || "$PLATFORM" == "all" ]]; then install_cursor; fi

log "Doctor Bill install complete. Validate with scripts/validate-install.py using the same paths."
