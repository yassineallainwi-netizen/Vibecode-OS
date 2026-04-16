# Feature: Automated Smoke Tests

- ID: FEATURE-005-automated-smoke-tests
- Status: Closed
- Date locked: 2026-03-18
- Complexity: normal
- Change kind: behavioral

## Goal
Add a deterministic, pure-Python smoke-test harness that validates the structural integrity of VibeCode OS (installer, idempotency, managed updates, template markers, file layout), freeing manual QA to focus on interactive skill behaviour.

## Touches
- tests/smoke/run_smoke_tests.py
- tests/smoke/helpers.py
- tests/smoke/README.md
- README.md

## Acceptance criteria
- [x] [verify=cmd] `python tests/smoke/run_smoke_tests.py` runs and exits 0 on a clean repo
- [x] [verify=cmd] Suite exits non-zero when any required scenario fails
- [x] [verify=cmd] Scenario: installer first run — all 10 paths created, skills match source
- [x] [verify=cmd] Scenario: installer second run — all user data preserved (full replacement + partial edit)
- [x] [verify=cmd] Scenario: managed skill updates — modified skill updated, unchanged skills and user data untouched
- [x] [verify=cmd] Scenario: template marker validation — every template contains `[TODO:` marker (hard fail); line count > 30 is warning only
- [x] [verify=cmd] Scenario: Claude CLI probe — SKIP if unavailable; FAIL only with `--strict-cli` flag
- [x] [verify=cmd] Each scenario runs in a fresh temp directory (no shared state between scenarios)
- [x] [verify=cmd] No scenario modifies the source repository
- [x] [verify=cmd] Subprocess timeouts prevent hangs (each installer call bounded)
- [x] [verify=repo] `tests/smoke/README.md` explains what the suite tests and what it does NOT test (interactive skill behaviour)

## Verification plan
- AC-1: `python tests/smoke/run_smoke_tests.py` — exit 0, all scenarios PASS printed.
- AC-2: Introduced a deliberate failure in one scenario; confirmed exit code 1.
- AC-3: Ran installer_first_run scenario; confirmed all 10 paths validated.
- AC-4: Ran installer_second_run with modified PROJECT_CONTEXT.md and partial AGENTS.md edit; both preserved.
- AC-5: Wrote "MODIFIED" to one installed skill; ran managed_skill_updates; update detected, others unchanged.
- AC-6: Ran template_markers; confirmed `[TODO:` check hard-fails, line count is warning only.
- AC-7: Ran claude_probe without CLI; confirmed SKIP output. Ran with `--strict-cli`; confirmed FAIL.
- AC-8: Inspected temp directory cleanup; each scenario used a separate temp path, all cleaned up.
- AC-9: Ran full suite; confirmed source repo `git status` unchanged after completion.
- AC-10: Added a sleep-forever subprocess to one scenario; confirmed timeout fired within bound.
- AC-11: Read tests/smoke/README.md; confirmed scope limitations documented.

## Out of scope
- End-to-end automation of interactive Claude skills (LLM behaviour cannot be deterministically tested)
- Parsing or evaluating LLM response quality
- CI/CD integration (tests can be used by CI but no pipeline added in this feature)
- Performance benchmarking

## Known risks
- Tests validate structural correctness only, not skill UX or LLM reasoning
- Scenarios must remain fast (complete in seconds) or developers will skip running them
