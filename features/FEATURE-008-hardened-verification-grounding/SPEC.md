# Feature: Hardened Verification Grounding

- ID: FEATURE-008-verification-grounding
- Status: Closed
- Date locked: 2026-03-18
- Complexity: complex
- Change kind: mixed

## Goal
Make completion claims materially more trustworthy by adding evidence labels, command approval persistence, allow-list validation, weak-success downgrade, and an audit trail — without adding unnecessary overhead.

## Touches
- src/helpers/verification.py
- src/helpers/approval.py
- src/skills/vibe-done/SKILL.md
- src/skills/vibe-start/SKILL.md
- src/skills/vibe-resume/SKILL.md
- src/skills/vibe-status/SKILL.md

## Acceptance criteria
- [x] [verify=spec] Evidence labels (command_verified, repo_observed, user_reported, spec_expected) present on all criteria in new VERIFY.md files
- [x] [verify=spec] Verification strength derived from ordered label states — none / weak / partial / strong / fresh_strong — not percentages
- [x] [verify=cmd] Command allow-list validation enforced; shell metacharacters (`|`, `;`, `$()`, `>`, `sudo`) rejected
- [x] [verify=spec] First-run approval prompt on new or changed verification commands before execution
- [x] [verify=spec] No approval re-prompt on identical approved commands (checksum-based)
- [x] [verify=cmd] `.claude/approved_commands.json` created on first install with valid schema
- [x] [verify=cmd] `.claude/approved_commands.json` preserved (not overwritten) on second install
- [x] [verify=cmd] Weak-success cases downgraded: 0 tests run, empty output, hostile formatting all produce repo_observed or lower
- [x] [verify=repo] ANSI escape sequences stripped from command output before evidence classification
- [x] [verify=repo] Audit trail HTML comment block written to VERIFY.md after each verification run
- [x] [verify=spec] Verification readiness line added to `/vibe-resume` War Room manifest
- [x] [verify=spec] `/vibe-start` proposes verification commands by scanning repo for test runner evidence
- [x] [verify=spec] Git Ghost v2 includes a verification result line in the commit message block
- [x] [verify=spec] `/vibe-status` shows a verification strength field
- [x] [verify=cmd] All existing smoke tests still pass

## Verification plan
- AC-1: Read vibe-done SKILL.md evidence label section; all four labels defined and described.
- AC-2: Read verification.py LABEL_TO_STATE and EVIDENCE_DISPLAY mappings; ordered states confirmed.
- AC-3: `python tests/smoke/run_smoke_tests.py --scenario command_validation_rejects_metacharacters` — exit 0.
- AC-4: Read approval section in vibe-done SKILL.md; first-run prompt rule confirmed.
- AC-5: Read is_approved() checksum logic in approval.py; re-prompt suppressed on match confirmed.
- AC-6: `python tests/smoke/run_smoke_tests.py --scenario approved_commands_created` — exit 0.
- AC-7: `python tests/smoke/run_smoke_tests.py --scenario approved_commands_preserved` — exit 0.
- AC-8: `python tests/smoke/run_smoke_tests.py --scenario downgrade_on_zero_tests` — exit 0; label confirmed as repo_observed or lower.
- AC-9: `python tests/smoke/run_smoke_tests.py --scenario ansi_stripping` — exit 0.
- AC-10: Read vibe-done SKILL.md audit trail section; HTML comment format in VERIFY.md confirmed.
- AC-11: Read vibe-resume SKILL.md War Room manifest; verification_readiness field confirmed.
- AC-12: Read vibe-start SKILL.md step 6.5; repo scan for test runner evidence confirmed.
- AC-13: Read Git Ghost block in vibe-done SKILL.md; verification line present in commit message template.
- AC-14: Read vibe-status SKILL.md report section; Verification strength field confirmed.
- AC-15: `python tests/smoke/run_smoke_tests.py` — exit 0, all scenarios pass.

## Out of scope
- Gating feature completion on config file completeness (only on non-zero command exits)
- Storing approval state in shared project files (kept in `.claude/approved_commands.json`)
- Executing any command not on the allow-list

## Known risks
- approved_commands.json may be deleted manually; missing file must be handled gracefully (create fresh)
- ANSI stripping must not corrupt legitimate output (only escape sequences removed)
- 0-test output is common on empty suites; downgrade must explain why, not silently fail
