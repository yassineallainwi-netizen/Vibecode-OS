# Smoke Tests

Structural smoke tests for VibeCode OS. These validate the installer and file integrity — not interactive Claude skill behavior.

## What is tested

- **installer_first_run** — first install creates all expected files, skills match source
- **installer_second_run** — second install preserves user data (full replacement + partial edits)
- **managed_skill_updates** — modified skills are refreshed, unchanged skills are skipped
- **template_markers** — source templates contain `[TODO:` markers for blank-state detection
- **claude_probe** (optional) — checks if the Claude CLI is available locally

## What is NOT tested

Interactive Claude skill behavior (`/vibe-resume`, `/vibe-start`, `/vibe-status`, `/vibe-done`) requires manual QA. See the checklist in the project README.

## How scenarios are isolated

Each scenario creates its own temporary directory via `tempfile.mkdtemp`. No scenario reuses state from another. No scenario modifies the source repo.

## Running

```bash
python tests/smoke/run_smoke_tests.py                 # all scenarios
python tests/smoke/run_smoke_tests.py --scenario X    # one scenario only
python tests/smoke/run_smoke_tests.py --verbose        # detail on pass
python tests/smoke/run_smoke_tests.py --keep-temp      # preserve temp repos
python tests/smoke/run_smoke_tests.py --strict-cli     # require Claude CLI
```

## Debugging failures

Use `--keep-temp` to preserve the temporary repo after a failure. The temp path is printed in the output. Inspect the installed files to understand what went wrong.

Use `--verbose` to see detailed pass messages and full tracebacks on unexpected errors.
