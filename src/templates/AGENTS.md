<!-- vibecode:agents:v2 -->
# Agent Operating Manual

## Mission
Build this project incrementally, one feature at a time, using the VibeCode OS workflow.

## Required Reading
Before any change, read: `PROJECT_CONTEXT.md`, `SESSION_LOG.md` (latest entry), and the active feature's `SPEC.md`.

## Workflow Mode
Commands available in this project:
- `/vibe-start` — spec and begin a new feature
- `/vibe-resume` — restore session context (run at the start of every session)
- `/vibe-status` — check active feature progress
- `/vibe-done` — verify and close the active feature

## Command Registry
verify_cmd: [TODO: e.g. "pytest" or "npm test" or "flutter test"]
test_cmd: [TODO: e.g. "pytest tests/" or "npm run test"]
lint_cmd: [TODO: e.g. "flake8 src/" or "npm run lint"]
typecheck_cmd: [TODO: e.g. "mypy src/" or "npx tsc --noEmit"]
build_cmd: [TODO: e.g. "npm run build" or "flutter build apk"]

## Working Rules
- Work one task at a time
- No code before the spec is written and reviewed
- Keep changes small and reviewable
- Do not invent requirements not in the spec
- Do not claim done without verification evidence
- Stop when uncertain — ask rather than guess

## Project-specific rules

### Tech constraints
[TODO: e.g. "Python 3.10+, stdlib only", "Flutter + Dart, no web target"]

### Off-limits areas
[TODO: e.g. "never modify auth.py directly", "don't change the DB schema without a migration"]

### Code style preferences
[TODO: e.g. "use single quotes in JS", "keep functions under 30 lines", "French UI labels, English identifiers"]

### Testing expectations
[TODO: e.g. "run pytest before marking done", "no tests needed for prototyping phase"]
