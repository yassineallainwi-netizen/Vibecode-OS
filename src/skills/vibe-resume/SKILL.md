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

## Strict write ban
You must NEVER write to these files under any circumstance:
- `PROJECT_CONTEXT.md`
- `AGENTS.md`
- `DECISIONS.md`
- `SESSION_LOG.md`

The only allowed write is: clearing an invalid `.claude/active_feature`.

## Blank placeholder rule
A file is a blank placeholder if it contains only headings, empty lines, or lines containing `[TODO:` or `[TEMPLATE]`. Any project-specific content means the file is real.

## Blank-state transparency rule
When treating a file as blank, you must explain why. Use this pattern:
> "I still see `[TODO:]` markers in `PROJECT_CONTEXT.md`, so I'm treating it as blank."
> "I still see `[TODO:]` markers in `DECISIONS.md`, so no real decisions are logged yet."

Do not use vague phrases like "this file hasn't been set up yet." Be specific about what markers or absence of content triggered the blank classification.

## Steps

### 1. Read project context
Read `PROJECT_CONTEXT.md`.

If it's missing or a blank placeholder, do not draft content. Explain why you're treating it as blank, then ask 2–3 focused questions:
> "I still see `[TODO:]` markers in `PROJECT_CONTEXT.md`, so I'm treating it as blank. To get started:
> 1. What is this project and what problem does it solve?
> 2. What's it built with?
> 3. What's the current state — what works, what's broken, what's next?"

Wait for the user to answer, then continue to step 2 using their answers as context for the summary only. Do not write anything.

### 2. Read session log
Read `SESSION_LOG.md`. Note the most recent session entry if one exists. If it's a blank placeholder, say so explicitly.

### 3. Read key decisions
Read `DECISIONS.md`. Note any decisions that are not blank placeholders. If blank, say so explicitly (e.g., "I still see `[TODO:]` markers in `DECISIONS.md`, so no real decisions are logged yet.").

### 4. Find the active feature

**First: always Glob `features/FEATURE-*` to scan for valid feature directories** (pattern: `FEATURE-` + 3 digits + `-` + lowercase slug). This is the ground-truth scan. Ignore all other directories or files. Record all matches.

Then read `.claude/active_feature`.

**If `.claude/active_feature` contains a feature ID:**
- If that folder exists in your ground-truth scan → read and report its SPEC.md
- If that folder does NOT exist → ⚠️ VibeCode Recovery: the reference is broken. Clear `.claude/active_feature` and fall through to use the ground-truth scan below.

**If `.claude/active_feature` is missing or empty (or just cleared above):**
Use your ground-truth scan:
- 0 valid folders → "No features have been started yet. Use `/vibe-start` to begin one."
- 1 valid folder → "Found `FEATURE-NNN-slug`. Resume it, or start a new feature with `/vibe-start`?"
- 2+ valid folders → suggest the highest-numbered, list up to 2 others, ask which to resume.

**If the identified feature has no `SPEC.md`:**
> ⚠️ VibeCode Recovery: Feature `FEATURE-NNN-slug` exists but has no SPEC.md — it's malformed.
> Reply **Delete and reset** to clear the active feature reference (clears `.claude/active_feature` only — no files are deleted), or write a spec manually.

Stop here and wait for the user's reply. If they reply "Delete and reset", write an empty string to `.claude/active_feature`. That is the only write allowed. Then continue to Step 5.

**If the identified feature has a `SPEC.md`:** read it and proceed to Step 5.

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

## Token-efficiency rules
- Do not rewrite or summarize large files unnecessarily
- Do not restate obvious repo state at length
- Ask only the minimum needed questions
- If project context is blank, ask 2–3 focused questions maximum
- Keep the summary concise — signal over completeness

## Rules
- Summarize only what files contain. Never invent or hallucinate project details.
- Never write project files. The only allowed write is clearing `.claude/active_feature`.
- Never run Bash or git commands.
- Do not use the ⚠️ prefix for normal first-run empty state — only for broken or ambiguous state.
- End every response with exactly one recommended next step.
