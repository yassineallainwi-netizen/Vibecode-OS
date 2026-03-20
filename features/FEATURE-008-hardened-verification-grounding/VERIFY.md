# Verification: Hardened Verification Grounding

## What was built
Added evidence model (4 labels + ordered states) to /vibe-done, command approval via .claude/approved_commands.json, strict allow-list validation, weak-success downgrade rules, evidence-graded VERIFY.md format with audit trail block, verification War Room line in /vibe-resume, verification command proposals in /vibe-start, Verification strength in /vibe-status, Git Ghost v2 with verification summary, mini verification-resume trigger. Two helper scripts: src/helpers/verification.py (evidence model, command validation, ANSI stripping, output triage, audit trail) and src/helpers/approval.py (approval persistence, checksum validation).

## Acceptance criteria
- [x] Evidence labels present on all criteria in VERIFY.md — evidence label format documented in step 5
- [x] Verification strength derived from ordered states, not percentages — ordered states (none/weak/partial/strong/fresh_strong) with display mapping
- [x] Command allow-list validation enforced; shell metacharacters rejected — smoke test passes: dangerous commands rejected
- [x] First-run approval prompt on new/changed commands — approval rule added to vibe-done
- [x] No approval re-prompt on identical approved commands — is_approved() checks cmd_hash + repo_id
- [x] Approved_commands.json created on first install — install.py updated; smoke test passes
- [x] Approved_commands.json preserved on second install — never-overwrite pattern; smoke test passes
- [x] Weak success cases downgraded (0 tests, empty output, hostile formatting) — classify_evidence() logic; smoke test passes
- [x] ANSI stripping applied before evaluation — strip_ansi() in verification.py; smoke test passes
- [x] Audit trail block present in VERIFY.md (HTML comment) — documented in step 5 format
- [x] Verification War Room line added to /vibe-resume manifest — verification line added after context pointer
- [x] /vibe-start proposes verification commands from repo evidence — step 6.5 added
- [x] Git Ghost v2 includes verification line — commit suggestion block updated
- [x] /vibe-status shows verification strength field — verification strength added to report structure
- [x] All existing smoke tests still pass — 15/15 pass (including 5 new 008 scenarios)

## Known gaps
- Command approval and execution are instruction-based; actual approval prompts require behavioral testing with live Claude
- ANSI stripping and output triage are tested structurally; edge cases (streaming output, very large logs) require manual QA
- Audit trail rows are added by prompt instruction; structural tests verify the format spec but not runtime population

## Status
Complete
