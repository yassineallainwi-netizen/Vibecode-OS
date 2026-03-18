---
name: vibe-resume
description: Resume work from a previous session. Use at the start of a new session to restore context.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Edit
---

# /vibe-resume — Resume a Previous Session

You are helping a vibe coder pick up where they left off. Your job is to read all context files and give a clear, actionable summary so the user is productive within 30 seconds.

## Steps

### 1. Read project context
- Read `PROJECT_CONTEXT.md` to understand the project.
- If it doesn't exist or is empty, tell the user: "I don't see a PROJECT_CONTEXT.md yet. Let's set one up — what is this project and what's it built with?" Then create it from their answers.

### 2. Read session history
- Read `SESSION_LOG.md` to see what happened in previous sessions.
- If it doesn't exist, note that this appears to be the first session.

### 3. Find the active feature
- Read `.claude/active_feature` to find the current feature ID.
- If the file exists and contains a feature ID, read that feature's `SPEC.md` and `VERIFY.md` (if it exists) from `features/<feature-id>/`.
- If the file is empty or missing, scan `features/` for any feature folders and check which ones lack a VERIFY.md (likely still in progress). If there's ambiguity, ask the user which feature to resume.

### 4. Summarize to the user
Present a concise summary:

> **Project:** [name from PROJECT_CONTEXT.md]
> **Last session:** [date and summary from SESSION_LOG.md]
> **Active feature:** [feature name and goal from SPEC.md]
> **Completed:** [what's been done/verified]
> **Still open:** [remaining acceptance criteria or tasks]
> **Recommended next step:** [your suggestion for what to work on first]

If there's no active feature, say so and suggest either resuming an incomplete feature or starting a new one with `/vibe-start`.

### 5. Ready to work
After the summary, be ready to start working. Don't ask for permission to begin — the user called `/vibe-resume` because they want to get going.

## Rules
- Be concise. The summary should be scannable in under 10 seconds.
- Recommend a concrete next step, not a vague "continue working."
- If a feature was never formally closed (no VERIFY.md, but work was done), mention this and suggest either continuing it or closing it with `/vibe-done`.
- Never ask the user to re-explain their project. That's what the context files are for.
