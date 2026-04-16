# Feature: Core Skill Commands

- ID: FEATURE-001-core-skills
- Status: Closed
- Date locked: 2026-03-18
- Complexity: complex
- Change kind: behavioral

## Goal
Give Claude Code four skills that create the structured vibe coding workflow, so the user never has to learn a format or fill in templates manually.

## Touches
- src/skills/vibe-start/SKILL.md
- src/skills/vibe-resume/SKILL.md
- src/skills/vibe-status/SKILL.md
- src/skills/vibe-done/SKILL.md
- install.py
- src/templates/PROJECT_CONTEXT.md
- src/templates/AGENTS.md
- src/templates/DECISIONS.md
- src/templates/SESSION_LOG.md

## Acceptance criteria
- [x] [verify=spec] `/vibe-start` asks 2-3 clarifying questions and drafts a complete SPEC.md without the user writing any template content
- [x] [verify=spec] `/vibe-resume` restores full project context within 30 seconds of being typed
- [x] [verify=spec] `/vibe-status` compares acceptance criteria against verification notes and reports done / not verified / open
- [x] [verify=spec] `/vibe-done` produces a complete VERIFY.md through conversational Q&A without the user filling in a template
- [x] [verify=cmd] `python install.py` completes without error on a fresh repo in under 60 seconds
- [x] [verify=cmd] `install.py` uses only Python stdlib (os, shutil, sys, argparse — no pip installs)
- [x] [verify=repo] Active feature tracked correctly via `.claude/active_feature` (written by `/vibe-start`, read by all other commands)
- [x] [verify=repo] Feature auto-numbering produces correct FEATURE-NNN-slug format for sequentially created features
- [x] [verify=repo] `features/` directory created by installer; empty on first install
- [x] [verify=spec] No command blocks or slows the developer — all four skills are voluntary

## Verification plan
- AC-1: Ran `/vibe-start` interactively; confirmed 2-3 question limit and Claude-drafted SPEC.md produced.
- AC-2: Timed `/vibe-resume` on a session with active feature; full context restored within 30s.
- AC-3: Compared `/vibe-status` output against SPEC.md criteria; all items categorised correctly.
- AC-4: Ran `/vibe-done`; confirmed VERIFY.md created with all required sections.
- AC-5: `python install.py` in a fresh git repo; exit 0, all items created.
- AC-6: `grep -r "import " install.py | grep -v "^#"` — only stdlib modules present.
- AC-7: Read `.claude/active_feature` after `/vibe-start`; matched new feature ID.
- AC-8: Created three features in sequence; IDs incremented correctly (001, 002, 003).
- AC-9: Inspected `features/` after install; directory exists and is empty.
- AC-10: All four commands ran without forcing any prerequisite action.

## Out of scope
- Plugin packaging (FEATURE-010)
- Automated test harness (FEATURE-005)
- Recovery from broken state (FEATURE-003)
- Output wording polish (FEATURE-002)

## Known risks
- Claude's skill file format may have size limits if commands grow significantly
- Users may not type `/vibe-done` and just stop — `/vibe-resume` must handle stale active features
- Built-in Claude Code commands may change; `vibe-` prefix provides namespace isolation
