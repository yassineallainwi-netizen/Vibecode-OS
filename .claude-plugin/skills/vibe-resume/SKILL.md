---
name: vibe-resume
description: Resume work from a previous session. Use at the start of a new session to restore context.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Bash
---

# /vibe-resume — Resume a Previous Session

You are restoring session context for a vibe coder. Read existing files and report what you find as a compact War Room manifest. Never invent, draft, or guess project details.

## Read-only rule
This command is read-only. The only write you are allowed to perform is clearing `.claude/active_feature` when it contains a broken reference.

## Strict write ban — NEVER write to these files under any circumstance:
- `PROJECT_CONTEXT.md`
- `AGENTS.md`
- `DECISIONS.md`
- `SESSION_LOG.md`
- Any feature SPEC.md or VERIFY.md

The only allowed write is: clearing an invalid `.claude/active_feature`.

## Allowed read-only Bash (whitelisted only):
- `git branch --show-current`
- `git status --short`
- `git diff --stat HEAD~5`
Never run any other Bash command. Never run destructive git commands.

## Branch sanitization rule
Before displaying a branch name, verify it matches `^[a-zA-Z0-9._/-]+$`. If it does not, display `[sanitized]` instead.

## Blank placeholder rule
A file is a blank placeholder if it contains only headings, empty lines, or `[TODO:` / `[TEMPLATE]` lines. Project-specific content means the file is real.

## AGENTS.md blank detection
AGENTS.md is uncustomized if `## Project-specific rules` section contains only `[TODO:]` markers. Generic sections (Mission, Working Rules) are installed by default and do not count as customization.

## Blank-state transparency rule
When treating a file as blank, explain why:
> "I still see `[TODO:]` markers in `PROJECT_CONTEXT.md`, so I'm treating it as blank."
Never use vague phrases like "this file hasn't been set up yet."

## Lost-state detection
Auto-trigger mini-resume (skip to Step 5, emit compact War Room) when ANY of the following are detected:
- User message contains "I'm lost", "what now", "where am I", "remind me", or equivalent confusion signal
- `.claude/active_feature` is malformed (does not match `^FEATURE-\d{3}-[a-z0-9-]+$`)
- Active feature points to a missing directory or missing SPEC.md
- SESSION_LOG.md latest entry references a different feature than active_feature

Mini-resume omits steps 1-4 and goes directly to Step 5 with whatever can be determined from files.

## Compact artifact check (run before Step 1)

Only run this check if `.claude/context/` directory exists. If absent, skip directly to Step 1.

If `.claude/context/project_state.json` exists:
1. Validate: schema_version == 1 AND all required fields present AND checksum matches AND age ≤ 24h
2. All four checks pass → `context_source = "compact_ready"` (use artifacts instead of full scan)
3. Any check fails → `context_source = "full_scan_required"` (run Steps 1-4 normally)

If compact_ready: also validate the active feature artifact (`feature_FEATURE-NNN.json`). If it fails, set `context_source = "mixed"` (supplement with targeted file reads).

---

## Steps

### 1. Read project context
Read `PROJECT_CONTEXT.md` in the **project root directory** (same level as `.claude/`). Cap read at ~4000 characters.

If missing or blank placeholder: explain why, then ask 2–3 focused questions:
> "I still see `[TODO:]` markers in `PROJECT_CONTEXT.md`, so I'm treating it as blank. To get started:
> 1. What is this project and what problem does it solve?
> 2. What's it built with?
> 3. What's the current state — what works, what's broken, what's next?"

Wait for answers. Use them as context for the manifest only. Do not write anything.

### 1.5. Read AGENTS.md
Read `AGENTS.md` in the **project root directory**. Cap at ~2000 characters.

If it has project-specific rules (not uncustomized per detection rule above): note for `Project rules` field.
If uncustomized or missing: `Project rules` = "Not configured — run `/vibe-start` to set up".

### 2. Read session log
Read `SESSION_LOG.md` in the **project root directory**. Cap at ~2000 characters.
Extract the most recent session entry. If blank placeholder, note it.

### 3. Read key decisions (brief)
Read `DECISIONS.md` briefly — extract the 2-3 most recent decisions only. If blank, note it.

### 4. Find the active feature

**Ground-truth scan first:** Glob `**/SPEC.md`, filter to `features/FEATURE-NNN-slug/SPEC.md` (pattern: `FEATURE-` + 3 digits + `-` + lowercase slug). Record all matching IDs.

**Validate active_feature format:** read `.claude/active_feature`. If content does not match `^FEATURE-\d{3}-[a-z0-9-]+$` and is not empty: treat as broken — clear the file, fall through to ground-truth scan.

**If `.claude/active_feature` contains a valid feature ID:**
- Found in ground-truth scan → read its SPEC.md and any VERIFY.md; proceed to Step 4.5
- NOT found → ⚠️ VibeCode Recovery: broken reference. Clear `.claude/active_feature`, fall through to ground-truth scan.

**If `.claude/active_feature` is empty or just cleared:**
Use ground-truth scan:
- 0 features → active feature = "None" in manifest; suggest `/vibe-start`
- 1 feature → read its SPEC.md; note in manifest; ask to resume or start new
- 2+ features → read highest-numbered SPEC.md; list up to 2 others; ask which to resume

**Malformed feature (SPEC.md found but outside expected path):**
> ⚠️ VibeCode Recovery: Feature exists but has no SPEC.md — malformed.
> Reply **Delete and reset** to clear active_feature only (no files deleted), or write a spec manually.
Wait for reply. If "Delete and reset": clear `.claude/active_feature` only. Continue to Step 5.

### 4.5. Check git branch alignment
Run `git branch --show-current` (read-only). Sanitize branch before displaying.

If branch contains a `FEATURE-NNN` pattern that does NOT match the active feature:
> ⚠️ **Branch mismatch:** on `[sanitized branch]` but active feature is `FEATURE-MMM-...`. Consider switching or merging.

If git unavailable or branch has no feature pattern: skip silently.

Also run `git status --short` and `git diff --stat HEAD~5` to gather Git and Recent files data for the manifest.

### 5. Present the War Room manifest
Summarize only what files directly support. Fail closed — omit any field where parsing fails rather than guessing.

**Determine repo maturity:** count how many of the following are true:
- AGENTS.md is customized
- CLAUDE.md exists
- Command registry has at least one declared command
- `.git` directory exists
- At least one feature folder exists
- At least one VERIFY.md exists
- SESSION_LOG.md has a non-placeholder entry

Score 0-2 = newbie mode. Score 3+ = expert mode.

**Present the manifest:**

> **Project:** [name and one-line description from PROJECT_CONTEXT.md, or "Not configured yet"]
>
> **Project rules:** [one-line summary from AGENTS.md project-specific rules, or "Not configured"]
>
> **Mode:** [building / verifying / closing — derived from: no VERIFY.md = building; VERIFY.md partial = verifying; VERIFY.md complete = closing; no active feature = idle]
>
> **Risk flags:** [grounded flags only, or "None" — flag: stale session if latest SESSION_LOG entry is old; no commands declared if AGENTS.md has no verify_cmd; branch mismatch if detected]
>
> **Current state:** [most recent session bullet from SESSION_LOG.md, or "No sessions logged yet"]
>
> **Active feature:** [feature ID and one-line goal from SPEC.md, or "None"]
>
> **Git:** [sanitized branch name, clean/dirty from git status, or "Not a git repo"]
>
> **Recent files:** [top 3-5 files from git diff --stat HEAD~5, or "None detected"]
>
> **Last hard problem solved:** [context pointer from last SESSION_LOG entry, or last verified criterion from VERIFY.md, or "None"]
>
> **Next file to edit:** [first unresolved artifact implied by first unchecked criterion in active SPEC.md, or "Unknown"]
>
> **Next concrete code action:** [one literal action derived from first unchecked criterion, or "Start with `/vibe-start`"]
>
> **Context pointer:** [first unchecked criterion in active SPEC.md, or last context pointer from SESSION_LOG.md, or "None"]
>
> **Verification:** [readiness: ready/degraded/none] | [strength: high/medium/low/none] | [last command or "none"] | [freshness: fresh/reused/stale/missing] | [blocking failure or "None"] | [safest next action]
>
> **Context source:** [compact_ready / mixed / full_scan_required] [— reconstruction reason if applicable]

*(Verification line: read VERIFY.md audit trail for last command/timestamp; compute freshness from audit trail timestamp vs now; strength from evidence labels on checked criteria; readiness = ready if strength ≥ medium, degraded if low, none if no VERIFY.md. Fail closed — omit this line entirely if VERIFY.md is unreadable.)*
*(Context source line: set during compact artifact check above. For compact_ready, fields sourced from JSON artifacts are labeled "(from cache)". For full_scan_required, note reconstruction reason. For mixed, note which source each field came from.)*

**Auto mini-resume on lost state:** if `context_source = full_scan_required` AND `reconstruction_reason` is "artifacts_stale" or "checksum_mismatch", prepend to the manifest:
> ⚠️ **Stale context detected** — running full reconstruction. [reconstruction_reason].

**Novice-only fields** (add only when maturity score is 0-2):
>
> **Why this is safe to start:** [one-sentence reassurance based on repo state]
>
> **First file to open:** [most relevant file based on active feature or project type]

## Token-efficiency rules
- Do not rewrite or summarize large files unnecessarily
- Cap SESSION_LOG contribution to ~2000 characters
- Cap AGENTS.md contribution to ~2000 characters
- Ask only the minimum needed questions
- Keep the manifest concise — signal over completeness

## Rules
- Summarize only what files contain. Never invent project details.
- Never write project files. The only allowed write is clearing `.claude/active_feature`.
- Only whitelisted Bash commands allowed. Never run destructive git commands.
- Do not use ⚠️ for normal first-run empty state — only for broken or ambiguous state.
- End every response with exactly one recommended next step.
