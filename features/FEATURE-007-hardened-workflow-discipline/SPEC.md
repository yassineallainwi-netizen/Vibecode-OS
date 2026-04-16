# Feature: Hardened Workflow Discipline and Project Rules

- ID: FEATURE-007-hardened-discipline
- Status: Closed
- Date locked: 2026-03-18
- Complexity: complex
- Change kind: mixed

## Goal
Make VibeCode OS materially stronger on documentation completeness, session recovery, and workflow discipline without adding ceremony or blocking the developer.

## Touches
- src/skills/vibe-resume/SKILL.md
- src/skills/vibe-start/SKILL.md
- src/skills/vibe-done/SKILL.md
- src/skills/vibe-status/SKILL.md
- src/helpers/claude_md.py
- src/templates/AGENTS.md
- src/templates/SESSION_LOG.md

## Acceptance criteria
- [x] [verify=spec] AGENTS.md blank detection uses concrete heuristics (version marker, byte size, boilerplate fingerprint)
- [x] [verify=spec] High-confidence uncustomized AGENTS.md triggers auto-draft from repo scan with no interview
- [x] [verify=spec] Mixed-confidence AGENTS.md triggers exactly one Accept/Edit/Skip prompt — no interview loop
- [x] [verify=spec] Customized AGENTS.md is skipped entirely on new features (no repeated prompting)
- [x] [verify=repo] CLAUDE.md bridge is generated/synced after an AGENTS.md patch (claude_md.py creates or updates it)
- [x] [verify=repo] CLAUDE.md critical field conflict halts with a user-resolution message (no silent overwrite)
- [x] [verify=spec] `/vibe-resume` outputs the War Room manifest covering all required fields (project, mode, risk, active feature, decisions, verification readiness)
- [x] [verify=repo] All War Room manifest fields are grounded in files; missing fields are omitted rather than fabricated
- [x] [verify=spec] Lost-state (no active feature, no session log) triggers auto mini-resume output, not a questionnaire
- [x] [verify=spec] `/vibe-done` outputs a Git Ghost commit suggestion block (copy-paste only — git never executed)
- [x] [verify=repo] No git write commands are ever executed by any skill
- [x] [verify=repo] Feature slug sanitised to `^[a-z0-9]+(-[a-z0-9]+){0,3}$` max 40 chars before writing `.claude/active_feature`
- [x] [verify=repo] FEATURE-NNN number collision halts with an explicit message; no guessing or auto-increment
- [x] [verify=spec] Repo maturity inferred from file evidence; output adapts between novice and expert tone
- [x] [verify=spec] `/vibe-status` surfaces Mode and Risk flags from the active SPEC.md
- [x] [verify=repo] `SESSION_LOG.md` template uses "Context pointer:" wording
- [x] [verify=repo] `AGENTS.md` template has `<!-- vibecode:agents:v2 -->` version marker and command registry section
- [x] [verify=cmd] All existing smoke tests still pass

## Verification plan
- AC-1: Read vibe-start SKILL.md heuristic classification section; version marker, byte size, and fingerprint checks present.
- AC-2: High-confidence path in vibe-start confirmed; no questions asked for uncustomized AGENTS.md.
- AC-3: Mixed path confirmed; exactly one Accept/Edit/Skip prompt in skill text.
- AC-4: Customized path skip rule confirmed in vibe-start; no AGENTS step on subsequent features.
- AC-5: Ran claude_md.py; confirmed CLAUDE.md created/updated after AGENTS patch.
- AC-6: Introduced critical field conflict in CLAUDE.md; confirmed halt message and no silent overwrite.
- AC-7: Read vibe-resume War Room manifest step; all required fields listed.
- AC-8: Read fail-closed rule in vibe-resume; missing fields omit rather than substitute placeholder text.
- AC-9: Cleared active_feature and session log; ran `/vibe-resume`; mini-resume output appeared, no questionnaire.
- AC-10: Ran `/vibe-done` on complete feature; confirmed Git Ghost copy-paste block in output.
- AC-11: Grepped all SKILL.md files for `git commit`, `git push`, `git add`; no write commands found.
- AC-12: Read slug sanitisation regex and max-length check in vibe-start; confirmed enforcement.
- AC-13: Attempted to create FEATURE-001 when it already existed; confirmed halt message.
- AC-14: Read maturity scoring logic in vibe-resume; novice/expert output path confirmed.
- AC-15: Read vibe-status SKILL.md; Mode and Risk flag output confirmed.
- AC-16: Inspected SESSION_LOG.md template; "Context pointer:" wording present.
- AC-17: Inspected AGENTS.md template; `<!-- vibecode:agents:v2 -->` marker and command registry present.
- AC-18: `python tests/smoke/run_smoke_tests.py` — exit 0, agents_version_marker + agents_command_registry scenarios pass.

## Out of scope
- New commands
- Blocking the developer (all guidance is advisory)
- Prompting for AGENTS rules on every feature (first feature only)
- Executing any git commands

## Known risks
- Skill file growth from War Room + Git Ghost sections; monitor line count
- Template changes must preserve `[TODO:]` markers (smoke test gate)
- CLAUDE.md may not exist in all repos; first-run sync must be safe
