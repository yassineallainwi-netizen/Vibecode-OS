# FEATURE-003-recovery-rules

## Goal

Make the skills recover predictably from missing, broken, or ambiguous project state.

## Why this feature exists

The workflow should not depend on Claude improvising when repo state is broken or incomplete.

This feature makes recovery deterministic.

## In scope

- active feature recovery
- malformed feature handling
- blank template detection
- missing verification handling
- premature `/vibe-done`
- session log rollover behavior

## Out of scope

- README
- template polish
- general output wording polish
- plugin packaging

## Recovery rules

### Case: `features/` exists but is empty
Response:
- say "No features have been started yet."
- recommend `/vibe-start`

### Case: `.claude/active_feature` is missing or empty
Behavior:
- inspect `features/` only when needed
- if no feature folders exist: recommend `/vibe-start`
- if one feature folder exists: ask whether to resume it or start a new one
- if multiple feature folders exist: suggest the most recently modified one and ask the user to confirm

### Case: `.claude/active_feature` points to a missing folder
Behavior:
- notify the user that the active feature reference is broken
- clear the invalid value
- ask whether to resume an existing feature or start a new one

### Case: active feature exists but has no `SPEC.md`
Behavior:
- report the feature as malformed
- do not invent status
- recommend repairing the spec first

### Case: `VERIFY.md` does not exist during `/vibe-done`
Behavior:
- create it from `SPEC.md`
- then record the completion state

### Case: templates are still blank placeholders
Behavior:
- ask 2–3 specific setup questions
- use the answers to help generate initial content

### Case: premature `/vibe-done`
Behavior:
- default to partially complete
- write what is done and what remains
- keep the feature active

### Case: `SESSION_LOG.md` exceeds cap
Behavior:
- keep newest 10 entries in `SESSION_LOG.md`
- move older entries to `SESSION_ARCHIVE.md`
- preserve chronological order

## Supporting rules

### Blank placeholder rule
A file counts as a blank placeholder if it contains only template headings, instructional text, or placeholder markers with no project-specific content.

### Most-recent feature rule
When suggesting a likely feature to resume, use the most recently modified feature directory.

## Acceptance criteria

- [ ] all listed broken states produce deterministic recovery
- [ ] Claude does not silently guess when ambiguity exists
- [ ] broken active feature references are handled cleanly
- [ ] premature `/vibe-done` keeps the feature active
- [ ] missing `VERIFY.md` is handled automatically
- [ ] session log rollover works as specified

## Verification

- test missing `.claude/active_feature`
- test empty `.claude/active_feature`
- test invalid `.claude/active_feature`
- test multiple feature folders with no active feature
- test missing `SPEC.md`
- test missing `VERIFY.md`
- test `/vibe-done` on partial work
- test session log rollover
