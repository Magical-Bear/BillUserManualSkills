#!/usr/bin/env python3
"""Validate Doctor Bill skill source tree.

This is a source-structure validator, not an independent functional test.
It checks skill metadata, required files, adapter templates, and shallow references.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

EXPECTED_SKILLS = {
    ".": "doctor-bill",
    "skills/doctor-bill-software": "doctor-bill-software",
    "skills/doctor-bill-hardware": "doctor-bill-hardware",
    "skills/doctor-bill-ai": "doctor-bill-ai",
    "skills/doctor-bill-ops": "doctor-bill-ops",
}

ROOT_REQUIRED = [
    "SKILL.md",
    "persona.md",
    "work.md",
    "README.md",
    "meta.json",
    "agents/openai.yaml",
    "agents/developer.md",
    "agents/tester.md",
    "references/skill-routing.md",
    "references/legacy-work-knowledge.md",
    "adapters/codex/AGENTS.md",
    "adapters/claude/CLAUDE.md",
    "adapters/cursor/doctor-bill.mdc",
    "scripts/install.sh",
    "scripts/uninstall.sh",
    "scripts/validate-skills.py",
    "scripts/validate-install.py",
]

DOMAIN_REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
]

REQUIRED_OPENAI_FIELDS = ["display_name", "short_description", "default_prompt"]
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
MAX_SKILL_NAME_LENGTH = 64
BLOCK_BEGIN = "<!-- DOCTOR-BILL:BEGIN -->"
BLOCK_END = "<!-- DOCTOR-BILL:END -->"


class ValidationError(Exception):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"{path}: not valid UTF-8") from exc


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = read_text(path)
    if not text.startswith("---\n"):
        raise ValidationError(f"{path}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValidationError(f"{path}: frontmatter is not closed")
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            raise ValidationError(f"{path}: invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        data[key.strip()] = value
    return data, body


def parse_simple_openai_yaml(path: Path) -> dict[str, str]:
    text = read_text(path)
    fields: dict[str, str] = {}
    for field in REQUIRED_OPENAI_FIELDS:
        match = re.search(rf"^\s+{re.escape(field)}:\s*[\"'](.*?)[\"']\s*$", text, re.M)
        if not match:
            match = re.search(rf"^\s+{re.escape(field)}:\s*(.*?)\s*$", text, re.M)
        if match:
            fields[field] = match.group(1).strip()
    return fields


def iter_md_links(text: str) -> Iterable[str]:
    # Markdown inline links only. We intentionally ignore URLs and code blocks loosely.
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip()
        if not target or "://" in target or target.startswith("#"):
            continue
        yield target.split("#", 1)[0]


def check_exists(root: Path, relative: str, errors: list[str]) -> None:
    path = root / relative
    if not path.exists():
        errors.append(f"missing required file: {relative}")


def check_reference_depth(skill_dir: Path, errors: list[str]) -> None:
    references = skill_dir / "references"
    if not references.exists():
        return
    for path in references.rglob("*"):
        if path.is_file():
            rel = path.relative_to(references)
            if len(rel.parts) > 1:
                errors.append(f"{path}: references must be at most one directory level")


def check_marked_adapter(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing adapter template: {path}")
        return
    text = read_text(path)
    if BLOCK_BEGIN not in text or BLOCK_END not in text:
        errors.append(f"{path}: missing DOCTOR-BILL marked block")
    if "doctor-bill" not in text or "super_bill" not in text:
        errors.append(f"{path}: must route to doctor-bill and super_bill")


def check_skill(root: Path, relative: str, expected_name: str, errors: list[str]) -> None:
    skill_dir = root / relative
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        errors.append(f"{relative}: missing SKILL.md")
        return

    try:
        fm, body = parse_frontmatter(skill_file)
    except ValidationError as exc:
        errors.append(str(exc))
        return

    unexpected_keys = set(fm) - ALLOWED_FRONTMATTER_KEYS
    if unexpected_keys:
        unexpected = ", ".join(sorted(unexpected_keys))
        allowed = ", ".join(sorted(ALLOWED_FRONTMATTER_KEYS))
        errors.append(
            f"{skill_file}: unexpected frontmatter key(s): {unexpected}; "
            f"officially allowed keys: {allowed}"
        )

    name = fm.get("name", "")
    if not name:
        errors.append(f"{skill_file}: missing name")
    elif not re.fullmatch(r"[a-z0-9-]+", name):
        errors.append(f"{skill_file}: name must use lowercase hyphen-case")
    elif name.startswith("-") or name.endswith("-") or "--" in name:
        errors.append(f"{skill_file}: name cannot start/end with hyphen or contain consecutive hyphens")
    elif len(name) > MAX_SKILL_NAME_LENGTH:
        errors.append(
            f"{skill_file}: name length {len(name)}, maximum is {MAX_SKILL_NAME_LENGTH}"
        )

    if name != expected_name:
        errors.append(f"{skill_file}: expected name {expected_name!r}, got {name!r}")

    description = fm.get("description", "")
    if not description:
        errors.append(f"{skill_file}: missing description")
    else:
        if "<" in description or ">" in description:
            errors.append(f"{skill_file}: description cannot contain angle brackets")
        if len(description) > 1024:
            errors.append(f"{skill_file}: description exceeds official 1024 character limit")
        if len(description) < 25:
            errors.append(f"{skill_file}: description too short")
    if not body.strip():
        errors.append(f"{skill_file}: empty body")

    openai = skill_dir / "agents" / "openai.yaml"
    if not openai.exists():
        errors.append(f"{openai}: missing")
    else:
        fields = parse_simple_openai_yaml(openai)
        for field in REQUIRED_OPENAI_FIELDS:
            if field not in fields or not fields[field]:
                errors.append(f"{openai}: missing interface.{field}")
        short = fields.get("short_description", "")
        short_len = len(short)
        if not 25 <= short_len <= 64:
            errors.append(f"{openai}: short_description length {short_len}, expected 25-64 chars")
        prompt = fields.get("default_prompt", "")
        if f"${expected_name}" not in prompt:
            errors.append(f"{openai}: default_prompt must contain ${expected_name}")

    for link in iter_md_links(body):
        target = (skill_dir / link).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{skill_file}: link escapes repository: {link}")
            continue
        if not target.exists():
            errors.append(f"{skill_file}: broken markdown link: {link}")

    check_reference_depth(skill_dir, errors)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.exists():
        return [f"root does not exist: {root}"]

    for rel in ROOT_REQUIRED:
        check_exists(root, rel, errors)

    for rel, name in EXPECTED_SKILLS.items():
        check_skill(root, rel, name, errors)
        if rel != ".":
            for req in DOMAIN_REQUIRED:
                check_exists(root / rel, req, errors)

    for adapter in [
        root / "adapters/codex/AGENTS.md",
        root / "adapters/claude/CLAUDE.md",
        root / "adapters/cursor/doctor-bill.mdc",
    ]:
        check_marked_adapter(adapter, errors)

    install_sh = root / "scripts/install.sh"
    uninstall_sh = root / "scripts/uninstall.sh"
    for script in [install_sh, uninstall_sh]:
        if script.exists() and not (script.stat().st_mode & 0o111):
            errors.append(f"{script}: not executable")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Doctor Bill skill source tree")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    errors = validate(root)
    if errors:
        print("Doctor Bill source validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Doctor Bill source validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
