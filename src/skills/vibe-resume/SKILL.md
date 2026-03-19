---
name: vibe-resume
description: Resume work from a previous session. Use at the start of a new session to restore context.
disable-model-invocation: true
allowed-tools: Read, Write, Glob
---

# /vibe-resume — Resume a Previous Session

You are restoring session context for a vibe coder. Read existing files and summarize what you find. Never invent, draft, or guess project details.

## Read-only rule
This command is read-only. The only write you are allowed to perform is clearing `.claude/active_feature` when it contains a broken reference. Never write or modify `PROJECT_CONTEXT.md`, `AGENTS.md`, `DECISIONS.md`, `SESSION_LOG.md`, or any feature file. Never run Bash or git commands.

## Blank placeholder rule
A file is a blank placeholder if it contains only headings, empty lines, or lines containing `[TODO:` or `[TEMPLATE]`. Any project-specific content means the file is real.

## Steps

### 1. Read project context
Read `PROJECT_CONTEXT.md`.

If it's missing or a blank placeholder, do not draft content. Instead ask 2–3 focused questions:
> "I don't see project context yet. To get started:
> 1. What is this project and what problem does it solve?
> 2. What's it built with?
> 3. What's the current state — what works, what's broken, what's next?"

Wait for the user to answer, then continue to step 2 using their answers as context for the summary only. Do not write anything.

### 2. Read session log
Read `SESSION_LOG.md`. Note the most recent session entry if one exists.

### 3. Read key decisions
Read `DECISIONS.md`. Note any decisions that are not blank placeholders.

### 4. Find the active feature
Read `.claude/active_feature`.

**If the file is missing or empty:**
Scan `features/` for directories strictly matching `FEATURE-NNN-slug` (pattern: `FEATURE-` + 3 digits + `-` + lowercase slug). Ignore all other directories or files.
- 0 valid folders → "No features have been started yet. Use `/vibe-start` to begin one."
- 1 valid folder → "Found `FEATURE-NNN-slug`. Resume it, or start a new feature with `/vibe-start`?"
- 2+ valid folders → suggest the highest-numbered, list up to 2 others, ask which to resume.

**If the file contains a feature ID but that folder does not exist:**
> ⚠️ VibeCode Recovery: Active feature reference is broken — `FEATURE-NNN-slug` doesn't exist.

Write an empty string to `.claude/active_feature` (this is the only allowed write). Then fall through to the scan logic above.

**If the feature folder exists but has no `SPEC.md`:**
> ⚠️ VibeCode Recovery: Feature `FEATURE-NNN-slug` exists but has no SPEC.md — it's malformed.
> Reply **Delete and reset** to clear the active feature reference (clears `.claude/active_feature` only — no files are deleted), or write a spec manually.

Stop here and wait for the user's reply. If they reply "Delete and reset", write an empty string to `.claude/active_feature`. That is the only write allowed.

**If the feature folder exists and has a `SPEC.md`:** read it.

### 5. Present the summary
Summarize only what is directly supported by the files you read. Do not invent details.

Always use this exact structure:

> **Project:** [name and one-line description from PROJECT_CONTEXT.md, or "Not configured yet"]
>
> **Current state:** [most recent session summary from SESSION_LOG.md, or "No sessions logged yet"]
>
> **Active feature:** [feature ID and goal from SPEC.md, or "None"]
>
> **Important decisions:** [2–3 key decisions from DECISIONS.md, or "None logged"]
>
> **Next step:** [one concrete action based on the above]

## Rules
- Summarize only what files contain. Never invent or hallucinate project details.
- Never write project files. The only allowed write is clearing `.claude/active_feature`.
- Never run Bash or git commands.
- Do not use the ⚠️ prefix for normal first-run empty state — only for broken or ambiguous state.
- End every response with exactly one recommended next step.
