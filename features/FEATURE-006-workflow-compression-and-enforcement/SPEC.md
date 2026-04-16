# Feature: Workflow Compression and Enforcement

- ID: FEATURE-006-workflow-compression
- Status: Closed
- Date locked: 2026-03-18
- Complexity: normal
- Change kind: mixed

## Goal
Make VibeCode OS lighter for solo developers while making completion harder to fake, without adding new commands or making the four core skills fragile.

## Touches
- src/skills/vibe-start/SKILL.md
- src/skills/vibe-resume/SKILL.md
- src/skills/vibe-status/SKILL.md
- src/skills/vibe-done/SKILL.md
- src/templates/AGENTS.md
- SESSION_LOG.md format (compressed to 3-bullet format)

## Acceptance criteria
- [x] [verify=spec] Trivial features can be started with little or no clarification (fast path in `/vibe-start`)
- [x] [verify=repo] `/vibe-start` still creates SPEC.md + writes `.claude/active_feature` for trivial features
- [x] [verify=repo] No new required commands introduced — the same four skills remain the full surface
- [x] [verify=spec] `/vibe-resume` cannot mutate user context files except clearing an invalid active feature
- [x] [verify=spec] `/vibe-resume` explains blank-state detection transparently rather than silently skipping
- [x] [verify=spec] `/vibe-done` does not classify features as complete without meaningful evidence (no rubber-stamp close)
- [x] [verify=user] Unchecked major acceptance criteria trigger a warning during closeout before classification
- [x] [verify=repo] Repeated `/vibe-done` runs produce one clean VERIFY.md (overwrite, not append)
- [x] [verify=user] Zero-diff short-circuit stops the close flow early when no work was done
- [x] [verify=user] Force-close escape hatch allows closure with explicit "Dropped scope" tracking
- [x] [verify=spec] `DECISIONS.md` entries are captured naturally during real work without extra commands
- [x] [verify=spec] Trivial decisions do not generate decision spam
- [x] [verify=repo] `SESSION_LOG.md` entries are capped at 3 bullets, 15 words each
- [x] [verify=spec] `/vibe-status` shows remaining unverified criteria with "not yet verified" marker
- [x] [verify=cmd] All existing structural smoke tests still pass
- [x] [verify=repo] Trivial specs use the same section headings as normal specs (parse compatibility maintained)

## Verification plan
- AC-1: Read vibe-start SKILL.md trivial fast-path section; confirmed concise path with no extra questions.
- AC-2: Started a trivial feature; inspected SPEC.md and `.claude/active_feature`; both written correctly.
- AC-3: Read all four SKILL.md files; confirmed no fifth command referenced.
- AC-4: Read vibe-resume SKILL.md; confirmed read-only enforcement rule and no write operations except active_feature clear.
- AC-5: Ran `/vibe-resume` on blank state; confirmed explanation of blank-state detection in output.
- AC-6: Read vibe-done SKILL.md evidence classification section; confirmed explicit criteria required.
- AC-7: Ran `/vibe-done` with most criteria unchecked; confirmed warning displayed before classification.
- AC-8: Ran `/vibe-done` twice on same feature; confirmed single VERIFY.md (not duplicated content).
- AC-9: Ran `/vibe-done` immediately after `/vibe-start` with no work described; confirmed early exit.
- AC-10: Triggered force-close; confirmed "Dropped scope" tracked in VERIFY.md.
- AC-11: Read vibe-done SKILL.md passive capture step; confirmed decision writing integrated.
- AC-12: Read passive capture threshold rule; confirmed null/trivial decisions not recorded.
- AC-13: Read SESSION_LOG.md template constraints in SKILL.md; confirmed 3-bullet, 15-word cap.
- AC-14: Read vibe-status SKILL.md; confirmed default-to-unverified marker on unchecked criteria.
- AC-15: `python tests/smoke/run_smoke_tests.py` — exit 0.
- AC-16: Compared trivial SPEC.md headings to normal SPEC.md headings; same structure confirmed.

## Out of scope
- New commands (vibe-checkpoint, vibe-decide, vibe-revert, vibe-reopen)
- Breaking existing recovery or installer behaviour

## Known risks
- Trivial-feature fast path must maintain spec parse compatibility or vibe-status/done break
- Template compression must preserve `[TODO:]` markers or template_markers smoke test fails
- Force-close must not be recorded as a normal "Complete" — classification must be distinct
