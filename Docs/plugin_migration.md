# VibeCode OS — Plugin Migration Guide

## Overview

VibeCode OS v2.0.1 ships as both a **standalone skill pack** (`.claude/skills/`) and an **official Claude Code plugin** (`.claude-plugin/`). Both modes are fully functional. The plugin is an optional packaging layer — it does not replace standalone mode.

---

## Install modes

### Standalone mode (default)
```
python install.py
```
Installs skill files to `.claude/skills/vibe-*/SKILL.md`. Works in all Claude Code environments, including remote sessions.

### Plugin mode (alongside standalone)
```
python install.py --plugin
```
Installs standalone skills AND creates `.claude-plugin/` with the official plugin manifest, packaged skills, helpers, and hooks. Both paths coexist.

### Rollback (remove plugin, keep standalone)
```
python install.py --rollback
```
Removes `.claude-plugin/` directory. Standalone `.claude/skills/` remains untouched and fully functional.

---

## Coexistence rules

- When the plugin is installed and active in your Claude Code session, `.claude-plugin/skills/` files take precedence over `.claude/skills/`
- When the plugin is absent, disabled, or unsupported, `.claude/skills/` is the fallback
- Both modes share the same `.claude/` data directory (active_feature, context/, runtime/, approved_commands.json)
- No user data is duplicated between the two modes

---

## Remote session limitation

**The plugin is not available in remote Claude Code sessions.**

When connecting to a remote agent or cloud session, Claude Code does not load local `.claude-plugin/` manifests. In this case:
- Standalone `.claude/skills/` skills still work normally (they are loaded per-session)
- All compact artifacts (`.claude/context/`) remain available to both modes
- Workflow semantics are identical — only the packaging layer differs

---

## Update discipline

When distributing changes to VibeCode OS:

1. Bump `version` in `.claude-plugin/plugin.json` for any change to packaged assets
2. Use semantic versioning: MAJOR.MINOR.PATCH
   - MAJOR: breaking changes to skill semantics or data format
   - MINOR: new features, new skills, new helpers
   - PATCH: bug fixes, wording changes, smoke test updates
3. Run `python install.py --plugin` after any source change to keep `.claude-plugin/` in sync
4. Smoke tests validate plugin parity: `python tests/smoke/run_smoke_tests.py`

---

## Hook restrictions

Hooks defined in `.claude-plugin/hooks/hooks.json` may only call scripts located under `.claude-plugin/helpers/`. Absolute paths and external scripts are not permitted. This is enforced by the parity test suite.

---

## Marketplace readiness

To publish VibeCode OS to the Claude Code plugin marketplace:
1. Ensure `plugin.json` has a valid `homepage` URL
2. All 4 skill files must be present under `.claude-plugin/skills/`
3. All helper scripts must be present under `.claude-plugin/helpers/`
4. Run the full smoke test suite including parity tests (0 failures required)
5. Bump version and tag a release commit

---

## Python version requirement

All helper scripts (`src/helpers/`, `src/adapter/`, `.claude-plugin/helpers/`) require **Python 3.8+** and use stdlib only (no pip installs). Scripts are verified for 3.8 syntax compatibility via the `py38_compatible_imports` smoke scenario.

---

## Troubleshooting

**Plugin skills not loading:** verify `.claude-plugin/plugin.json` is valid JSON (`python -c "import json; json.load(open('.claude-plugin/plugin.json'))"`)

**Corrupt plugin state:** run `python install.py --rollback` to remove plugin, then `python install.py` to restore standalone mode

**Standalone skills missing:** run `python install.py` (without `--plugin`) to reinstall standalone skills

**Context artifacts stale:** delete `.claude/context/project_state.json` to force full reconstruction on next `/vibe-resume`
