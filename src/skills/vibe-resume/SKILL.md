---
name: vibe-resume
description: Resume work from a previous session. Use at the start of a new session to restore context.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Edit
---

# /vibe-resume — Resume a Previous Session

You are restoring session context for a vibe coder. Read the minimum needed, then give a focused summary so they can start working immediately.

## Steps

### 1. Read project context
Read `PROJECT_CONTEXT.md`.

If it's missing or still a blank template (only placeholder text, no real content), say:
> "No project context yet. What is this project and what's it built with?"
Then create `PROJECT_CONTEXT.md` from their answer before continuing.

### 2. Read session log
Read `SESSION_LOG.md` for the most recent session summary.

### 3. Read key decisions
Read `DECISIONS.md` for any decisions marked as active or recent.

### 4. Find the active feature
Read `.claude/active_feature`.
- If it contains a feature ID, read `features/<feature-id>/SPEC.md`.
- If it's empty or missing, note that no feature is active — do not scan the repo.

### 5. Present the summary
Always use this exact structure:

> **Project:** [name and one-line description]
>
> **Current state:** [what was happening as of the last session — date and summary]
>
> **Active feature:** [feature ID and goal, or "None"]
>
> **Important decisions:** [2–3 key decisions from DECISIONS.md that affect current work, or "None logged"]
>
> **Next step:** [one concrete action — e.g., "Continue building X" or "Run /vibe-start to begin your first feature"]

## Rules
- No filler. Lead with facts.
- Never ask the user to re-explain their project.
- Do not scan `features/` unless `.claude/active_feature` is missing (that's handled by /vibe-start or /vibe-status).
- End every response with exactly one recommended next step.
