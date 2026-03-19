---
name: vibe-status
description: Check the current status of the active feature or all features. Use when the user wants a progress report.
disable-model-invocation: true
allowed-tools: Read, Glob
---

# /vibe-status — Check Feature Progress

You are giving a vibe coder an honest progress report. Be structured and direct.

## Feature scan rule
When scanning `features/`, only consider directories strictly matching `FEATURE-NNN-slug` (pattern: `FEATURE-` + 3 digits + `-` + lowercase slug). Ignore all other directories and files.

## Steps

### 1. Find the active feature
Read `.claude/active_feature`.

**If it contains a feature ID but that folder does not exist:**
> ⚠️ VibeCode Recovery: Active feature reference is broken — `FEATURE-NNN-slug` doesn't exist.
> Use `/vibe-resume` to repair the active feature state.
Stop here.

**If it contains a feature ID, the folder exists, but there is no `SPEC.md`:**
> ⚠️ VibeCode Recovery: Feature `FEATURE-NNN-slug` has no SPEC.md — it's malformed. Cannot report status without acceptance criteria.
> Use `/vibe-resume` to repair or reset this state.
Stop here.

### 2a. Active feature exists with SPEC.md
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
Scan `features/` using the feature scan rule above.

If no valid folders exist:
> "No features have been started yet. Use `/vibe-start` to begin one."

If valid folders exist, suggest the highest-numbered feature as the likely active one. Show at most 3 candidates (highest-numbered first, up to 2 others). Do not list all features.

For each displayed feature:
- If SPEC.md exists: show status (Complete if VERIFY.md present and status=Complete, Partial if VERIFY.md present with partial status, Open otherwise)
- If SPEC.md missing: show "No spec — malformed"

> **Active feature:** None
>
> **Most likely to resume:** `FEATURE-NNN-slug` — [goal from SPEC.md, or "No spec — malformed"]
>
> [up to 2 other candidates if they exist]
>
> **Next step:** Use `/vibe-resume` to select a feature, or `/vibe-start` to begin a new one.

## Rules
- Read-only. Never write or modify files.
- Never say the `features/` folder is missing if it exists but is empty.
- End every response with exactly one next step.
- Do not invent status for malformed features.
