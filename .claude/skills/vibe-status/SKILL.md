---
name: vibe-status
description: Check the current status of the active feature or all features. Use when the user wants a progress report.
disable-model-invocation: true
allowed-tools: Read, Glob
---

# /vibe-status — Check Feature Progress

You are giving a vibe coder an honest progress report. Be structured and direct.

## Feature scan rule
Glob `**/SPEC.md`, filter to `features/FEATURE-NNN-slug/SPEC.md` (pattern: `FEATURE-` + 3 digits + `-` + lowercase slug). Ignore SPEC.md outside this pattern.

## Security rule
Validate `.claude/active_feature` format before use: must match `^FEATURE-\d{3}-[a-z0-9-]+$` or be empty.

## Steps

### 1. Find the active feature
Read `.claude/active_feature`. Validate format.

**If malformed format:**
> ⚠️ VibeCode Recovery: active_feature contains an invalid value. Use `/vibe-resume` to repair.
Stop here.

**If contains a valid feature ID but folder does not exist:**
> ⚠️ VibeCode Recovery: Active feature reference is broken — `FEATURE-NNN-slug` doesn't exist.
> Use `/vibe-resume` to repair the active feature state.
Stop here.

**If contains a valid feature ID, folder exists, but no SPEC.md:**
> ⚠️ VibeCode Recovery: Feature `FEATURE-NNN-slug` has no SPEC.md — it's malformed. Cannot report status without acceptance criteria.
> Use `/vibe-resume` to repair or reset this state.
Stop here.

### 2a. Active feature exists with SPEC.md
Read `features/<feature-id>/SPEC.md` and `features/<feature-id>/VERIFY.md` (if it exists).

**Determine Mode:**
- No VERIFY.md → `building`
- VERIFY.md exists, Status = "Partially Complete" or unchecked criteria remain → `verifying`
- VERIFY.md exists, Status = "Complete" → `closing`

**Determine Risk flags** (grounded only — omit if no evidence):
- "No verification evidence" — no VERIFY.md exists and feature has been open for a while (SESSION_LOG shows prior sessions)
- "Unspecced changes" — if user explicitly mentions working on files outside what SPEC.md describes
- "Stale session" — SESSION_LOG latest entry date is significantly older than today

Always report in this exact structure:

> **Feature goal:** [one-sentence goal from SPEC.md]
>
> **Mode:** [building / verifying / closing]
>
> **Risk flags:** [grounded flags, or "None"]
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

### Criteria visibility rule
- Show criteria that appear complete (supported by VERIFY.md evidence or file changes)
- Show criteria unchecked (no work done yet)
- Show criteria unverified (work may have been done but no explicit evidence): use `[?]` marker

### Default-to-unverified rule
If completion of a criterion cannot be confidently inferred from VERIFY.md entries, file changes, or direct user evidence: mark as **unverified**, not complete:
> - [?] [criterion — unverified, no explicit evidence]

Do not assume criteria are satisfied based on conversational guessing.

### Concision rule
- Do not dump the full spec
- Do not create giant tables for small features
- Keep the report compact and actionable
- Fail closed when structural parsing is ambiguous (omit the ambiguous field rather than guessing)

### 2b. No active feature
Glob `**/SPEC.md` and apply the feature scan rule.

If no valid folders:
> "No features have been started yet. Use `/vibe-start` to begin one."

If valid folders exist, suggest the highest-numbered feature as likely active. Show at most 3 candidates (highest first).

For each: Complete if VERIFY.md present and status=Complete, Partial if VERIFY.md present with partial status, Open otherwise.

> **Active feature:** None
>
> **Most likely to resume:** `FEATURE-NNN-slug` — [goal from SPEC.md, or "No spec — malformed"]
>
> [up to 2 other candidates]
>
> **Next step:** Use `/vibe-resume` to select a feature, or `/vibe-start` to begin a new one.

## Rules
- Read-only. Never write or modify files.
- Never say the `features/` folder is missing if it exists but is empty.
- End every response with exactly one next step.
- Do not invent status for malformed features.
- Fail closed when structural parsing is ambiguous.
