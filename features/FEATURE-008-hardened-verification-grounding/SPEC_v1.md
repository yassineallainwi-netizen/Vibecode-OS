# Feature: Hardened Verification Grounding

## Goal
Make VibeCode OS verification explicit, bounded, evidence-graded, and low-friction so completion claims are materially more trustworthy without adding unnecessary approval overhead.

## What it should do
- Tag every acceptance criterion with an evidence label: command_verified, repo_observed, user_reported, spec_expected
- Persist first-run command approval in .claude/approved_commands.json; re-prompt only on command change, repo identity change, or file corruption
- Enforce strict command allow-list before execution: no shell metacharacters, no sudo/su, no absolute executable paths; allow trusted PATH-resolved tools
- Run commands in isolated subprocesses with trusted env vars only, non-root, 30s timeout, 50KB output cap, ANSI stripping
- Downgrade weak success: 0 tests detected, empty output, hostile formatting, truncated output → not command_verified
- Upgrade VERIFY.md with evidence labels, verification summary, and machine-readable audit trail in HTML comment
- Add verification War Room line to /vibe-resume manifest (readiness, strength, last command, freshness, blocking failure, safest next action)
- Propose verification commands from repo evidence in /vibe-start (exact package.json scripts, pytest configs, Makefile targets)
- Add Git Ghost v2: include verification summary line in commit suggestion
- Auto-trigger mini verification-resume on repeated failures, repeated downgraded successes, or cache invalidation thrash
- /vibe-status: show Verification strength (high/medium/low/none) derived from ordered evidence states

## What it should NOT do
- Gate completion on configuration completeness — only gate on executed non-zero verification failure
- Ask user to manually explain commands if repo evidence supports a clear proposal
- Store approval state in active-feature state or project-visible shared files (use .claude/approved_commands.json)
- Execute commands outside the approved allow-list
- Replace existing criteria with percentage thresholds — use ordered states: none → weak → partial → strong → fresh_strong

## Acceptance Criteria
- [ ] Evidence labels present on all criteria in VERIFY.md
- [ ] Verification strength derived from ordered states, not percentages
- [ ] Command allow-list validation enforced; shell metacharacters rejected
- [ ] First-run approval prompt on new/changed commands
- [ ] No approval re-prompt on identical approved commands
- [ ] Approved_commands.json created on first install
- [ ] Approved_commands.json preserved on second install
- [ ] Weak success cases downgraded (0 tests, empty output, hostile formatting)
- [ ] ANSI stripping applied before evaluation
- [ ] Audit trail block present in VERIFY.md (HTML comment)
- [ ] Verification War Room line added to /vibe-resume manifest
- [ ] /vibe-start proposes verification commands from repo evidence
- [ ] Git Ghost v2 includes verification line
- [ ] /vibe-status shows verification strength field
- [ ] All existing smoke tests still pass

## Risks and edge cases
- Command approval file may be missing after manual delete — handle gracefully (treat as new, re-prompt)
- ANSI stripping must not corrupt legitimate output (only strip escape sequences, not printable chars)
- Approval record checksum mismatch should trigger re-prompt, not crash
- 0-test output is common in some ecosystems (e.g., first test run on empty suite) — downgrade clearly but explain why
