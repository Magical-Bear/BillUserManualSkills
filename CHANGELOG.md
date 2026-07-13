# Changelog

## v2 - 2026-07-13

### Added

- Renamed root Skill from `colleague-beier` to `doctor-bill`.
- Standardized execution identity as `super_bill`.
- Added root `agents/openai.yaml`.
- Added developer and tester role documents:
  - `agents/developer.md`
  - `agents/tester.md`
- Added four domain Skills:
  - `doctor-bill-software`
  - `doctor-bill-hardware`
  - `doctor-bill-ai`
  - `doctor-bill-ops`
- Added one-level references for root and each domain Skill.
- Added user-level adapter templates:
  - Codex `AGENTS.md`
  - Claude `CLAUDE.md`
  - Cursor `.mdc`
- Added install and uninstall scripts with dry-run, help, path overrides, safe backups, and marked block updates.
- Added source and installation validators:
  - `scripts/validate-skills.py`
  - `scripts/validate-install.py`

### Changed

- Root `SKILL.md` now focuses on gates, routing, role separation, branch rules, merge gates, and final reporting.
- `work.md` is retained as compatibility navigation instead of being removed.
- README now documents Doctor Bill v2 architecture, install paths, Cursor path verification, validation, and workflow gates.
- `meta.json` updated to Doctor Bill v2 metadata.

### Preserved

- `persona.md` is preserved as the original persona source.
- Legacy technical preferences are migrated into domain Skills and `references/legacy-work-knowledge.md`.

### Notes

- Automatic restart is explicitly distinguished from zero-downtime deployment.
- API E2E testing policy requires `asyncio + httpx.AsyncClient` against a real running service, with no mock.
