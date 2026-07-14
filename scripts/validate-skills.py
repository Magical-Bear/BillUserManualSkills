#!/usr/bin/env python3
"""Validate Doctor Bill source structure and approved requirement coverage."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_NAMES = [
    "doctor-bill-software",
    "doctor-bill-hardware",
    "doctor-bill-ai",
    "doctor-bill-ops",
]


def read(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def require(path: Path, terms: list[str], errors: list[str]) -> None:
    text = read(path, errors)
    for term in terms:
        if term not in text:
            errors.append(f"{path.relative_to(ROOT)}: missing required content {term!r}")


def validate_frontmatter(path: Path, expected_name: str, errors: list[str]) -> None:
    text = read(path, errors)
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append(f"{path.relative_to(ROOT)}: invalid frontmatter")
        return
    frontmatter = match.group(1)
    if not re.search(rf"^name:\s*{re.escape(expected_name)}\s*$", frontmatter, re.M):
        errors.append(f"{path.relative_to(ROOT)}: expected name {expected_name}")
    if not re.search(r"^description:\s*\S.+$", frontmatter, re.M):
        errors.append(f"{path.relative_to(ROOT)}: missing description")


def main() -> int:
    errors: list[str] = []

    validate_frontmatter(ROOT / "SKILL.md", "doctor-bill", errors)
    for name in DOMAIN_NAMES:
        validate_frontmatter(ROOT / "skills" / name / "SKILL.md", name, errors)

    forbidden = [
        ROOT / "work.md",
        ROOT / "references",
        ROOT / "agents" / "developer.md",
        ROOT / "agents" / "tester.md",
    ]
    forbidden += [ROOT / "skills" / name / "references" for name in DOMAIN_NAMES]
    for path in forbidden:
        if path.exists():
            errors.append(f"forbidden fragmented rule artifact exists: {path.relative_to(ROOT)}")

    require(ROOT / "SKILL.md", [
        "super_bill", "贝尔 / Doctor Bill", "不同时充当守门员和裁判员",
        "superpowers", "Context7", "ui-ux-pro-max-skill", "小白能看懂",
        "用户明确要求\n> 现有项目约束", "开发 Agent 完成后，再派测试 Agent",
        "非 `main` 分支", "httpx.AsyncClient", "禁止 mock", "用户明确验收",
        "UI → 消费/聚合 → API → 数据库 → 桥梁层 → 生产端",
    ], errors)
    require(ROOT / "skills/doctor-bill-software/SKILL.md", [
        "FastAPI", "aiohttp", "psycopg 3", "Taskiq", "FastMCP", "SQLAlchemy 2.x ORM",
        "async_sessionmaker", "AsyncSession", "lifespan", "现有 MySQL",
        "开发数据库与测试数据库必须", "第三范式", "3 分钟", "20 个样本",
        "aggregation_version", "原始数据", "向后兼容", ".env.example",
        "httpx.AsyncClient", "真实运行服务",
    ], errors)
    require(ROOT / "skills/doctor-bill-hardware/SKILL.md", [
        "ESP32", "STM32", "UART", "I²C", "SPI", "CAN", "RS-485",
        "MQTT", "protocol_version", "sequence_no", "离线缓存", "原始 payload",
        "开发/测试库隔离", "OTA", "回滚",
    ], errors)
    require(ROOT / "skills/doctor-bill-ai/SKILL.md", [
        "Dify", "LangChain/LangGraph", "FastMCP", "RAG", "embedding model/version",
        "prompt version", "model/provider version", "SQLAlchemy async ORM",
        "开发/测试库分离", "vLLM", "prompt injection", "真实 E2E",
    ], errors)
    require(ROOT / "skills/doctor-bill-ops/SKILL.md", [
        "systemctl --user", "enable-linger", "StartLimitIntervalSec", "StartLimitBurst",
        "WantedBy=default.target", "DEPLOY_KNOWN_HOSTS", "main", "concurrency",
        "uv sync --frozen", "MIGRATION_COMMAND", "工作树不干净", "回滚", "零停机",
    ], errors)

    for name in DOMAIN_NAMES:
        yaml_path = ROOT / "skills" / name / "agents/openai.yaml"
        require(yaml_path, ["Use $doctor-bill first", "allow_implicit_invocation: false"], errors)
    require(ROOT / "agents/openai.yaml", ["allow_implicit_invocation: true"], errors)

    for adapter in [
        ROOT / "adapters/codex/AGENTS.md",
        ROOT / "adapters/claude/CLAUDE.md",
        ROOT / "adapters/cursor/doctor-bill.mdc",
    ]:
        require(adapter, [
            "DOCTOR-BILL:BEGIN", "super_bill", "superpowers", "Context7",
            "ui-ux-pro-max-skill", "开发 Agent", "测试 Agent", "SQLAlchemy",
            "开发数据库", "3 分钟", "用户验收",
        ], errors)
    require(ROOT / "adapters/cursor/doctor-bill.mdc", ["alwaysApply: true"], errors)

    require(ROOT / "skills/doctor-bill-ops/assets/systemd/doctor-bill-system.service", [
        "User=__SERVICE_USER__", "StartLimitIntervalSec=300", "StartLimitBurst=5",
        "WantedBy=multi-user.target",
    ], errors)
    require(ROOT / "skills/doctor-bill-ops/assets/systemd/doctor-bill-user.service", [
        "StartLimitIntervalSec=300", "StartLimitBurst=5", "WantedBy=default.target",
    ], errors)
    require(ROOT / "skills/doctor-bill-ops/assets/github/deploy-main.yml", [
        "branches: [main]", "workflow_dispatch", "permissions:", "contents: read",
        "concurrency:", "timeout-minutes: 15", "DEPLOY_KNOWN_HOSTS",
        "BatchMode=yes", "ConnectTimeout=15", "HEALTH_TIMEOUT_SECONDS", "APP_DIR_B64", "deploy.sh",
    ], errors)
    require(ROOT / "skills/doctor-bill-ops/assets/deploy/deploy.sh", [
        "set -Eeuo pipefail", "git status --porcelain", "git pull --ff-only",
        "uv sync --frozen", "npm ci", "MIGRATION_COMMAND", "health_check", "git reset --hard",
        "sudo -n systemctl", "rollback result:", "CRITICAL:", "base64 --decode",
    ], errors)

    require(ROOT / "scripts/install.sh", ["unique_backup_path", "doctor-bill-backup", "-$$"], errors)
    require(ROOT / "scripts/uninstall.sh", ["unique_backup_path", "doctor-bill-uninstall", "-$$"], errors)
    require(ROOT / "scripts/test-regressions.py", [
        "unique backups and custom content", "node rollback and reporting",
        "critical rollback and dirty guard", "base64 transport",
    ], errors)

    scenarios = json.loads((ROOT / "tests/behavior-scenarios.json").read_text(encoding="utf-8"))
    if len(scenarios) < 6:
        errors.append("tests/behavior-scenarios.json: expected at least six scenarios")

    if errors:
        print("Doctor Bill source validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Doctor Bill source validation passed: self-contained five-Skill architecture and requirement matrix verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
