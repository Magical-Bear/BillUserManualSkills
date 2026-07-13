#!/usr/bin/env python3
"""Validate Doctor Bill user-level installation artifacts.

This checks installed files under Codex/Claude/Cursor user paths. It does not
exercise runtime agent behavior and is not a replacement for independent tests.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

SKILLS = [
    "doctor-bill",
    "doctor-bill-software",
    "doctor-bill-hardware",
    "doctor-bill-ai",
    "doctor-bill-ops",
]

BLOCK_BEGIN = "<!-- DOCTOR-BILL:BEGIN -->"
BLOCK_END = "<!-- DOCTOR-BILL:END -->"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter_name(path: Path) -> Optional[str]:
    text = read_text(path)
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    raw = text[4:end]
    for line in raw.splitlines():
        if line.strip().startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return None


def check_skill_dir(skills_dir: Path, errors: list[str]) -> None:
    for skill in SKILLS:
        base = skills_dir / skill
        if not base.is_dir():
            errors.append(f"missing installed skill directory: {base}")
            continue
        skill_md = base / "SKILL.md"
        openai = base / "agents/openai.yaml"
        if not skill_md.exists():
            errors.append(f"missing installed SKILL.md: {skill_md}")
        elif frontmatter_name(skill_md) != skill:
            errors.append(f"{skill_md}: frontmatter name mismatch, expected {skill}")
        if not openai.exists():
            errors.append(f"missing installed openai.yaml: {openai}")
        else:
            text = read_text(openai)
            if f"${skill}" not in text:
                errors.append(f"{openai}: default prompt must mention ${skill}")

    root_skill = skills_dir / "doctor-bill"
    for rel in ["persona.md", "work.md", "agents/developer.md", "agents/tester.md", "references/skill-routing.md"]:
        if not (root_skill / rel).exists():
            errors.append(f"missing root skill artifact: {root_skill / rel}")


def check_marked_file(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing adapter entry: {path}")
        return
    text = read_text(path)
    if BLOCK_BEGIN not in text or BLOCK_END not in text:
        errors.append(f"{path}: missing DOCTOR-BILL marked block")
    if "doctor-bill" not in text or "super_bill" not in text:
        errors.append(f"{path}: missing doctor-bill/super_bill routing text")


def validate_codex(home: Path, errors: list[str]) -> None:
    check_skill_dir(home / "skills", errors)
    check_marked_file(home / "AGENTS.md", errors)


def validate_claude(home: Path, errors: list[str]) -> None:
    check_skill_dir(home / "skills", errors)
    check_marked_file(home / "CLAUDE.md", errors)


def validate_cursor(rules_dir: Path, errors: list[str]) -> None:
    if not rules_dir.exists():
        errors.append(f"Cursor rules dir does not exist: {rules_dir}")
        return
    target = rules_dir / "doctor-bill.mdc"
    check_marked_file(target, errors)
    if target.exists():
        text = read_text(target)
        if not re.search(r"^alwaysApply:\s*true\s*$", text, re.M):
            errors.append(f"{target}: expected alwaysApply: true")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Doctor Bill installed artifacts")
    parser.add_argument("--platform", choices=["codex", "claude", "cursor", "all"], default="all")
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--claude-home", type=Path, default=Path.home() / ".claude")
    parser.add_argument("--cursor-rules-dir", type=Path, default=None)
    args = parser.parse_args()

    errors: list[str] = []
    if args.platform in {"codex", "all"}:
        validate_codex(args.codex_home.expanduser(), errors)
    if args.platform in {"claude", "all"}:
        validate_claude(args.claude_home.expanduser(), errors)
    if args.platform in {"cursor", "all"}:
        cursor_dir = args.cursor_rules_dir or (Path.home() / ".cursor/rules")
        validate_cursor(cursor_dir.expanduser(), errors)

    if errors:
        print("Doctor Bill install validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Doctor Bill install validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
