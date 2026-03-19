# FEATURE-005-automated-smoke-tests

## Goal

Add a deterministic, pure-Python automated smoke-test harness that validates the structural integrity of VibeCode OS.

This feature tests:
- the installer
- idempotency
- managed skill updates
- template integrity
- file layout invariants

It does **not** attempt to automate interactive Claude skill behavior.

## Why this feature exists

Manual QA has validated the product, but repeatedly testing the installer and file-state behavior by hand is slow and error-prone.

The project now needs a fast structural test suite that answers:

- did `install.py` create the correct files?
- did a second run preserve user data?
- did managed skills update correctly when source content changed?
- do templates still contain the markers required by the skills?
- is the repo layout still compatible with the current workflow?

This feature improves confidence without depending on interactive Claude sessions.

## In scope

- add a pure-Python smoke test runner
- add reusable test helpers
- create temporary test repos programmatically
- validate installed file layout
- validate installer idempotency
- validate managed skill update logic
- validate template marker presence
- document how to run the smoke suite
- document the split between automated structural tests and manual skill QA

## Out of scope

- end-to-end automation of interactive Claude skills
- parsing or judging LLM responses
- browser automation
- IDE automation
- plugin packaging
- CI setup
- performance benchmarking
- exhaustive workflow simulation

## Files to create

- `tests/smoke/run_smoke_tests.py`
- `tests/smoke/helpers.py`
- `tests/smoke/README.md`

## Files to modify

- `README.md` — add automated smoke test section and clarify manual-vs-automated test split

## Design principles

### 1. Test the framework, not the AI
The smoke suite validates deterministic behavior in `install.py`, installed files, templates, and managed skill updates. Do not simulate or mock interactive Claude skill execution.

### 2. Programmatic fixtures only
Do not create or maintain a static `tests/smoke/fixtures/` tree. Each test creates its own temporary repo using `tempfile`, `pathlib`, `os`, and `shutil`.

### 3. Fast and rerunnable
The suite completes in a few seconds. Each scenario runs in fresh temporary state by default. Failed runs do not leave clutter unless `--keep-temp` is used.

### 4. Deterministic assertions
Prefer assertions on file existence, content equality, content preservation, directory existence, installer output categories, and exact presence of `[TODO:` markers.

### 5. Minimal dependencies
Python stdlib only. No pytest, no third-party CLI wrappers, no snapshot libraries.

### 6. Clear failure reporting
Each scenario reports: scenario name, PASS/FAIL/SKIP, one-line reason. The suite exits non-zero if any required scenario fails.

## Required scenarios

### Scenario 1 — Installer first run
Verify first install creates the expected structure. All 10 paths must exist, `features/` must be empty, `.claude/active_feature` must be empty, installed skills must match source.

### Scenario 2 — Installer second run / idempotency
Self-contained. Runs first install, modifies user data (full replacement + partial edit), snapshots all user files, runs installer again. All user data must be preserved exactly.

### Scenario 3 — Managed skill updates
Self-contained. Runs first install, modifies one installed skill, runs installer again. Modified skill must be updated, others unchanged, user data preserved.

### Scenario 4 — Template marker validation
Reads source templates directly. Each must contain `[TODO:` (hard fail). Line count > 30 is warning only.

### Scenario 5 — Optional Claude CLI probe
Runs `claude --version`. SKIP if unavailable, FAIL only with `--strict-cli`.

## Acceptance criteria

- [ ] one command runs the smoke suite
- [ ] the suite exits non-zero on required failures
- [ ] the suite validates installer first run, second run, managed skill updates, and template markers
- [ ] each scenario runs in fresh temp state
- [ ] no scenario modifies the source repo
- [ ] subprocess timeouts prevent hangs
- [ ] README.md explains automated smoke tests and their limits
- [ ] tests/smoke/README.md explains scenario purpose and debugging
