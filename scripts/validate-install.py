#!/usr/bin/env python3
"""Validate installed Doctor Bill Skills and user-level entry files."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ["doctor-bill", "doctor-bill-software", "doctor-bill-hardware", "doctor-bill-ai", "doctor-bill-ops"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_skill_set(skills_dir: Path, errors: list[str]) -> None:
    for name in SKILLS:
        target = skills_dir / name / "SKILL.md"
        source = ROOT / "SKILL.md" if name == "doctor-bill" else ROOT / "skills" / name / "SKILL.md"
        if not target.is_file():
            errors.append(f"missing installed Skill: {target}")
            continue
        if digest(target) != digest(source):
            errors.append(f"installed Skill differs from source: {target}")
        yaml = skills_dir / name / "agents" / "openai.yaml"
        if not yaml.is_file():
            errors.append(f"missing installed metadata: {yaml}")
        for forbidden in ["work.md", "references", "agents/developer.md", "agents/tester.md"]:
            if (skills_dir / name / forbidden).exists():
                errors.append(f"fragmented rule artifact installed: {skills_dir / name / forbidden}")
    root_persona = skills_dir / "doctor-bill" / "persona.md"
    if not root_persona.is_file():
        errors.append(f"missing preserved persona: {root_persona}")
    for relative in [
        "assets/systemd/doctor-bill-system.service",
        "assets/systemd/doctor-bill-user.service",
        "assets/github/deploy-main.yml",
        "assets/deploy/deploy.sh",
    ]:
        path = skills_dir / "doctor-bill-ops" / relative
        if not path.is_file():
            errors.append(f"missing installed ops asset: {path}")


def check_marked_file(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"missing entry file: {path}")
        return
    text = path.read_text(encoding="utf-8")
    if text.count("<!-- DOCTOR-BILL:BEGIN -->") != 1 or text.count("<!-- DOCTOR-BILL:END -->") != 1:
        errors.append(f"invalid Doctor Bill marked block: {path}")
    for term in ["super_bill", "superpowers", "Context7", "ui-ux-pro-max-skill", "开发 Agent", "测试 Agent"]:
        if term not in text:
            errors.append(f"{path}: missing entry requirement {term!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Doctor Bill installed artifacts")
    parser.add_argument("--platform", choices=["codex", "claude", "cursor", "all"], default="all")
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--claude-home", type=Path, default=Path.home() / ".claude")
    parser.add_argument("--cursor-home", type=Path, default=Path.home() / ".cursor")
    parser.add_argument("--cursor-rules-dir", type=Path, default=None)
    parser.add_argument("--cursor-skills-dir", type=Path, default=None)
    args = parser.parse_args()

    errors: list[str] = []
    if args.platform in {"codex", "all"}:
        check_skill_set(args.codex_home.expanduser() / "skills", errors)
        check_marked_file(args.codex_home.expanduser() / "AGENTS.md", errors)
    if args.platform in {"claude", "all"}:
        check_skill_set(args.claude_home.expanduser() / "skills", errors)
        check_marked_file(args.claude_home.expanduser() / "CLAUDE.md", errors)
    if args.platform in {"cursor", "all"}:
        cursor_home = args.cursor_home.expanduser()
        rules_dir = (args.cursor_rules_dir or cursor_home / "rules").expanduser()
        skills_dir = (args.cursor_skills_dir or cursor_home / "skills").expanduser()
        check_skill_set(skills_dir, errors)
        mdc = rules_dir / "doctor-bill.mdc"
        check_marked_file(mdc, errors)
        if mdc.is_file() and not re.search(r"^alwaysApply:\s*true\s*$", mdc.read_text(encoding="utf-8"), re.M):
            errors.append(f"{mdc}: expected alwaysApply: true")

    if errors:
        print("Doctor Bill install validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Doctor Bill install validation passed: all five Skills and user-level entries match source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
