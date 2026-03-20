---
name: vibe-done
description: Finish a feature with verification. Use when the user thinks a feature is complete.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Edit, Bash
---

# /vibe-done — Finish and Verify a Feature

You are closing out a feature. Collect evidence, verify against acceptance criteria, classify honestly, and write a concise record.

## Feature scan rule
To find features: Glob `**/SPEC.md`, then filter results to paths matching `features/FEATURE-NNN-slug/SPEC.md` (pattern: `FEATURE-` + 3 digits + `-` + lowercase slug). Ignore any SPEC.md outside this pattern. A feature "has no VERIFY.md" if no corresponding `features/FEATURE-NNN-slug/VERIFY.md` exists — check with Glob `**/VERIFY.md`.

## Steps

### 1. Find the active feature
Read `.claude/active_feature`.

**If it contains a feature ID but that folder does not exist:**
> ⚠️ VibeCode Recovery: Active feature `FEATURE-NNN-slug` doesn't exist.
Clear `.claude/active_feature`, then scan `features/` for valid folders without a `VERIFY.md`. If one exists, ask the user if they want to close it. If none exist, say "Nothing to close. Use `/vibe-start`." Stop here.

**If empty or missing:**
Glob `**/SPEC.md` and apply the feature scan rule to find valid features. Check `**/VERIFY.md` to identify those without a VERIFY.md. If one exists, use it. If multiple exist, ask which one to close. If none, say "Nothing to close. Use `/vibe-start`."

**Feature mismatch check:** If `.claude/active_feature` contains a feature ID but the user is asking to close a DIFFERENT feature, flag it:
> ⚠️ Mismatch: `.claude/active_feature` says `FEATURE-NNN` but you're asking to close `FEATURE-MMM`. Which feature should I verify?
Wait for the user's reply before proceeding.

**Once a feature is identified — read its SPEC.md:**

If the folder has no `SPEC.md`:
> ⚠️ VibeCode Recovery: Feature `FEATURE-NNN-slug` is malformed — no SPEC.md. Cannot verify without acceptance criteria.
> Reply **Delete and reset** to clear this state (clears `.claude/active_feature` only — no files are deleted), or write a spec manually.
Stop here and wait for user reply.

**If `VERIFY.md` already exists:** read it before doing anything else. This is the current verification state — it will be overwritten (not appended) if verification proceeds.

### 2. Zero-diff short-circuit
If available evidence shows no relevant file changes since the feature started and no concrete work was described by the user, stop early:
> ⚠️ VibeCode Recovery: No relevant file changes detected.

Classify as `Not Ready to Close`. Do not spend tokens parsing criteria if there is no evidence of work. Docs-only or unrelated changes do not count as feature implementation evidence.

### 3. Collect evidence
Ask conversationally — not as a checklist:
> "What's been built and tested? Walk me through it."

If the user's answer is vague or only covers some criteria, ask one focused follow-up. Do not re-ask about criteria they already addressed.

### Evidence inspection rule
Inspect evidence with bounded scope, in this order:
1. The active feature's `SPEC.md`
2. Existing `VERIFY.md` if present
3. Files the user explicitly says were changed
4. Obviously relevant files in the feature area if needed for confirmation

Do not perform a heavy repo-wide scan. If evidence is still unclear, ask the user to state which files were changed, then evaluate.

### Cross-check rule
When the user claims specific quantitative evidence (e.g., "94 tests pass", "flutter analyze clean"):
- If Bash is available: verify the claim by running the relevant command (e.g., count test files, run analyzer). Bash is allowed for read-only verification commands.
- If the claim cannot be verified: note it as "user-stated, not independently verified" in VERIFY.md
- If the claim contradicts observable evidence: flag the discrepancy before writing VERIFY.md

Do not silently accept quantitative claims. A VERIFY.md that says "94 tests green" when the repo has 142 tests is misleading.

### 4. Classify the work

**Meaningful implementation evidence** must be tied to filesystem reality or explicit concrete claims. Valid evidence includes at least one of:
- Changed project files observed by Claude
- Newly created files relevant to the feature
- Updated files relevant to the feature
- Explicit user statement of which files changed
- Verification notes tied to specific acceptance criteria
- Completed checklist items supported by the work

**Invalid evidence** includes:
- Vague statements like "I think it's done"
- Generic confidence without changed files or verification
- Purely aspirational claims
- "Should be fine"

**Classification states — exactly one of:**

- **Not Ready to Close** — no meaningful implementation evidence exists, or the user says work has not started. Feature remains active.
- **Partially Complete** — meaningful implementation evidence exists, but acceptance criteria are incomplete or unverified. Feature remains active.
- **Complete** — meaningful implementation evidence exists, spec criteria are substantially satisfied, and explicit verification of what was tested or checked exists. No major unverified core criteria remain.

Default to **Partially Complete** when evidence exists but you are uncertain about completeness.

### Acceptance criteria enforcement
When `SPEC.md` contains acceptance criteria:
- Explicitly compare reported work against each criterion
- Warn if major criteria remain unchecked or unverified
- Do not classify as `Complete` when core criteria are still unverified

### 5. Write VERIFY.md (live snapshot)
`VERIFY.md` is a live snapshot of the current verification state.

**Overwrite rule:** On repeated `/vibe-done` runs for the same feature, overwrite the existing `VERIFY.md` entirely. Do not append duplicate verification blocks. Keep one current view.

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
After writing VERIFY.md, check: did the completed work introduce a meaningful decision?

**Meaningful decisions** include:
- Architecture choice
- Storage or data model choice
- CLI structure choice
- Dependency choice
- Error-handling pattern
- Significant simplification or tradeoff

**Do NOT log:**
- Variable names, wording tweaks, tiny formatting choices
- Obvious implementation details with no future consequence
- Trivial features should almost never generate decisions

**If no meaningful decision exists:** do nothing. Do not write to `DECISIONS.md`.

**If a meaningful decision exists:** append a short entry to `DECISIONS.md` in the **project root**:

```markdown
## Decision NNN
- Date: [today]
- Feature: [feature ID]
- Decision: [what was chosen]
- Why: [one sentence]
- Tradeoff: [what was given up, or "None"]
```

**First-entry cleanup rule:** If `DECISIONS.md` in the **project root** is still in blank template state (contains only `[TODO:` markers), remove all placeholder content and replace with the first real entry. Do not mix real decisions with blank-state markers.

Number decisions sequentially from the last existing entry. If no entries exist, start at 001.

### 7. Update SESSION_LOG.md (compressed)
Update `SESSION_LOG.md` in the **project root**. SESSION_LOG.md keeps entries newest-first. SESSION_ARCHIVE.md keeps entries oldest-first.

**Write the new entry at the top of the log, below the `# Session Log` heading:**

```markdown
## Session [date]
- [what changed — max 15 words]
- [what remains open — max 15 words, or "Nothing — complete"]
- Suggested next: [max 15 words — this is advisory, not a commitment]
```

**Strict limits:** Maximum 3 bullets. Maximum 15 words per bullet. No narrative paragraphs. Prioritize signal over completeness.

**Rollover — if SESSION_LOG.md now has more than 10 `## Session` headings:**
1. Remove the oldest entries from the bottom until only 10 remain
2. Append those removed entries to the end of `SESSION_ARCHIVE.md` (create the file if it doesn't exist)
3. Preserve chronological order — oldest entries go to the bottom of the archive

### 7.5. Git commit and branch reminder (Complete or Force Close only)
Skip this step for Partially Complete or Not Ready to Close.

Run `git branch --show-current` via Bash (read-only).

Include in the closing report:
> **Git reminder:** Consider committing your changes for this feature:
> `git add -A && git commit -m "feat(FEATURE-NNN-slug): [short description]"`

If on a feature branch matching the completed feature:
> This branch can now be merged to master.

If on master or a mismatched branch:
> Consider creating a feature branch for your next feature: `git checkout -b feature/FEATURE-NNN-slug`

If git is not available or the directory is not a git repo: skip the git reminder silently.

**First feature only:** If SESSION_LOG.md had no prior `## Session` entries before the one you just wrote, add:
> If your project doesn't have a README.md yet, consider adding one — even a single paragraph helps future you.

### 8. Report and act on classification

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

### Force-close escape hatch
If the user explicitly says **"Force Close"**, **"Drop remaining"**, or equivalent, `/vibe-done` may close the feature despite unchecked criteria. In that case:
- Write `VERIFY.md` with a `## Dropped Scope` section listing all unmet criteria
- The closeout must clearly indicate the feature was closed with dropped scope, not fully verified
- Clear `.claude/active_feature`
- Session log entry must note scope was dropped

This prevents users from getting trapped in an enforcement loop without corrupting the meaning of "complete."

## Rules
- You write everything. The user speaks in plain language.
- Never present a form or checklist for the user to fill in.
- Be honest. If something wasn't tested, mark it unchecked.
- Only clear `.claude/active_feature` on Complete, Force Close, or explicit user request to move on.
- End every response with exactly one next step.
- Delete and reset clears `.claude/active_feature` only — it does not delete feature folders or files.
