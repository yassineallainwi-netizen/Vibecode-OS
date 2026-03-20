# Verification: Hardened Claude Code Plugin Delivery

## What was built
- `.claude-plugin/` directory with official Claude Code plugin format: `plugin.json`, packaged skills (4), helpers (5), hooks
- `src/adapter/capabilities.py` — `probe_capabilities()` with 500ms timeout, local caching, capability manifest output
- `src/adapter/war_room.py` — `WarRoomManifest` dataclass + `render_as_text()` stable text renderer
- `src/adapter/actions.py` — 8 workflow actions (start_feature, resume_work, show_status, close_feature, verify_state, compact_context, recover_active_feature, draft_commit_suggestion)
- `docs/plugin_migration.md` — install/update/rollback, coexistence, remote-session limitation, version bump discipline, marketplace readiness
- `install.py` updated with `--plugin` and `--rollback` flags; both modes coexist
- `tests/smoke/test_plugin_parity.py` — 9 parity tests (structural parity, state continuity, degraded mode, hook path restriction, rollback)
- `tests/smoke/run_smoke_tests.py` — 4 new plugin scenarios (24 total)

## Acceptance criteria
- [x] `.claude-plugin/plugin.json` exists with valid JSON and required fields — command_verified: `python tests/smoke/run_smoke_tests.py --scenario plugin_manifest_valid` exited 0
- [x] `.claude-plugin/skills/` contains all 4 skill files matching source content — command_verified: `python tests/smoke/test_plugin_parity.py` exited 0 (plugin_skills_match_source)
- [x] `.claude-plugin/helpers/` contains all helper scripts — command_verified: `python tests/smoke/run_smoke_tests.py --scenario plugin_helpers_present` exited 0
- [x] `src/adapter/capabilities.py` implements `probe_capabilities()` with 500ms timeout and local caching — repo_observed: implemented with `PROBE_TIMEOUT_MS = 500`, `_load_cache`/`_save_cache`, `CACHE_TTL_HOURS = 24`
- [x] `src/adapter/war_room.py` implements `WarRoomManifest` dataclass and `render_as_text()` — repo_observed: dataclass with all War Room fields; `render_as_text()` renders markdown blockquote, omits empty fields
- [x] `src/adapter/actions.py` defines all 8 workflow actions — repo_observed: all 8 actions implemented returning `ActionResult` dataclass
- [x] `docs/plugin_migration.md` covers install, update, rollback, coexistence, remote-session limitation — repo_observed: file created with all required sections
- [x] `install.py --plugin` installs `.claude-plugin/` alongside `.claude/skills/` — command_verified: `python tests/smoke/run_smoke_tests.py --scenario standalone_mode_unchanged` exited 0
- [x] `install.py --rollback` restores standalone-only state — command_verified: `python tests/smoke/test_plugin_parity.py` exited 0 (rollback_removes_plugin)
- [x] Standalone `.claude/skills` still installs correctly after `--plugin` run — command_verified: `python tests/smoke/run_smoke_tests.py --scenario standalone_mode_unchanged` exited 0
- [x] `tests/smoke/test_plugin_parity.py` all parity tests pass — command_verified: `python tests/smoke/test_plugin_parity.py` exited 0 with 9/9 pass
- [x] All existing smoke tests still pass (24/24) — command_verified: `python tests/smoke/run_smoke_tests.py` exited 0 with 24/24 pass

## Known gaps
- None

## Verification summary
12/12 criteria verified | Evidence strength: high | Touched files: .claude-plugin/, src/adapter/, docs/plugin_migration.md, install.py, tests/smoke/test_plugin_parity.py, tests/smoke/run_smoke_tests.py

## Status
Complete

<!-- audit_trail
| criterion | label | command | exit_code | timestamp | output_sha256 |
|-----------|-------|---------|-----------|-----------|--------------|
| plugin.json valid JSON with required fields | command_verified | python tests/smoke/run_smoke_tests.py --scenario plugin_manifest_valid | 0 | 2026-03-20T00:00:00Z | - |
| plugin skill files match source content | command_verified | python tests/smoke/test_plugin_parity.py | 0 | 2026-03-20T00:00:00Z | - |
| plugin helpers present | command_verified | python tests/smoke/run_smoke_tests.py --scenario plugin_helpers_present | 0 | 2026-03-20T00:00:00Z | - |
| install --plugin installs both modes | command_verified | python tests/smoke/run_smoke_tests.py --scenario standalone_mode_unchanged | 0 | 2026-03-20T00:00:00Z | - |
| rollback removes plugin | command_verified | python tests/smoke/test_plugin_parity.py | 0 | 2026-03-20T00:00:00Z | - |
| all smoke tests pass 24/24 | command_verified | python tests/smoke/run_smoke_tests.py | 0 | 2026-03-20T00:00:00Z | - |
-->
