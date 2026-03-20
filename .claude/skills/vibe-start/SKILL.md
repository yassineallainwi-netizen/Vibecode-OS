---
name: vibe-start
description: Start a new feature with a structured spec. Use when the user wants to begin building something new.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Edit, Bash
---

# /vibe-start — Start a New Feature

You are helping a vibe coder spec a new feature. You gather requirements, draft everything, and ask for confirmation. The user never fills in a template.

## Security rules
- Normalize all file paths to the project root before reading or writing
- Never read or write outside the project root directory
- Cap any single file read at 50KB during startup scanning
- Allowed scan targets: package.json, pyproject.toml, requirements.txt, Cargo.toml, go.mod, pubspec.yaml, Dockerfile, Makefile, CI files (.github/workflows/), lint/test/typecheck configs

## Blank placeholder rule
A file is a blank placeholder if it contains only headings, empty lines, or lines containing `[TODO:` or `[TEMPLATE]`. Any project-specific content means the file is real.

## Slug sanitization rule
Feature slugs must match: `^[a-z0-9]+(-[a-z0-9]+){0,3}$`, max 40 characters.
Strip non-alphanumeric characters, collapse spaces to hyphens, lowercase. Truncate to 4 words max.

## Next-step reconciliation
If `SESSION_LOG.md` contains a "Context pointer" from a previous `/vibe-done` that differs from the user's current request, proceed with the user's actual request without warning. The pointer was advisory, not a commitment.

## Steps

### 1. Read project context
Read the file `PROJECT_CONTEXT.md` in the **project root directory** (same level as `.claude/` folder, not inside it).

If it's missing or a blank placeholder, ask:
> "What is this project and what's it built with?"
Create `PROJECT_CONTEXT.md` from their answer, then continue.

### 1.3. Scan for tech-stack signals
Silently scan root-bounded allowed files (see Security rules). Infer tech stack only from literal repo evidence.

**Inference rules:**
- Only infer short literal rules directly supported by repo files (max 120 characters each)
- Preferred sources: package.json scripts/engines, pyproject.toml requires-python, Cargo.toml edition, go.mod version, pubspec.yaml sdk
- Leave unsupported sections untouched
- Never invent rules not grounded in files

Record findings for use in steps 1.5 and 5. Do not show this step's output to the user unless asked.

### 1.5. Check AGENTS.md (first feature only)
Read `AGENTS.md` in the **project root directory**.

**Glob `**/SPEC.md`** and filter to `features/FEATURE-NNN-slug/SPEC.md`. Count existing features.

**If one or more existing features found:** skip this step entirely.

**If zero existing features found:** classify AGENTS.md using concrete heuristics:

**AGENTS confidence classification:**
- `high_template`: ALL of the following are true:
  - File missing, OR normalized byte size < 600 bytes
  - OR version marker `<!-- vibecode:agents:v2 -->` is present AND `## Project-specific rules` section still contains only `[TODO:]` markers
  - OR 3+ boilerplate fingerprints still present (e.g. `[TODO: e.g.`, `"Python 3.10+`, `"Flutter + Dart`, `never modify auth.py`, `run pytest before`)
- `mixed`: file exists, has some user content, but also has 1-2 unmodified boilerplate sections
- `customized`: file has clear project-specific content throughout; no `[TODO: e.g.` strings; passes as user-authored

**Behavior by confidence:**

`high_template`: Optimistic patch — using tech-stack findings from step 1.3, immediately draft inferred rules into the relevant `[TODO:]` sections of AGENTS.md. Show result and say:
> "I drafted AGENTS.md from your repo. Does this look right? Edit anything or say **go**."
Wait for confirmation. If user says **go**, also run CLAUDE.md sync (step 1.6).

`mixed`: Compact one-prompt choice — show a brief preview of what was inferred, then ask:
> "**[Accept]** write these inferred rules, **[Edit]** show me first, or **[Skip]** fill it in later."
On Accept or confirmed edits: apply changes, then run CLAUDE.md sync (step 1.6). On Skip: continue.

`customized`: Skip entirely. Run CLAUDE.md sync (step 1.6) silently.

**Never re-prompt for AGENTS on features 2+.**

### 1.6. Sync CLAUDE.md bridge
Run `python src/helpers/claude_md.py` via Bash if available, OR apply the sync logic inline:

Read AGENTS.md and PROJECT_CONTEXT.md. Generate CLAUDE.md in the project root as a compact bridge:
- Header: `<!-- vibecode:claude-bridge:auto-generated -->`
- Sections: Mission, Working Rules, Never Do (if present), Project-specific rules (if customized), VibeCode OS Commands, Verification Commands (if declared in AGENTS.md)

**If CLAUDE.md already exists and was NOT auto-generated** (no header marker):
- Compare critical sections (Working Rules, Never Do, Project-specific rules) against AGENTS.md
- If they differ AND existing has non-template content: halt with:
  > "⚠️ CLAUDE.md has manual edits that conflict with AGENTS.md in [section names]. Resolve before continuing."
- If divergence is non-critical: overwrite with updated content
- If no conflict: overwrite silently

**If CLAUDE.md doesn't exist or was auto-generated:** write it. Note the outcome in a single line in the response.

### 1.7. Check for active feature conflict
Read `.claude/active_feature`.

**Validate format first:** content must match `^FEATURE-\d{3}-[a-z0-9-]+$`. If malformed, clear the file silently and continue.

**If it contains a valid feature ID and that folder exists:**
> ⚠️ VibeCode Recovery: You have an active feature: `FEATURE-NNN-slug`. Close it with `/vibe-done`, or reply **override** to start a new one anyway.

- If user replies **override**: replace `.claude/active_feature` with the new feature ID when created.
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

Short wording alone does not make a feature trivial. When uncertain: do not fast-path. Ask 1 focused clarifying question instead.

### 3A. Trivial fast path

If safely classified as trivial:

1. **Determine the feature number:** Glob `**/SPEC.md`, filter to `features/FEATURE-NNN-slug/SPEC.md`. Count to determine next number; start at 001 if none exist.
2. **Collision check:** verify `features/FEATURE-NNN-*` does not already exist. If it does, increment until a free number is found. If a collision is found with the SAME slug, halt:
   > "⚠️ FEATURE-NNN already exists with that name. Reply with a different name or use `/vibe-status` to check it."
3. **Sanitize slug** from the user's description (see Slug sanitization rule).
4. **Write SPEC.md immediately:**

```markdown
# Feature: [Name]

## Goal
[One sentence]

## Scope
[What will change — keep it brief]

## Acceptance Criteria
- [ ] [Single clear condition]
```

5. **Write `.claude/active_feature`** with the new feature ID.
6. Return:
> "Spec written. Implement it and run `/vibe-done` when finished."

### 3B. Normal path

**Understand the feature.** If the request is clear enough to draft a spec, go to step 4.

If not, ask at most 2 focused questions — pick the most important gaps:
- What should the user be able to do when this is built?
- What should it NOT do or touch?

Include a recommended default assumption based on project context. Example:
> "I'll assume local JSON storage. Reply 'y' to confirm, or tell me a different choice."

### 4. Determine the feature number (normal path)
Glob `**/SPEC.md`, filter to `features/FEATURE-NNN-slug/SPEC.md`. Count existing features; start at 001 if none.

**Collision check:** verify `features/FEATURE-NNN-*` does not already exist. Increment if needed. Halt on slug collision (same name, same number):
> "⚠️ FEATURE-NNN already exists with that name. Reply with a different name or use `/vibe-status` to check it."

Sanitize the slug (see Slug sanitization rule).

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

Fill every section from the conversation. No placeholders.

### 6. Set the active feature (normal path)
Write the sanitized feature ID (e.g. `FEATURE-003-auth-login`) to `.claude/active_feature`.

### 7. Surface mode and risk flags (normal path)
Before confirming the spec, show a compact header using repo maturity data from step 1.3:

> **Mode:** building | **Complexity:** [trivial/normal/complex/high-risk]
> **Risk flags:** [any grounded flags, or "None"]

Flags to surface:
- "No verification commands declared in AGENTS.md" (if command registry is empty)
- "No CLAUDE.md" (if sync failed or skipped)
- "Feature touches [area] — consider branch" (advisory, non-blocking)

### 8. Confirm with the user (normal path)
Show the spec and ask:
> "Does this look right? Edit anything you want, or say 'go' to lock it."

If they request changes, update and ask again. Once confirmed:
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
- Never execute git commands.
- Advisory guidance (git, README, AGENTS) never blocks feature creation.
