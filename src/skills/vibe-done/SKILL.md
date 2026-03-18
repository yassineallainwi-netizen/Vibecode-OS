---
name: vibe-done
description: Finish a feature with verification. Use when the user thinks a feature is complete.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Edit
---

# /vibe-done — Finish and Verify a Feature

You are helping a vibe coder close out a feature properly. Your job is to walk through the acceptance criteria conversationally, document what was built and tested, and write the verification record. The user answers in plain language; you write the structured notes.

## Steps

### 1. Find the active feature
- Read `.claude/active_feature` to find the current feature ID.
- If the file is empty or missing, scan `features/` for folders without a VERIFY.md. If there's only one, use it. If there are multiple, ask the user which feature they're finishing.
- Read `features/<feature-id>/SPEC.md` to get the acceptance criteria.

### 2. Walk through each acceptance criterion
For each item in the "How to verify it works" section of SPEC.md, ask the user conversationally:
- "Did [criterion] get built?"
- "How was it tested? What happened?"

Keep it natural. If the user gives a long answer covering multiple criteria, don't re-ask about ones they already addressed. If the user says "yes, all of those work," ask for at least a brief description of how they verified.

### 3. Write VERIFY.md
Create `features/<feature-id>/VERIFY.md` with this structure:

```markdown
# Verification: [Feature Name]

## What was built
[Summary paragraph based on the conversation and spec]

## Acceptance criteria
- [x] [Criterion] — [how it was verified]
- [ ] [Criterion] — not yet done
- [x] [Criterion] — [how it was verified]

## Tests and checks
- [List of what was tested, how, and what the result was]

## Known limitations
- [Anything that doesn't fully work or needs follow-up]

## Status
[Complete / Partial / Blocked]
```

Set status to:
- **Complete** if all acceptance criteria are checked
- **Partial** if some criteria are unchecked
- **Blocked** if work cannot continue due to an external dependency

### 4. Update SESSION_LOG.md
Add or update a session entry in SESSION_LOG.md:

```markdown
## Session [date]
- Date: [today's date]
- Feature: [feature ID]
- What happened: [summary of what was built]
- What was tested: [summary of verification]
- Still open: [any unchecked criteria, or "Nothing — feature complete"]
- Next step: [suggestion for what to do next]
```

If SESSION_LOG.md already has 10 or more session entries (count `## Session` headings under `## Previous Sessions`), move the oldest entry to `SESSION_ARCHIVE.md` before adding the new one.

The new entry should be placed under `## Latest Session`, and the previous "Latest Session" content should move to the top of `## Previous Sessions`.

### 5. Clear the active feature
Write an empty string to `.claude/active_feature`.

### 6. Report to the user
- If all criteria pass: "Feature complete. VERIFY.md written. Use `/vibe-start` to begin your next feature."
- If some gaps remain: "These items are still open: [list]. Want to continue working on them, or mark the feature as partial and move on?"
  - If the user wants to continue, do NOT clear active_feature. Leave VERIFY.md as Partial.
  - If the user wants to move on, keep VERIFY.md as Partial and clear active_feature.

## Rules
- Ask verification questions conversationally. Never present a form or checklist for the user to fill in.
- The user answers in plain language. You write the structured VERIFY.md.
- Be honest about gaps. If something wasn't tested, mark it unchecked.
- Never overwrite an existing VERIFY.md without reading it first and asking the user if they want to update it.
