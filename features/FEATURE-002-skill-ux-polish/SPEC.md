# Feature: Skill UX Polish

- ID: FEATURE-002-skill-ux-polish
- Status: Closed
- Date locked: 2026-03-18
- Complexity: normal
- Change kind: instruction-only

## Goal
Polish the wording and output structure of the four core skills so they feel clear, consistent, and low-friction, eliminating token waste and improving first-time user guidance.

## Touches
- src/skills/vibe-start/SKILL.md
- src/skills/vibe-resume/SKILL.md
- src/skills/vibe-status/SKILL.md
- src/skills/vibe-done/SKILL.md

## Acceptance criteria
- [x] [verify=spec] `/vibe-resume` on a fresh install gives clear first-run guidance using a 5-part structure (project context, current state, active feature, important decisions, recommended next step)
- [x] [verify=spec] `/vibe-start` asks at most 2 clarifying questions per turn (not 5 or more in a list)
- [x] [verify=spec] `/vibe-status` always outputs using the 5-part structure: feature goal, completed work, missing verification, risks/unknowns, recommended next step
- [x] [verify=spec] `/vibe-done` uses explicit language — "Complete", "Partially complete", or "Not ready to close" — to classify the work, never ambiguous summaries
- [x] [verify=spec] Response length across all four commands is shorter than the F-001 baseline (filler phrases removed)
- [x] [verify=spec] No command output references old non-namespaced command names (no `/resume`, `/status`, `/done`)
- [x] [verify=spec] `/vibe-status` handles empty `features/` folder correctly: says "No features have been started yet" rather than reporting a missing folder

## Verification plan
- AC-1: Ran `/vibe-resume` on blank install; confirmed 5-part structure and first-run setup guidance appeared.
- AC-2: Ran `/vibe-start` with a vague request; confirmed exactly 2 questions, not a list.
- AC-3: Ran `/vibe-status` with active feature; confirmed all 5 parts present and clearly labelled.
- AC-4: Ran `/vibe-done` on partial work; confirmed explicit "Partially complete" wording.
- AC-5: Compared response word count to F-001 baseline; reduction confirmed across all four commands.
- AC-6: Grepped all four SKILL.md files for old command names; found none.
- AC-7: Deleted all feature folders; ran `/vibe-status`; confirmed correct wording (no "missing folder" error).

## Out of scope
- Recovery from broken state (FEATURE-003)
- Template or README improvements (FEATURE-004)
- Automated test harness (FEATURE-005)
- Plugin packaging (FEATURE-010)

## Known risks
- Excessive brevity in skill wording could make instructions hard for Claude to follow across different context sizes
