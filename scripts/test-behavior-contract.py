#!/usr/bin/env python3
"""Validate approved Doctor Bill scenarios against the mandatory loaded artifacts.

This is a requirement-to-artifact contract test. It is stricter than file-existence
validation, but it does not claim to be a live model evaluation. Independent Agent
forward tests are still required before release.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "tests" / "behavior-scenarios.json"


def main() -> int:
    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    failures: list[str] = []
    passed = 0
    for scenario in scenarios:
        texts: list[str] = []
        for relative in scenario["files"]:
            path = ROOT / relative
            if not path.is_file():
                failures.append(f"{scenario['id']}: missing {relative}")
                continue
            texts.append(path.read_text(encoding="utf-8"))
        combined = "\n".join(texts)
        missing = [term for term in scenario["must_cover"] if term not in combined]
        if missing:
            failures.append(f"{scenario['id']}: missing contract terms {missing}")
        else:
            passed += 1
            print(f"PASS {scenario['id']}: {scenario['prompt']}")

    if failures:
        print("Doctor Bill behavior contract failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Behavior contract passed: {passed}/{len(scenarios)} scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
