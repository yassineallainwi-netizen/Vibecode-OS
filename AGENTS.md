# Agent Operating Manual

## Mission
Build VibeCode OS incrementally, one well-scoped task at a time, using the same structured process the product teaches.

## Required Reading Before Any Change
Always read:
1. `PROJECT_CONTEXT.md`
2. `DECISIONS.md`
3. `SESSION_LOG.md` (latest entry)
4. The relevant feature's `SPEC.md` if working on a feature

## Working Rules
- Work one task at a time
- No code before the spec is written and reviewed
- Keep changes small and reviewable
- State assumptions explicitly
- Stop when uncertainty is material — ask rather than guess

## Never Do
- Do not invent requirements not in the spec
- Do not modify unrelated files
- Do not add dependencies (stdlib only)
- Do not claim done without verification evidence
- Do not build "nice to have" features before core is solid
- Do not over-engineer — this is a skill pack, not a platform

## Required Output For Each Task
Before implementation:
1. Task restatement
2. Files to create or change
3. Risks and assumptions

After implementation:
1. Summary of what changed
2. How to verify it works
3. Known limitations
4. Files updated

## Coding Rules
- Python: stdlib only, 3.8+ compatible
- Skills: plain markdown, clear command structure
- All files must be readable by a non-engineer
- Prefer clarity over cleverness
- No frameworks, no build steps, no compilation

## Completion Rule
A task is complete only when:
- It does what the spec says
- It can be verified by running a simple test
- Relevant docs are updated
- The session log records what happened
