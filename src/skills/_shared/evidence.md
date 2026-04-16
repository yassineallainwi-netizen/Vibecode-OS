# VibeCode OS — Evidence Model

Single source of truth for the 5-label evidence system used across all skills.
Reference this file instead of duplicating the model in each skill.

---

## Evidence labels (weakest to strongest)

| Label | When to use | Display strength |
|-------|-------------|-----------------|
| `spec_expected` | Criterion expected to be met based on spec alone — no verification done | low |
| `user_reported` | User claims it works — no command run, no file inspection | medium |
| `repo_observed` | Command ran with exit 0 but no test assertions (empty output or 0 tests), OR file inspection confirms the change is present | high |
| `command_verified` | Command ran, exit 0, tests passed (tests_run > 0, tests_failed == 0) | high |
| `command_failed` | Command ran but exited non-zero, OR tests ran but tests_failed > 0 — this is evidence of failure, NOT success | low |

---

## Classification logic (`classify_evidence`)

Given: `exit_code`, `output`, `triage` (from `triage_log(output)`)

```
if exit_code != 0:
    return "command_failed"

if output is empty:
    return "repo_observed"

if triage.tests_run == 0:
    return "repo_observed"

if triage.tests_failed > 0:
    return "command_failed"

return "command_verified"
```

**Critical:** `command_failed` maps to strength "low", never "high". A failing run is not positive evidence.

---

## Strength → display mapping

| Internal state | Display | Example |
|----------------|---------|---------|
| fresh_strong (command_verified) | high | ✅ Tests passed: 94/94 |
| strong (repo_observed) | high | ✅ File change confirmed |
| partial (user_reported) | medium | ⚠️ User reported working |
| weak (spec_expected, command_failed) | low | ❌ Command failed / Assumed from spec |
| none | none | — Not verified |

---

## Using the evidence model in skills

When writing to VERIFY.md, label each criterion with exactly one evidence label:
```
- [x] Login form submits `[command_verified]`
- [ ] Error state shown on 401 `[user_reported]`
- [ ] Password reset email sent `[spec_expected]`
```

When displaying a summary, use `evidence_strength_display(labels)` to get the aggregate strength across all criteria in a feature.

---

## Related

- Implementation: `src/helpers/verification.py` — `classify_evidence`, `evidence_strength_display`, `LABEL_TO_STATE`
- Tests: `tests/smoke/test_helpers.py` — `test_nonzero_exit_returns_command_failed`, `test_command_failed_maps_to_weak_strength`
