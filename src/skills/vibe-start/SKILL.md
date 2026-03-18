---
name: vibe-start
description: Start a new feature with a structured spec. Use when the user wants to begin building something new.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Edit
---

# /vibe-start — Start a New Feature

You are helping a vibe coder start a new feature. Your job is to gather requirements conversationally and produce a clear spec. The user describes what they want; you draft everything. Never present an empty template.

## Steps

### 1. Read project context
- Read `PROJECT_CONTEXT.md` in the repo root to understand the project, tech stack, and rules.
- If `PROJECT_CONTEXT.md` does not exist or is empty, tell the user: "I don't see a PROJECT_CONTEXT.md yet. Let's fill one in quickly — what is this project and what's it built with?" Then create it from their answers before continuing.

### 2. Ask clarifying questions
Ask the user 2-3 short questions to understand the feature:
- "What should the user be able to do when this is built?" (the goal)
- "What specific behaviors or screens does this involve?" (the scope)
- "Is there anything this should NOT do or touch?" (the boundary)

Keep it conversational. Don't ask all three at once if the user's initial description already answers some.

### 3. Determine the feature number
- Scan the `features/` directory for existing `FEATURE-NNN-*` folders.
- Pick the next number (e.g., if FEATURE-002 exists, use 003).
- If no features exist yet, start with 001.
- Derive a short slug from the user's description (lowercase, hyphens, max 4 words). Example: "user auth login" becomes `auth-login`.

### 4. Draft the SPEC.md
Create the file `features/FEATURE-NNN-slug/SPEC.md` with this structure:

```markdown
# Feature: [Name from conversation]

## Goal
[One sentence: what should the user be able to do after this is built?]

## What it should do
- [Bullet list of behaviors, drafted from the conversation]

## What it should NOT do
- [Scope boundaries from the conversation]

## How to verify it works
- [ ] [Plain language acceptance test]
- [ ] [Another one]

## Risks and edge cases
- [Anything flagged during the conversation]
```

Draft all sections yourself based on the conversation. Fill in concrete details, not placeholders.

### 5. Set the active feature
Write the feature ID (e.g. `FEATURE-003-auth-login`) to `.claude/active_feature`.

### 6. Ask for confirmation
Show the user the spec you drafted and ask: "Does this look right? Edit anything you want, or say 'go' to lock the spec and start building."

- If the user requests changes, update the spec and ask again.
- Once confirmed, say: "Spec locked. You can start building now. Use `/vibe-status` to check progress and `/vibe-done` when you're finished."

## Rules
- You draft everything. The user only confirms, edits, or adds.
- Never present an empty template or ask the user to fill in sections.
- Keep the spec concise — no more than a page for simple features.
- If the user describes something very small (a bug fix, a one-liner), still create the spec but make it proportionally brief.
