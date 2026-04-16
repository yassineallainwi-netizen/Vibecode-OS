# Feature: Hardened Claude Code Plugin Delivery

## Complexity
complex

## Goal
Convert VibeCode OS into an installable Claude Code plugin while keeping standalone `.claude/skills` mode fully working alongside it.

## What it should do
- Create `.claude-plugin/` directory with official plugin format: `plugin.json`, packaged skill files, helper scripts, optional hooks
- `plugin.json` declares skills, required/optional capabilities, fallback mode
- `src/adapter/capabilities.py` probes available host capabilities (file_read/write, command_exec) with 500ms timeout; caches locally; fails gracefully
- `src/adapter/war_room.py` defines `WarRoomManifest` dataclass and `render_as_text()` — stable payload contract across hosts
- `src/adapter/actions.py` defines 8 stable workflow actions (start_feature, resume_work, show_status, close_feature, verify_state, compact_context, recover_active_feature, draft_commit_suggestion)
- `docs/plugin_migration.md` covers install/update/rollback, standalone↔plugin coexistence, remote-session limitation, version bump discipline, marketplace readiness
- `install.py` updated: `--plugin` flag installs `.claude-plugin/` alongside `.claude/skills/`; `--rollback` flag restores standalone-only state; both modes coexist
- `tests/smoke/test_plugin_parity.py` validates structural parity (skill content hash match), state continuity, degraded-mode behavior, hook path restriction
- Existing `tests/smoke/run_smoke_tests.py` gains 4 plugin scenarios

## What it should NOT do
- Break standalone `.claude/skills` mode — it must continue working with or without the plugin
- Use custom Python command handlers as the slash-command surface (use official plugin format only)
- Require the plugin to work in remote sessions (document limitation; standalone is the fallback)
- Execute git commands in any adapter or hook

## Acceptance Criteria
- [ ] `.claude-plugin/plugin.json` exists with valid JSON and required fields (name, version, skills, capabilities_required, fallback_mode)
- [ ] `.claude-plugin/skills/` contains all 4 skill files matching source content
- [ ] `.claude-plugin/helpers/` contains all helper scripts from src/helpers/
- [ ] `src/adapter/capabilities.py` implements `probe_capabilities()` with 500ms timeout and local caching
- [ ] `src/adapter/war_room.py` implements `WarRoomManifest` dataclass and `render_as_text()`
- [ ] `src/adapter/actions.py` defines all 8 workflow actions
- [ ] `docs/plugin_migration.md` covers install, update, rollback, coexistence, remote-session limitation
- [ ] `install.py --plugin` installs `.claude-plugin/` alongside `.claude/skills/` (both present after install)
- [ ] `install.py --rollback` restores standalone-only state (`.claude-plugin/` removed or skipped)
- [ ] Standalone `.claude/skills` still installs correctly after `--plugin` run
- [ ] `tests/smoke/test_plugin_parity.py` all parity tests pass
- [ ] All existing smoke tests still pass (20/20)

## Risks and edge cases
- Plugin skill files must stay in sync with src/skills/ — parity tests catch divergence
- Hook path restriction: hooks may only call scripts under `.claude-plugin/helpers/`, not arbitrary paths
- Corrupt plugin state (bad plugin.json) must fall back to standalone mode gracefully
- Remote-session limitation must be clearly documented — plugin not available, standalone is the fallback
