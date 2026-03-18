---
name: vibe-done
description: Finish a feature with verification. Use when the user thinks a feature is complete.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Edit
---

# /vibe-done — Finish and Verify a Feature

You are closing out a feature. Walk through verification conversationally, write the record, and classify the result honestly.

## Steps

### 1. Find the active feature
Read `.claude/active_feature`.

If empty or missing, read `features/` for folders without a `VERIFY.md`. If one exists, use it. If multiple exist, ask which one to close.

Read `features/<feature-id>/SPEC.md` to get acceptance criteria.

If `VERIFY.md` already exists, read it before doing anything else. Ask the user if they want to update it.

### 2. Ask about verification
Ask conversationally — not as a checklist:
> "What's been built and tested? Walk me through it."

If the user's answer is vague or only covers some criteria, ask one focused follow-up. Do not re-ask about criteria they already addressed.

### 3. Classify the work
Based on the conversation:

- **Complete** — all acceptance criteria are done and tested
- **Partially Complete** — some criteria done, some missing
- **Not Ready to Close** — little or nothing built yet; called `/vibe-done` too early

Default to **Partially Complete** if there is any doubt.

### 4. Write VERIFY.md
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
Add a new session entry at the top of the log:

```markdown
## Session [date]
- Date: [today's date]
- Feature: [feature ID]
- What happened: [what was built]
- What was tested: [summary of verification]
- Still open: [unchecked criteria, or "Nothing — feature complete"]
- Next step: [what to do next]
```

If SESSION_LOG.md has 10 or more `## Session` entries, move the oldest to `SESSION_ARCHIVE.md` before adding the new one.

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
- Only clear `.claude/active_feature` on Complete or explicit user request.
- End every response with exactly one next step.
