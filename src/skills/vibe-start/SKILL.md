---
name: vibe-start
description: Start a new feature with a structured spec. Use when the user wants to begin building something new.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Edit
---

# /vibe-start — Start a New Feature

You are helping a vibe coder spec a new feature. You gather requirements, draft everything, and ask for confirmation. The user never fills in a template.

## Blank placeholder rule
A file is a blank placeholder if it contains only headings, empty lines, or lines containing `[TODO:` or `[TEMPLATE]`. Any project-specific content means the file is real — treat it as such.

## Steps

### 1. Read project context
Read `PROJECT_CONTEXT.md`.

If it's missing or a blank placeholder, ask:
> "What is this project and what's it built with?"
Create `PROJECT_CONTEXT.md` from their answer, then continue.

### 1.5. Check for active feature conflict
Read `.claude/active_feature`.

**If it contains a valid feature ID and that folder exists:**
> ⚠️ VibeCode Recovery: You have an active feature: `FEATURE-NNN-slug`. Close it with `/vibe-done`, or reply **override** to start a new one anyway.

- If user replies **override**: replace `.claude/active_feature` with the new feature ID when created, continue normally.
- If the active feature is malformed (folder exists but no SPEC.md): allow override without further prompts.

**If it points to a missing folder:** clear the file silently and continue.

**If it's empty or missing:** continue normally.

### 2. Understand the feature
If the user's request is clear enough to draft a spec, go to step 3.

If not, ask at most 2 focused questions — pick the most important gaps:
- What should the user be able to do when this is built?
- What should it NOT do or touch?

Do not ask all questions at once if the description already answers some.

### 3. Determine the feature number
Scan `features/` for directories strictly matching `FEATURE-NNN-slug` (pattern: `FEATURE-` + 3 digits + `-` + lowercase slug). Use the next number. If none exist, start at 001.

Derive a short slug from the user's description (lowercase, hyphens, max 4 words).

### 4. Draft the SPEC.md
Create `features/FEATURE-NNN-slug/SPEC.md`:

```markdown
# Feature: [Name]

## Goal
[One sentence: what the user can do after this is built]

## What it should do
- [Concrete behavior from the conversation]

## What it should NOT do
- [Scope boundary]

## How to verify it works
- [ ] [Plain-language acceptance test]

## Risks and edge cases
- [Anything flagged during the conversation]
```

Fill every section with real content from the conversation. No placeholders.

### 5. Set the active feature
Write the feature ID (e.g. `FEATURE-003-auth-login`) to `.claude/active_feature`.

### 6. Confirm with the user
Show the spec and ask:
> "Does this look right? Edit anything you want, or say 'go' to lock it."

If they request changes, update and ask again.

Once confirmed, say:
> "Spec locked. Use `/vibe-status` to track progress and `/vibe-done` when you're finished."

## Rules
- You draft everything. The user only confirms or edits.
- Never show an empty template.
- Keep specs concise — one page for simple features.
- Ask at most 2 questions at a time.
