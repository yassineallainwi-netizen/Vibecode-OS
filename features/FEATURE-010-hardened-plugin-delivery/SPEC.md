# Feature: Hardened Claude Code Plugin Delivery

- ID: FEATURE-010-plugin-delivery
- Status: Closed
- Date locked: 2026-03-20
- Complexity: complex
- Change kind: behavioral

## Goal
Convert VibeCode OS into an installable Claude Code plugin while keeping standalone `.claude/skills` mode fully working alongside it.

## Touches
- .claude-plugin/plugin.json
- .claude-plugin/skills/ (all four packaged skill files)
- .claude-plugin/helpers/ (all helper scripts mirrored from src/helpers/)
- src/adapter/capabilities.py
- src/adapter/war_room.py
- src/adapter/actions.py
- docs/plugin_migration.md
- install.py
- tests/smoke/test_plugin_parity.py

## Acceptance criteria
- [x] [verify=cmd] `.claude-plugin/plugin.json` exists with valid JSON and required fields (name, version, skills, capabilities_required, fallback_mode)
- [x] [verify=cmd] `.claude-plugin/skills/` contains all four skill files matching source content (parity test passes)
- [x] [verify=cmd] `.claude-plugin/helpers/` contains all helper scripts from src/helpers/
- [x] [verify=repo] `src/adapter/capabilities.py` implements `probe_capabilities()` with 500ms timeout and local caching
- [x] [verify=repo] `src/adapter/war_room.py` implements `WarRoomManifest` dataclass and `render_as_text()`
- [x] [verify=repo] `src/adapter/actions.py` defines all 8 stable workflow actions
- [x] [verify=repo] `docs/plugin_migration.md` covers install, update, rollback, coexistence, and remote-session limitation
- [x] [verify=cmd] `python install.py --plugin` installs both `.claude-plugin/` and `.claude/skills/` (both present after run)
- [x] [verify=cmd] `python install.py --rollback` removes `.claude-plugin/` and restores standalone-only state
- [x] [verify=cmd] Standalone `.claude/skills` still installs correctly after a `--plugin` run
- [x] [verify=cmd] `tests/smoke/test_plugin_parity.py` — all parity tests pass
- [x] [verify=cmd] All existing smoke tests still pass (24/24)

## Verification plan
- AC-1: `python tests/smoke/run_smoke_tests.py --scenario plugin_manifest_valid` — exit 0.
- AC-2: `python tests/smoke/test_plugin_parity.py` — plugin_skills_match_source scenario passes.
- AC-3: `python tests/smoke/run_smoke_tests.py --scenario plugin_helpers_present` — exit 0.
- AC-4: Read capabilities.py; PROBE_TIMEOUT_MS constant, _load_cache/_save_cache functions, CACHE_TTL_HOURS confirmed.
- AC-5: Read war_room.py; WarRoomManifest dataclass with all fields, render_as_text() rendering markdown confirmed.
- AC-6: Read actions.py; all 8 actions returning ActionResult dataclass confirmed.
- AC-7: Read docs/plugin_migration.md; install, update, rollback, coexistence, remote-session limitation sections confirmed.
- AC-8: `python tests/smoke/run_smoke_tests.py --scenario standalone_mode_unchanged` — exit 0.
- AC-9: `python tests/smoke/test_plugin_parity.py` — rollback_removes_plugin scenario passes.
- AC-10: `python tests/smoke/run_smoke_tests.py --scenario standalone_mode_unchanged` — exit 0 after --plugin run.
- AC-11: `python tests/smoke/test_plugin_parity.py` — exit 0, all parity tests pass.
- AC-12: `python tests/smoke/run_smoke_tests.py` — exit 0, 24/24 pass.

## Out of scope
- Breaking standalone `.claude/skills` mode (must continue working with or without the plugin)
- Custom Python command handlers as the slash-command surface (official plugin format only)
- Plugin working in remote Claude sessions (documented limitation; standalone is the fallback)
- Executing git commands in any adapter or hook

## Known risks
- Plugin skill files must stay in sync with src/skills/; parity tests are the only automated gate
- Hooks may only call scripts under `.claude-plugin/helpers/`; arbitrary path execution must be blocked
- Corrupt plugin.json must fall back gracefully to standalone mode (no crash)
