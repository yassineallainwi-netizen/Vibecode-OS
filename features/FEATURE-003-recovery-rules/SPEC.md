# Feature: Recovery Rules

- ID: FEATURE-003-recovery-rules
- Status: Closed
- Date locked: 2026-03-18
- Complexity: normal
- Change kind: instruction-only

## Goal
Make the skills recover predictably from missing, broken, or ambiguous project state so the workflow never depends on Claude improvising.

## Touches
- src/skills/vibe-start/SKILL.md
- src/skills/vibe-resume/SKILL.md
- src/skills/vibe-status/SKILL.md
- src/skills/vibe-done/SKILL.md

## Acceptance criteria
- [x] [verify=spec] Missing or empty `.claude/active_feature` is handled deterministically — no guessing, no crash
- [x] [verify=spec] Invalid `.claude/active_feature` (points to non-existent folder) triggers recovery with user choice offered
- [x] [verify=spec] Multiple feature folders with no active feature: Claude suggests the most recently modified and asks for confirmation
- [x] [verify=spec] Active feature folder exists but has no `SPEC.md`: reported as malformed, user asked to repair
- [x] [verify=spec] Missing `VERIFY.md` during `/vibe-done`: created automatically from `SPEC.md` without blocking the developer
- [x] [verify=spec] Blank placeholder templates detected (via `[TODO:` marker check) and user asked setup questions before generating content
- [x] [verify=spec] Premature `/vibe-done` on clearly incomplete work: defaults to "Partially complete", keeps feature active
- [x] [verify=spec] `SESSION_LOG.md` exceeding 10 entries: newest 10 preserved, older entries moved to `SESSION_ARCHIVE.md`

## Verification plan
- AC-1: Deleted `.claude/active_feature`; ran all four commands; no errors, proper guidance offered each time.
- AC-2: Wrote an invalid feature ID to `.claude/active_feature`; ran `/vibe-resume`; recovery prompt appeared with user choice.
- AC-3: Created three feature folders with no active feature; ran `/vibe-status`; most recent suggested with confirmation request.
- AC-4: Created feature folder with empty SPEC.md; ran `/vibe-status`; malformed detection confirmed.
- AC-5: Ran `/vibe-done` without VERIFY.md present; confirmed automatic creation.
- AC-6: Cleared content from PROJECT_CONTEXT.md leaving `[TODO:`; ran `/vibe-resume`; setup questions appeared.
- AC-7: Ran `/vibe-done` with most acceptance criteria unchecked; confirmed "Partially complete" and feature remained active.
- AC-8: Created 12 session log entries; confirmed rollover: newest 10 in SESSION_LOG.md, older entries in SESSION_ARCHIVE.md.

## Out of scope
- README or template content improvements (FEATURE-004)
- Output wording polish beyond recovery scenarios (FEATURE-002)
- Plugin packaging (FEATURE-010)

## Known risks
- Detecting "blank placeholder" templates requires clear heuristics; `[TODO:` marker is the gate
- Recovery rules must cover all permutations; silent failures would undermine the product's core promise
