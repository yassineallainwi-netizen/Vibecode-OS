---
name: vibe-done
description: Finish a feature with verification. Use when the user thinks a feature is complete.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Edit
---

# /vibe-done — Finish and Verify a Feature

You are closing out a feature. Walk through verification conversationally, write the record, and classify the result honestly.

## Feature scan rule
When scanning `features/`, only consider directories strictly matching `FEATURE-NNN-slug` (pattern: `FEATURE-` + 3 digits + `-` + lowercase slug). Ignore all other directories and files.

## Steps

### 1. Find the active feature
Read `.claude/active_feature`.

**If it contains a feature ID but that folder does not exist:**
> ⚠️ VibeCode Recovery: Active feature `FEATURE-NNN-slug` doesn't exist.
Clear `.claude/active_feature`, then scan `features/` for valid folders without a `VERIFY.md`. If one exists, ask the user if they want to close it. If none exist, say "Nothing to close. Use `/vibe-start`." Stop here.

**If empty or missing:**
Scan `features/` for valid folders without a `VERIFY.md`. If one exists, use it. If multiple exist, ask which one to close. If none, say "Nothing to close. Use `/vibe-start`."

**Once a feature is identified — read its SPEC.md:**

If the folder has no `SPEC.md`:
> ⚠️ VibeCode Recovery: Feature `FEATURE-NNN-slug` is malformed — no SPEC.md. Cannot verify without acceptance criteria.
> Reply **Delete and reset** to clear this state (clears `.claude/active_feature` only — no files are deleted), or write a spec manually.
Stop here and wait for user reply.

**If `VERIFY.md` already exists:** read it before doing anything else. Ask the user if they want to update it.

### 2. Ask about verification
Ask conversationally — not as a checklist:
> "What's been built and tested? Walk me through it."

If the user's answer is vague or only covers some criteria, ask one focused follow-up. Do not re-ask about criteria they already addressed.

### 3. Classify the work

**Meaningful implementation evidence** means at least one of:
- The user describes specific completed work
- Relevant project files were changed
- Verification notes or completed checklist items exist

Classification:
- **Not Ready to Close** — no meaningful implementation evidence exists. Never classify as Partial or Complete based on vague intent like "I think it's mostly done."
- **Partially Complete** — meaningful implementation evidence exists, but acceptance criteria are incomplete.
- **Complete** — meaningful implementation evidence exists and spec criteria are substantially satisfied.

Default to **Partially Complete** when evidence exists but you are uncertain about completeness.

### 4. Write VERIFY.md
If `VERIFY.md` doesn't exist, create it automatically from SPEC.md criteria — do not ask first.

Create or update `features/<feature-id>/VERIFY.md`:

```markdown
# Verification: [Feature Name]

## What was built
[Summary from the conversation]

## Acceptance criteria
- [x] [Criterion] — [how verified]
- [ ] [Criterion] — not done

## Tests and checks
- [What was tested, how, and the result]

## Known limitations
- [Anything incomplete or needing follow-up, or "None"]

## Status
[Complete / Partially Complete / Not Ready to Close]
```

### 5. Update SESSION_LOG.md
SESSION_LOG.md keeps entries newest-first. SESSION_ARCHIVE.md keeps entries oldest-first.

**Write the new entry at the top of the `## Latest Session` section:**

```markdown
## Session [date]
- Date: [today's date]
- Feature: [feature ID]
- What happened: [what was built]
- What was tested: [summary of verification]
- Still open: [unchecked criteria, or "Nothing — feature complete"]
- Next step: [what to do next]
```

**Rollover — if SESSION_LOG.md now has more than 10 `## Session` headings:**
1. Remove the oldest entries from the bottom until only 10 remain
2. Append those removed entries to the end of `SESSION_ARCHIVE.md` (create the file if it doesn't exist)
3. Preserve chronological order — oldest entries go to the bottom of the archive

### 6. Report and act on classification

**Complete:**
> "Feature complete. VERIFY.md written."
>
> **Next step:** Use `/vibe-start` to begin your next feature.

Clear `.claude/active_feature`.

**Partially Complete:**
> "Feature partially complete. These criteria are still open: [list]."
>
> **Next step:** Continue working on them, or say 'move on' to close the feature as partial.

If the user says move on: clear `.claude/active_feature`. Otherwise leave it active.

**Not Ready to Close:**
> "This feature isn't ready to close yet — not enough has been verified. VERIFY.md written with current state."
>
> **Next step:** Continue building, then run `/vibe-done` again when more is complete.

Do NOT clear `.claude/active_feature`.

## Rules
- You write everything. The user speaks in plain language.
- Never present a form or checklist for the user to fill in.
- Be honest. If something wasn't tested, mark it unchecked.
- Only clear `.claude/active_feature` on Complete or explicit user request to move on.
- End every response with exactly one next step.
- Delete and reset clears `.claude/active_feature` only — it does not delete feature folders or files.
