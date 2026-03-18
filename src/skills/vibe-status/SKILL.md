---
name: vibe-status
description: Check the current status of the active feature or all features. Use when the user wants a progress report.
disable-model-invocation: true
allowed-tools: Read, Glob
---

# /vibe-status — Check Feature Progress

You are giving a vibe coder an honest progress report. Be structured and direct.

## Steps

### 1. Find the active feature
Read `.claude/active_feature`.

### 2a. Active feature exists
Read `features/<feature-id>/SPEC.md` and `features/<feature-id>/VERIFY.md` (if it exists).

Always report in this exact structure:

> **Feature goal:** [one-sentence goal from SPEC.md]
>
> **Completed:**
> - [x] [criterion — how verified, or "built but not tested"]
>
> **Missing:**
> - [ ] [criterion not yet built]
>
> **Risks / unknowns:**
> - [anything from spec or discovered during work, or "None"]
>
> **Next step:** [one concrete action]

### 2b. No active feature
Scan `features/FEATURE-*/` folders.

If no folders exist or the folder is empty:
> "No features have been started yet. Use `/vibe-start` to begin one."

If folders exist, report a summary table:

> | Feature | Status | Notes |
> |---------|--------|-------|
> | FEATURE-001-auth-login | Complete | Verified 2026-03-15 |
> | FEATURE-002-dashboard | Partial | 3 of 5 criteria done |
> | FEATURE-003-settings | Open | Spec written, not started |
>
> **Next step:** [suggest which feature to resume or use `/vibe-start` for a new one]

## Rules
- Read-only. Never write or modify files.
- Never say the `features/` folder is missing if it exists but is empty.
- If SPEC.md is missing for a folder, mark it as "No spec — malformed."
- End every response with exactly one next step.
