---
name: vibe-start
description: Start a new feature with a structured spec. Use when the user wants to begin building something new.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Edit, Bash
shared_references:
  - _shared/recovery.md
  - _shared/evidence.md
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

If it exists and has project-specific content, continue to step 1.3.

**Inception mode — triggers only when ALL of these are true:**
- `PROJECT_CONTEXT.md` is missing or a blank placeholder
- No `features/FEATURE-NNN-slug/SPEC.md` exists anywhere
- `AGENTS.md` is missing or classifies as `high_template`

When in inception mode, ask exactly this batch of 3 questions in one turn:
> "Looks like day zero. Three quick questions to set up the project:
> 1. **What is this project and who is it for?** (one sentence)
> 2. **What's it built with?** (languages/frameworks, or 'not decided yet')
> 3. **What's the smallest first version going to do?** (what a user can do once v0.1 is real)"

Wait for the answers. Then:
- Write `PROJECT_CONTEXT.md` in the project root using the answers. Fill the "What is this?", "What's it built with?", and "What's the current state?" sections directly from the user's answers. Leave "Important rules" blank with a single line: `[TODO: add as you go]`.
- Ensure the `features/` directory exists (create if missing — no files inside yet).
- Note the inception in a single line in the response: "Project initialized. PROJECT_CONTEXT.md written."

Then continue to step 1.3.

**Partial inception (PROJECT_CONTEXT blank but features exist):** this is a recovery case — do not re-ask the 3-question batch. Ask only the minimum needed:
> "PROJECT_CONTEXT.md is blank but features exist. What is this project and what's it built with?"
Create PROJECT_CONTEXT.md from the answer, then continue.

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
Run `python src/helpers/claude_md.py` via Bash to regenerate CLAUDE.md. If Bash is unavailable, skip this step and note "CLAUDE.md sync skipped (Bash unavailable)" in the response.

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

**If it contains a valid feature ID and that folder exists:** → _shared/recovery.md **R3** (conflicting active feature).

- If user replies **override**: replace `.claude/active_feature` with the new feature ID when created.
- If the active feature is malformed (folder exists but no SPEC.md): allow override without further prompts.

**If it points to a missing folder:** clear the file silently and continue.

**If it's empty or missing:** continue normally.

### 2. Classify complexity

Assign exactly one complexity label. Use this in the SPEC.md and mode header.

**`trivial`** — ALL of these must be true:
- Narrow, clearly bounded change; low-risk; limited to one small area
- No architectural clarification needed; no substantial acceptance-criteria decomposition needed
- Naturally only one checklist item to verify

**`normal`** — typical feature work; a few acceptance criteria; doesn't trigger complex/high-risk

**`complex`** — ANY of these apply:
- Touches 3+ subsystems or files across multiple directories
- New dependency added
- Storage format or schema change
- Non-obvious investigation needed
- Ambiguous requirements requiring clarification
- Broad refactor spanning existing code

**`high-risk`** — ANY of these apply:
- Security-sensitive work (auth, secrets, permissions, sandboxing)
- Database or persistence redesign
- Migration logic
- Changing public CLI surface substantially
- Changing core architecture
- Requires coordinated rollback strategy

**Negative filters — a feature is NEVER trivial if ANY of these apply:** creating multiple new files, adding a new dependency, changing storage format or schema, changing core architecture, changing public CLI surface substantially, modifying multiple subsystems, security-sensitive work, database redesign, migration logic, non-obvious bug investigation, ambiguous requirements, broad refactors.

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

## Complexity
trivial

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

## Complexity
[trivial / normal / complex / high-risk]

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

### 6.5. Propose verification commands (normal path — complex/high-risk features only)
Using findings from the tech-stack scan (step 1.3), propose verification commands if the feature is complex or high-risk AND the command registry in AGENTS.md has no declared `verify_cmd`.

**Propose only from repo evidence:**
- `package.json` has `scripts.test` → propose the exact script value (e.g. `npm test`)
- `pytest.ini` or `[tool.pytest]` in `pyproject.toml` exists → propose `pytest`
- `Makefile` has a `test` target → propose `make test`
- Flutter project (`pubspec.yaml` + `lib/`) → propose `flutter test`
- Cargo project → propose `cargo test`
- Go project → propose `go test ./...`

**Rules:**
- Prefer exact declared commands over ecosystem defaults
- Leave unsupported fields blank (never invent commands)
- Surface as advisory note only: "Consider adding to AGENTS.md: `verify_cmd: [proposed]`"
- Do not prompt or block — this is a suggestion, not a question

### 6.8. Source-check flag (normal path — external library/API involved)
Before locking the spec, scan the drafted "What it should do" for external dependencies — named libraries (e.g., Stripe, OpenAI, Supabase, Firebase), HTTP APIs, new frameworks, or SDKs not already in the project.

**If any external dependency is mentioned and is NOT already in the repo's dependency files** (package.json, pyproject.toml, Cargo.toml, go.mod, etc.): append a single advisory bullet to the SPEC.md `## Risks and edge cases` section:

```
- [UNVERIFIED_API] `[library/api name]` — check official docs before implementing. Training data may be outdated. Cite source URL in code comments for the exact version in use.
```

**Rules:**
- One line per distinct library/API. Do not spam.
- Advisory only — never blocks the spec.
- If the library is already in the dependency file (same version): skip (it's a known quantity).
- Do not fetch docs at this step — this is a flag, not an action. Docs get fetched during build.

This prevents the #1 vibecoding failure: implementing against hallucinated API signatures.

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

## Spec rationalizations to resist
These shortcuts bypass the spec discipline and cost more time than they save:

| Rationalization | Why it fails |
|-----------------|--------------|
| "This is small enough, I don't need a SPEC.md" | Every untracked feature is lost when the session ends. No exceptions. |
| "I'll keep the scope in my head" | Scope drift happens silently. Write it down or it doesn't exist. |
| "The user seems confident, no need to clarify" | Undiscovered ambiguity becomes rework. Surface the gap now. |
| "I'll just start and adjust as we go" | Adjusting mid-build costs more tokens than asking one question upfront. |
