#!/usr/bin/env python3
"""Dynamic regressions for installer backup safety and deployment rollback."""
from __future__ import annotations

import base64
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts/install.sh"
UNINSTALL = ROOT / "scripts/uninstall.sh"
DEPLOY = ROOT / "skills/doctor-bill-ops/assets/deploy/deploy.sh"


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True)
    if check and result.returncode:
        raise AssertionError(f"command failed ({result.returncode}): {' '.join(cmd)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result


def write_executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def test_unique_backups_and_custom_content(tmp: Path) -> None:
    fakebin = tmp / "fixed-date-bin"
    fakebin.mkdir()
    write_executable(fakebin / "date", "#!/usr/bin/env bash\nprintf '%s\\n' 20260713120000\n")
    env = os.environ.copy()
    env["PATH"] = f"{fakebin}:{env['PATH']}"

    codex = tmp / "codex"
    claude = tmp / "claude"
    cursor = tmp / "cursor"
    (codex).mkdir()
    (claude).mkdir()
    (cursor / "rules").mkdir(parents=True)
    (codex / "AGENTS.md").write_text("CODEX CUSTOM CONTENT\n", encoding="utf-8")
    (claude / "CLAUDE.md").write_text("CLAUDE CUSTOM CONTENT\n", encoding="utf-8")
    original_cursor = "ORIGINAL CURSOR MDC\n"
    (cursor / "rules/doctor-bill.mdc").write_text(original_cursor, encoding="utf-8")

    args = [
        "bash", str(INSTALL), "--platform", "all",
        "--codex-home", str(codex), "--claude-home", str(claude),
        "--cursor-home", str(cursor),
    ]
    run(args, env=env)
    run(args, env=env)

    assert "CODEX CUSTOM CONTENT" in (codex / "AGENTS.md").read_text(encoding="utf-8")
    assert "CLAUDE CUSTOM CONTENT" in (claude / "CLAUDE.md").read_text(encoding="utf-8")
    for skills_root in [codex / "skills", claude / "skills", cursor / "skills"]:
        assert not (skills_root / "doctor-bill/persona.md").exists(), "obsolete persona.md was installed"
    backups = list((cursor / "rules").glob("doctor-bill.mdc.doctor-bill-backup-*"))
    assert len(backups) == 2, f"expected two unique Cursor backups, found {backups}"
    assert len({path.name for path in backups}) == len(backups)
    assert any(path.read_text(encoding="utf-8") == original_cursor for path in backups), "original Cursor MDC was not recoverable"

    uninstall_args = [
        "bash", str(UNINSTALL), "--platform", "all",
        "--codex-home", str(codex), "--claude-home", str(claude),
        "--cursor-home", str(cursor),
    ]
    run(uninstall_args, env=env)
    run(args, env=env)
    run(uninstall_args, env=env)
    uninstall_backups = list((cursor / "rules").glob("doctor-bill.mdc.doctor-bill-uninstall-*"))
    assert len(uninstall_backups) == 2, f"expected two unique uninstall backups, found {uninstall_backups}"


def git(cmd: list[str], cwd: Path) -> str:
    return run(["git", *cmd], cwd=cwd).stdout.strip()


def make_deploy_fixture(tmp: Path) -> tuple[Path, Path, str]:
    origin = tmp / "origin.git"
    author = tmp / "author"
    server = tmp / "server"
    run(["git", "init", "--bare", str(origin)])
    run(["git", "init", "-b", "main", str(author)])
    git(["config", "user.name", "Regression"], author)
    git(["config", "user.email", "regression@example.invalid"], author)
    (author / "package-lock.json").write_text('{"version": 1}\n', encoding="utf-8")
    git(["add", "package-lock.json"], author)
    git(["commit", "-m", "old"], author)
    git(["remote", "add", "origin", str(origin)], author)
    git(["push", "-u", "origin", "main"], author)
    old_commit = git(["rev-parse", "HEAD"], author)
    run(["git", "clone", "--branch", "main", str(origin), str(server)])
    return author, server, old_commit


def make_fake_tools(tmp: Path, curl_body: str) -> tuple[Path, Path, Path]:
    fakebin = tmp / "fakebin"
    fakebin.mkdir(exist_ok=True)
    npm_log = tmp / "npm.log"
    systemctl_log = tmp / "systemctl.log"
    write_executable(fakebin / "npm", f"#!/usr/bin/env bash\nprintf '%s %s\\n' \"$*\" \"$(cat package-lock.json)\" >> {shlex_quote(npm_log)}\n")
    write_executable(fakebin / "systemctl", f"#!/usr/bin/env bash\nprintf '<%s>\\n' \"$@\" >> {shlex_quote(systemctl_log)}\n")
    write_executable(fakebin / "journalctl", "#!/usr/bin/env bash\nexit 0\n")
    write_executable(fakebin / "curl", "#!/usr/bin/env bash\n" + curl_body + "\n")
    return fakebin, npm_log, systemctl_log


def shlex_quote(path: Path) -> str:
    import shlex
    return shlex.quote(str(path))


def deploy_env(fakebin: Path, server: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.update({
        "PATH": f"{fakebin}:{env['PATH']}",
        "APP_DIR": str(server),
        "SERVICE_MODE": "user",
        "SERVICE_NAME": "doctor-bill-test.service",
        "HEALTH_URL": "http://127.0.0.1/health",
        "HEALTH_ATTEMPTS": "1",
        "HEALTH_INTERVAL_SECONDS": "0",
        "HEALTH_TIMEOUT_SECONDS": "1",
    })
    return env


def test_node_rollback_and_reporting(tmp: Path) -> None:
    author, server, old_commit = make_deploy_fixture(tmp)
    (author / "package-lock.json").write_text('{"version": 2}\n', encoding="utf-8")
    git(["add", "package-lock.json"], author)
    git(["commit", "-m", "new"], author)
    git(["push", "origin", "main"], author)

    fakebin, npm_log, _ = make_fake_tools(
        tmp,
        "if grep -q '\"version\": 2' package-lock.json; then exit 1; fi\nexit 0",
    )
    result = run(["bash", str(DEPLOY)], env=deploy_env(fakebin, server), check=False)
    combined = result.stdout + result.stderr
    assert result.returncode != 0, "failed deployment should return non-zero"
    assert git(["rev-parse", "HEAD"], server) == old_commit, "code was not rolled back"
    npm_text = npm_log.read_text(encoding="utf-8")
    assert npm_text.count("ci") == 2, f"npm ci must run for deployment and rollback: {npm_text}"
    assert '"version": 2' in npm_text and '"version": 1' in npm_text
    assert "rollback result: git_reset=0 dependencies=0 service_restart=0 health=0" in combined
    assert "CRITICAL" not in combined


def test_critical_rollback_and_dirty_guard(tmp: Path) -> None:
    author, server, _ = make_deploy_fixture(tmp)
    (author / "package-lock.json").write_text('{"version": 2}\n', encoding="utf-8")
    git(["add", "package-lock.json"], author)
    git(["commit", "-m", "new"], author)
    git(["push", "origin", "main"], author)
    fakebin, _, _ = make_fake_tools(tmp, "exit 1")
    result = run(["bash", str(DEPLOY)], env=deploy_env(fakebin, server), check=False)
    assert "CRITICAL: rollback did not fully restore a healthy service" in result.stdout + result.stderr

    (server / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    dirty = run(["bash", str(DEPLOY)], env=deploy_env(fakebin, server), check=False)
    assert dirty.returncode != 0
    assert "worktree is dirty" in dirty.stdout + dirty.stderr


def b64(value: str) -> str:
    return base64.b64encode(value.encode()).decode()


def test_base64_transport_is_data_not_shell(tmp: Path) -> None:
    _, server, _ = make_deploy_fixture(tmp)
    fakebin, _, systemctl_log = make_fake_tools(tmp, "exit 0")
    marker = tmp / "INJECTION_MARKER"
    payload = f"svc'; touch {marker}; echo 'x\n$(touch {marker})"
    env = os.environ.copy()
    env["PATH"] = f"{fakebin}:{env['PATH']}"
    env.update({
        "APP_DIR_B64": b64(str(server)),
        "SERVICE_MODE_B64": b64("user"),
        "SERVICE_NAME_B64": b64(payload),
        "HEALTH_URL_B64": b64("http://127.0.0.1/health?q='quoted'\nnext"),
        "HEALTH_ATTEMPTS_B64": b64("1"),
        "HEALTH_INTERVAL_SECONDS_B64": b64("0"),
        "HEALTH_TIMEOUT_SECONDS_B64": b64("1"),
    })
    result = run(["bash", str(DEPLOY)], env=env, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not marker.exists(), "decoded service value escaped into shell execution"
    assert payload in systemctl_log.read_text(encoding="utf-8"), "service name was not preserved as data"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="doctor-bill-regression-") as raw:
        base = Path(raw)
        tests = [
            ("unique backups and custom content", test_unique_backups_and_custom_content),
            ("node rollback and reporting", test_node_rollback_and_reporting),
            ("critical rollback and dirty guard", test_critical_rollback_and_dirty_guard),
            ("base64 transport", test_base64_transport_is_data_not_shell),
        ]
        for index, (name, test) in enumerate(tests):
            case = base / f"case-{index}"
            case.mkdir()
            test(case)
            print(f"PASS: {name}")
    print("Doctor Bill dynamic regression tests passed: 4/4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
