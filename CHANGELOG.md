# Changelog

## v2.1.1 - 2026-07-13

### Fixed

- Made installer and uninstaller backups collision-safe with timestamp, process ID and a fallback counter.
- Preserved recoverability of pre-existing Cursor MDC and user-authored Codex/Claude entry content across immediate repeated installs.
- Restored Node dependencies with `npm ci` after a failed deployment resets to the previous commit.
- Transported workflow values as Base64 data instead of interpolating unsafe remote-shell string literals.
- Added noninteractive systemd sudo, workflow timeout, SSH batch/connect/keepalive settings and health timeout forwarding.
- Replaced hidden rollback failures with per-step status reporting and a `CRITICAL` recovery warning.
- Added dynamic regression tests for backup safety, dirty-worktree refusal, Node rollback, failed recovery and shell-injection resistance.

## v2.1.0 - 2026-07-13

### Fixed

- Rebuilt Doctor Bill as one mandatory main Skill plus four self-contained domain Skills.
- Removed fragmented behavioral sources: `work.md`, root/domain `references/`, and passive `agents/developer.md` / `agents/tester.md`.
- Restored the approved `super_bill` / 贝尔 identity, requirements gate, architecture gate, UI gate, branch-first development, independent testing, acceptance and reporting rules.
- Restored the exact decision priority and made FastAPI/aiohttp/etc. preferences non-absolute.
- Restored mandatory SQLAlchemy async ORM, lifespan session factory, request/task session isolation, existing MySQL preference, third normal form, and development/test database isolation.
- Added the full production → bridge → raw data → aggregation → API → UI scenario workflow and the three-minute-to-hourly-report example.
- Prevented domain Skills from implicit invocation and routed their default prompts through `$doctor-bill`.
- Installed the complete five-Skill set for Cursor instead of only installing a short MDC router.

### Added

- Actionable systemd system/user service templates.
- No-sudo user service and linger guidance.
- GitHub Actions main-push deployment workflow.
- Safe deployment script with dirty-worktree guard, fast-forward update, frozen dependency sync, migration gate, restart, health checks, logs and rollback.
- Requirement-matrix source validator and six behavior contract scenarios.
- Installed-content hash validation for Codex, Claude Code and Cursor.

### Preserved

- Original `persona.md`; mandatory identity and behavior are also embedded in the main Skill so execution does not depend on lazy-loading the persona file.

## v2.0.0 - 2026-07-13

Initial Doctor Bill v2 release. Superseded by v2.1.0 because mandatory behavior was over-fragmented into optional references and platform/behavior validation was incomplete.
