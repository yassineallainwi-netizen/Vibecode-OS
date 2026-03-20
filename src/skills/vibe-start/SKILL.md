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

## AGENTS.md blank detection rule
AGENTS.md is considered "uncustomized" if its `## Project-specific rules` section contains only `[TODO:]` markers, even if the generic sections (Mission, Working Rules, Required Reading) have content. The generic sections are installed by default — they do not count as project-specific customization.

## Next-step reconciliation
If `SESSION_LOG.md` contains a "Suggested next" from a previous `/vibe-done` that differs from the user's current feature request, proceed with the user's actual request without warning. The suggestion was advisory, not a commitment.

## Steps

### 1. Read project context
Read the file `PROJECT_CONTEXT.md` in the **project root directory** (same level as `.claude/` folder, not inside it).

If it's missing or a blank placeholder, ask:
> "What is this project and what's it built with?"
Create `PROJECT_CONTEXT.md` from their answer, then continue.

### 1.5. Check AGENTS.md (first feature only)
Read `AGENTS.md` in the **project root directory**.

Glob `**/SPEC.md` and filter to `features/FEATURE-NNN-slug/SPEC.md`. If **zero** existing features are found AND AGENTS.md is missing or uncustomized (see AGENTS.md blank detection rule):
> "Quick setup: `AGENTS.md` has placeholder rules. Want to add any project-specific rules now?
> For example: tech constraints, off-limits areas, code style, or testing expectations.
> Reply with your rules, or say **skip** to fill it later."

If the user provides rules, update the `## Project-specific rules` subsections in AGENTS.md, replacing `[TODO:]` markers with their input. If they say **skip**, continue silently.

On subsequent features (existing SPEC.md files found): skip this step entirely.

### 1.7. Check for active feature conflict
Read the file `.claude/active_feature`.

**If it contains a valid feature ID and that folder exists:**
> ⚠️ VibeCode Recovery: You have an active feature: `FEATURE-NNN-slug`. Close it with `/vibe-done`, or reply **override** to start a new one anyway.

- If user replies **override**: replace `.claude/active_feature` with the new feature ID when created, continue normally.
- If the active feature is malformed (folder exists but no SPEC.md): allow override without further prompts.

**If it points to a missing folder:** clear the file silently and continue.

**If it's empty or missing:** continue normally.

### 2. Classify: trivial or normal?

**A feature may be trivial only if ALL of these are true:**
- Narrow, clearly bounded change
- Low-risk scope
- Limited to one small area
- No architectural clarification needed
- No substantial acceptance-criteria decomposition needed

**Hard blocker:** If the feature naturally requires more than one checklist item to verify, it is not trivial.

**Negative filters — a feature is NEVER trivial if ANY of these apply:**
- Creating multiple new files
- Adding a new dependency
- Changing storage format or schema
- Changing core architecture
- Changing public CLI surface substantially
- Modifying multiple subsystems
- Security-sensitive work (auth, secrets, permissions)
- Database or persistence redesign
- Migration logic
- Non-obvious bug investigation
- Ambiguous requirements
- Broad refactors

Short wording alone does not make a feature trivial.

**Examples of likely trivial work:**
- Typo fix
- One-line text update
- Tiny docs correction
- Narrow UI wording change
- Single obvious bug fix in one file with low scope

**When uncertain:** do not fast-path. Ask 1 focused clarifying question instead.

### 3A. Trivial fast path

If the request is safely classified as trivial:

1. **Do not ask clarifying questions** unless absolutely necessary.
2. **Determine the feature number:** Glob `**/SPEC.md`, filter to paths matching `features/FEATURE-NNN-slug/SPEC.md`. Count existing features to determine next number. If none exist, start at 001. Derive a short slug (lowercase, hyphens, max 4 words).
3. **Write SPEC.md immediately** using this parse-compatible format:

```markdown
# Feature: [Name]

## Goal
[One sentence]

## Scope
[What will change — keep it brief]

## Acceptance Criteria
- [ ] [Single clear condition]
```

4. **Set `.claude/active_feature`** to the new feature ID.
5. **Do NOT pause for spec approval.** Return control with:
> "Spec written. Implement it and run `/vibe-done` when finished."

### 3B. Normal path

If the request is non-trivial:

**Understand the feature.** If the user's request is clear enough to draft a spec, go to step 4.

If not, ask at most 2 focused questions — pick the most important gaps:
- What should the user be able to do when this is built?
- What should it NOT do or touch?

**Assumption-based questions:** When asking a clarifying question, include a recommended default assumption based on project context. Example:
> "I'll assume local JSON storage. Reply 'y' to confirm, or tell me a different choice."

The user should be able to confirm with a very short reply. Do not ask all questions at once if the description already answers some.

### 4. Determine the feature number (normal path)
Glob `**/SPEC.md`, filter to paths matching `features/FEATURE-NNN-slug/SPEC.md` (pattern: `FEATURE-` + 3 digits + `-` + lowercase slug). Count existing features to determine next number. If none exist, start at 001.

Derive a short slug from the user's description (lowercase, hyphens, max 4 words).

### 5. Draft the SPEC.md (normal path)
Create `features/FEATURE-NNN-slug/SPEC.md`:

```markdown
# Feature: [Name]

## Goal
[One sentence: what the user can do after this is built]

## What it should do
- [Concrete behavior from the conversation]

## What it should NOT do
- [Scope boundary]

## Acceptance Criteria
- [ ] [Plain-language acceptance test]

## Risks and edge cases
- [Anything flagged during the conversation]
```

Fill every section with real content from the conversation. No placeholders.

### 6. Set the active feature (normal path)
Write the feature ID (e.g. `FEATURE-003-auth-login`) to `.claude/active_feature`.

### 7. Confirm with the user (normal path)
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
- Never skip feature tracking — even trivial features get a SPEC.md and active_feature set.
- Never skip creating SPEC.md.
- Never skip setting `.claude/active_feature`.
- Do not misclassify large or ambiguous work as trivial.
