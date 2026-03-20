---
name: vibe-done
description: Finish a feature with verification. Use when the user thinks a feature is complete.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Edit, Bash
---

# /vibe-done — Finish and Verify a Feature

You are closing out a feature. Collect evidence, verify against acceptance criteria, classify honestly, and write a concise record.

## Security rules
- Validate `.claude/active_feature` format before any writes: must match `^FEATURE-\d{3}-[a-z0-9-]+$`
- Verify the target feature directory exists before writing any file
- Never execute git commands — only draft suggestions
- Prefix unsupported quantitative claims with `[USER_REPORTED]` in VERIFY.md

## Feature scan rule
Glob `**/SPEC.md`, filter to `features/FEATURE-NNN-slug/SPEC.md`. Ignore SPEC.md files outside this pattern.
A feature "has no VERIFY.md" if no `features/FEATURE-NNN-slug/VERIFY.md` exists — check with Glob `**/VERIFY.md`.

## Steps

### 1. Find the active feature
Read `.claude/active_feature`. Validate format (`^FEATURE-\d{3}-[a-z0-9-]+$`).

**If malformed or pointing to a missing folder:**
> ⚠️ VibeCode Recovery: Active feature `FEATURE-NNN-slug` doesn't exist.
Clear `.claude/active_feature`. Scan `features/` for valid folders without a VERIFY.md. If one exists, ask to close it. If none: "Nothing to close. Use `/vibe-start`." Stop here.

**If empty or missing:**
Glob `**/SPEC.md`, apply feature scan rule. Check `**/VERIFY.md` to find features without VERIFY.md. If one, use it. If multiple, ask which. If none: "Nothing to close. Use `/vibe-start`."

**Feature mismatch check:** if `.claude/active_feature` has a feature ID but user asks to close a DIFFERENT feature:
> ⚠️ Mismatch: `.claude/active_feature` says `FEATURE-NNN` but you're asking to close `FEATURE-MMM`. Which should I verify?
Wait for reply before proceeding.

**Read SPEC.md:** if folder has no SPEC.md:
> ⚠️ VibeCode Recovery: Feature `FEATURE-NNN-slug` is malformed — no SPEC.md. Cannot verify without acceptance criteria.
> Reply **Delete and reset** to clear `.claude/active_feature` (no files deleted), or write a spec manually.
Stop and wait.

**If VERIFY.md already exists:** read it — this is the current state; it will be overwritten if verification proceeds.

### 2. Zero-diff short-circuit
If evidence shows no relevant file changes since the feature started and no concrete work was described by the user:
> ⚠️ VibeCode Recovery: No relevant file changes detected.

Classify as `Not Ready to Close`. Do not parse criteria without evidence of work.

### 3. Collect evidence
Ask conversationally:
> "What's been built and tested? Walk me through it."

If the answer is vague or covers only some criteria, ask one focused follow-up. Do not re-ask about criteria already addressed.

### Evidence inspection rule
Inspect in this order, bounded scope:
1. Active feature's SPEC.md (acceptance criteria)
2. Existing VERIFY.md if present
3. Files the user explicitly says were changed
4. Obviously relevant files in the feature area if needed

Do not run a heavy repo-wide scan. If evidence is unclear, ask which files changed, then evaluate.

### Cross-check rule
When the user claims specific quantitative evidence (e.g., "94 tests pass"):
- If Bash is available: verify with a read-only command (e.g., count test files, run test suite with allowed commands — see Step 3.5)
- If not verifiable: note as `[USER_REPORTED]` in VERIFY.md
- If contradicts observable evidence: flag discrepancy before writing VERIFY.md

### 3.5. Verification command safety
If running a verification command:
- Check the command against the allowlist:
  - **Block:** `|`, `&`, `;`, `$()`, backticks, `>`, `<`, `sudo`, `su`, explicit absolute paths to executables outside project-local dirs
  - **Allow:** trusted PATH-resolved tools: python, node, npm, pytest, flutter, cargo, go, make, gradle, mvn, jest, mocha, rspec
- Run in the project root directory, with only trusted env vars (PATH, PWD, HOME)
- Set Bash timeout to 30 seconds
- Capture at most 50KB of output
- Strip ANSI escape sequences from output before evaluating
- If output appears to be binary: skip and label `[USER_REPORTED]`
- Non-zero exit code: never classify the criterion as verified

### 4. Classify the work

**Meaningful implementation evidence** must include at least one of:
- Changed project files observed by Claude
- Newly created files relevant to the feature
- Updated files relevant to the feature
- Explicit user statement of which files changed
- Verification notes tied to specific acceptance criteria
- Completed checklist items supported by the work

**Invalid evidence:** vague statements ("I think it's done"), generic confidence, purely aspirational claims, "should be fine".

**Classification states (exactly one):**
- **Not Ready to Close** — no meaningful evidence, or work not started. Feature remains active.
- **Partially Complete** — evidence exists but criteria incomplete or unverified. Feature remains active.
- **Complete** — evidence exists, criteria substantially satisfied, explicit verification of what was tested. No major unverified core criteria remain.

Default to **Partially Complete** when evidence exists but completeness is uncertain.

### Acceptance criteria enforcement
- Compare reported work against each criterion explicitly
- Warn if major criteria remain unchecked or unverified
- Do not classify as `Complete` when core criteria are still unverified

### 5. Write VERIFY.md (live snapshot)
`VERIFY.md` is a live snapshot. On repeated `/vibe-done` runs, **overwrite entirely** — do not append.

Create or overwrite `features/<feature-id>/VERIFY.md`:

```markdown
# Verification: [Feature Name]

## What was built
[Concise summary from the conversation]

## Acceptance criteria
- [x] [Criterion] — [how verified]
- [ ] [Criterion] — not done

## Known gaps
- [Anything incomplete or needing follow-up, or "None"]

## Status
[Complete / Partially Complete / Not Ready to Close]
```

### 6. Passive decision capture
After writing VERIFY.md, check: did completed work introduce a meaningful decision?

**Meaningful decisions:**
- Architecture choice
- Storage or data model choice
- CLI structure choice
- Dependency choice
- Error-handling pattern
- Significant simplification or tradeoff

**Do NOT log:** variable names, wording tweaks, trivial formatting, obvious implementation details.

**If no meaningful decision:** do nothing.

**If a meaningful decision exists:** append to `DECISIONS.md` in the **project root**:

```markdown
## Decision NNN
- Date: [today]
- Feature: [feature ID]
- Decision: [what was chosen]
- Why: [one sentence]
- Tradeoff: [what was given up, or "None"]
```

**First-entry cleanup:** if DECISIONS.md is still in blank template state, remove placeholder content and replace with first real entry.

Number decisions sequentially from the last existing entry. If none, start at 001.

### 7. Update SESSION_LOG.md (compressed)
SESSION_LOG.md keeps entries newest-first. SESSION_ARCHIVE.md keeps entries oldest-first.

**Write the new entry at the top of the log, below the `# Session Log` heading:**

```markdown
## Session [date]
- [what changed — max 15 words]
- [what remains open — max 15 words, or "Nothing — complete"]
- Context pointer: [what to read/do first next session — max 15 words]
```

**Strict limits:** max 3 bullets, max 15 words per bullet. No narrative paragraphs.

**Session log integrity:**
- Preserve exact chronological order of existing entries
- Truncate only the oldest entries when rolling over
- Append removed entries to SESSION_ARCHIVE.md in append-only order (oldest go to bottom of archive)
- Write the SESSION_LOG.md and SESSION_ARCHIVE.md pair atomically — if SESSION_LOG write fails, do not write SESSION_ARCHIVE

**Rollover:** if SESSION_LOG.md now has more than 10 `## Session` headings:
1. Remove oldest entries from the bottom until 10 remain
2. Append removed entries to end of SESSION_ARCHIVE.md (create if doesn't exist)

### 7.5. Git Ghost commit suggestion (Complete or Force Close only)
Skip for Partially Complete or Not Ready to Close.

Run `git branch --show-current` via Bash (read-only). Sanitize branch: must match `^[a-zA-Z0-9._/-]+$`; otherwise show `[sanitized]`.
Run `git status --short` to detect dirty working tree.

Read the literal SPEC.md title (first `# Feature:` heading). Derive the commit subject:
- Default prefix: `feat:`
- Use `fix:` only if the literal spec title is clearly a repair/fix (e.g. contains "fix", "repair", "bug", "patch")
- Subject template: `feat: FEATURE-NNN-slug literal-spec-title-truncated`
- Keep total subject under 72 characters — truncate title portion only

Present the Git Ghost block:

> **Git Ghost — copy and run this yourself (VibeCode never executes git):**
> ```
> git add -A && git commit -m "feat: FEATURE-NNN-slug [truncated literal title]"
> ```
> [If on a feature branch matching this feature:]
> This branch can now be merged to master.
> [If dirty working tree:]
> Working tree has uncommitted changes — review before committing.
> [If branch does not match active feature:]
> ⚠️ Branch mismatch: on `[sanitized branch]` but active feature is `FEATURE-NNN`. Verify before committing.

If git is unavailable or not a git repo: skip silently.

**First feature only:** if SESSION_LOG.md had no prior `## Session` entries before the one just written:
> If your project doesn't have a README.md yet, consider adding one — even a single paragraph helps future you.

### 8. Report and act on classification

**Complete:**
> "Feature complete. VERIFY.md written."
> **Next step:** Use `/vibe-start` to begin your next feature.
Clear `.claude/active_feature`.

**Partially Complete:**
> "Feature partially complete. These criteria are still open: [list]."
> **Next step:** Continue working on them, or say 'move on' to close the feature as partial.
If user says move on: clear `.claude/active_feature`.

**Not Ready to Close:**
> "This feature isn't ready to close yet — not enough has been verified. VERIFY.md written with current state."
> **Next step:** Continue building, then run `/vibe-done` again when more is complete.
Do NOT clear `.claude/active_feature`.

### Force-close escape hatch
If user says **"Force Close"**, **"Drop remaining"**, or equivalent:
- Write VERIFY.md with a `## Dropped Scope` section listing all unmet criteria
- Clearly indicate the feature was closed with dropped scope, not fully verified
- Clear `.claude/active_feature`
- Session log entry must note scope was dropped
- Git Ghost block shows `[PARTIAL]` annotation in commit body

## Rules
- You write everything. The user speaks in plain language.
- Never present a form or checklist for the user to fill in.
- Be honest. If something wasn't tested, mark it unchecked.
- Only clear `.claude/active_feature` on Complete, Force Close, or explicit user request to move on.
- End every response with exactly one next step.
- Delete and reset clears `.claude/active_feature` only — it does not delete feature folders or files.
- Never execute git commands.
