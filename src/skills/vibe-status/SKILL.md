---
name: vibe-status
description: Check the current status of the active feature or all features. Use when the user wants a progress report.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
---

# /vibe-status — Check Feature Progress

You are helping a vibe coder understand where their project stands. Your job is to give an honest, actionable progress report.

## Steps

### 1. Find the active feature
- Read `.claude/active_feature` to find the current feature ID.

### 2a. If there IS an active feature
- Read `features/<feature-id>/SPEC.md` to get the acceptance criteria.
- Read `features/<feature-id>/VERIFY.md` if it exists to see what's been verified.
- Compare the acceptance criteria against verification notes.
- Report in this format:

> **Feature:** [name] — [goal]
>
> **Done and verified:**
> - [x] [criterion] — [how it was verified]
>
> **Built but not verified:**
> - [ ] [criterion] — appears implemented but not yet tested
>
> **Still open:**
> - [ ] [criterion] — not yet built
>
> **Blockers or risks:**
> - [anything noted in spec or discovered during work]

### 2b. If there is NO active feature
- Scan all `features/FEATURE-*/` folders.
- For each, check if VERIFY.md exists and its status (Complete/Partial/Blocked).
- Report a summary table:

> **All features:**
> | Feature | Status | Notes |
> |---------|--------|-------|
> | FEATURE-001-auth-login | Complete | Verified 2026-03-15 |
> | FEATURE-002-dashboard | Partial | 3 of 5 criteria done |
> | FEATURE-003-settings | Open | Spec written, no work started |

Then suggest: "Use `/vibe-start` to begin a new feature, or tell me which feature to resume."

## Rules
- Be honest. If something isn't verified, say so. Don't assume it works.
- Keep the report scannable — use the structured format above.
- This is a read-only command. Do not modify any files.
- If SPEC.md is missing for a feature folder, note it as "No spec found."
