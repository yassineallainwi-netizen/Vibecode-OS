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

## Evidence model
Every acceptance criterion must carry exactly one evidence label:
- `command_verified` — a command was run and exited 0 with meaningful output
- `repo_observed` — Claude inspected files directly and observed the criterion is met
- `user_reported` — user stated it; not independently verified
- `spec_expected` — spec says so but no evidence exists yet

**Ordered strength (weakest → strongest):** none → weak (spec_expected) → partial (user_reported) → strong (repo_observed) → fresh_strong (command_verified)

**Downgrade from command_verified when:**
- Exit code is non-zero
- Output is empty (and silent success is not explicitly expected for this tool)
- Output shows 0 tests run
- Output contains binary data or hostile formatting
- Output was truncated before trustworthy interpretation

**Display mapping:** command_verified/repo_observed → high; user_reported → medium; spec_expected → low

## Verification rationalizations to resist
These shortcuts feel reasonable but silently degrade quality:

| Rationalization | Why it fails |
|-----------------|--------------|
| "The user said it works — that's enough" | `user_reported` is weak evidence. Run the command; observe the output. |
| "The code looks right, I don't need to check" | "Looks right" is `spec_expected` at best. Observable evidence is required. |
| "Most criteria are met, the rest are minor" | Unverified core criteria → Partially Complete. Don't round up. |
| "Tests passed on the first try, nothing's wrong" | Shallow tests always pass. Check what was actually tested — e.g., 0 tests run exits 0. |
| "I'll skip the simplicity check, the skill is long enough" | Over-engineered code creates future rework. A 30-second scan prevents 2 hours of debt. |

## Command approval rule
Before running a verification command, check `.claude/approved_commands.json`:
- If command is approved for this repo (matching cmd_hash + repo_id): run without prompting
- If not found, or hash differs, or file missing/corrupt: ask the user once:
  > "I'd like to run `[command]` to verify. **Approve** (run now + remember), **approve-all** (remember all future commands), or **skip** (mark as user_reported)?"
- On Approve: add to approved_commands.json (call `python src/helpers/approval.py` or apply logic inline)
- On Skip: do not run; mark evidence as `user_reported`

## Command execution safety
When running a verification command:
- **Block:** `|`, `&`, `;`, `$()`, backticks, `>`, `<`, `sudo`, `su`, absolute executable paths
- **Allow:** trusted PATH-resolved tools (python, node, npm, pytest, flutter, cargo, go, make, jest, etc.)
- Set Bash timeout to 30 seconds
- Cap output at 50KB (truncate if exceeded; set `truncated: true` in evidence)
- Strip ANSI escape sequences from output before evaluating (call `src/helpers/verification.py strip_ansi` or apply inline)
- If output appears binary: skip and label `user_reported`
- Non-zero exit code → never classify as `command_verified`

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

### 3.5. Verification command execution
If running a verification command, follow Command execution safety rules above.

After execution:
1. Strip ANSI from output
2. Triage output: extract test counts, failing files, error classes (call `src/helpers/verification.py triage_log` or apply inline pattern matching)
3. Classify evidence: use `classify_evidence(exit_code, output, triage)` logic
   - Non-zero exit → `command_failed` (strength: low) — a failing run is NOT positive evidence
   - Zero exit, no output → `repo_observed` (strength: high) — ran, nothing complained
   - Zero exit, tests_run == 0 → `repo_observed` — ran, but nothing was asserted
   - Zero exit, tests_failed > 0 → `command_failed` (strength: low) — tests ran but failed
   - Zero exit, tests passed → `command_verified` (strength: high)
4. Compute output SHA-256 for audit trail: `compute_output_hash(stripped_output)`

**Mini verification-resume trigger:** if any of these occur:
- Same command fails 2+ times across repeated /vibe-done runs (detected via audit trail in existing VERIFY.md)
- Repeated downgraded success (exit 0 but 0 tests, twice)
- Evidence classification thrash (oscillating between labels for same criterion)

When triggered, emit before the classification step:
> ⚠️ **Verification mini-resume:**
> - Last command: `[cmd]` — exit code [N], [X] tests run
> - Evidence: [label] (reason for downgrade if applicable)
> - Safest next action: [fix failing test / add tests / verify manually]

### 3.8. Simplicity check (Complete candidates only)
Skip if already classifying as Not Ready or Partially Complete.

Scan the files the user says changed. Ask:
- Is any abstraction doing work that a plain function or simple conditional would handle?
- Is any library dependency doing something 5 lines of stdlib would cover?
- Is the same thing done two different ways in the same file?

If yes: add a brief note to the Known Gaps section of VERIFY.md as:
`[SIMPLICITY] [description] — consider simplifying before next feature`

This is not a blocker and does not change the classification. It is a forward flag only.

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
`VERIFY.md` is a live snapshot. On repeated `/vibe-done` runs, **overwrite entirely** — do not append. Preserve any `## Manual notes` section if it exists in the existing VERIFY.md.

Create or overwrite `features/<feature-id>/VERIFY.md`:

```markdown
# Verification: [Feature Name]

## What was built
[Concise summary from the conversation]

## Acceptance criteria
- [x] [Criterion] — command_verified: [how verified / command run]
- [x] [Criterion] — repo_observed: [what was inspected]
- [x] [Criterion] — user_reported: [USER_REPORTED] [what user stated]
- [ ] [Criterion] — not done

## Known gaps
- [Anything incomplete or needing follow-up, or "None"]

## Verification summary
[X/Y criteria verified] | Evidence strength: [high/medium/low/none] | Touched files: [list or "not tracked"]

## Status
[Complete / Partially Complete / Not Ready to Close]

<!-- audit_trail
| criterion | label | command | exit_code | timestamp | output_sha256 |
|-----------|-------|---------|-----------|-----------|--------------|
| [criterion text truncated to 40 chars] | [label] | [command] | [0/-1] | [ISO-8601] | [sha256 prefix...] |
-->
```

**Audit trail rules:**
- Add one row per command-verified criterion
- Preserve rows from existing VERIFY.md audit trail (do not discard old entries)
- SHA-256 is computed from ANSI-stripped output
- Timestamps are ISO-8601 UTC

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

Present the Git Ghost block (v2 — includes verification summary):

> **Git Ghost — copy and run this yourself (VibeCode never executes git):**
> ```
> git add -A && git commit -m "feat: FEATURE-NNN-slug [truncated literal title]"
> ```
> Verification: [X/Y command_verified] | Evidence strength: [high/medium/low]
> [If on a feature branch matching this feature:]
> This branch can now be merged to master.
> [If dirty working tree:]
> Working tree has uncommitted changes — review before committing.
> [If branch does not match active feature:]
> ⚠️ Branch mismatch: on `[sanitized branch]` but active feature is `FEATURE-NNN`. Verify before committing.

If git is unavailable or not a git repo: skip silently.

**First feature only:** if SESSION_LOG.md had no prior `## Session` entries before the one just written:
> If your project doesn't have a README.md yet, consider adding one — even a single paragraph helps future you.

### 7.8. Auto-compaction (Complete or Partially Complete only)
After writing SESSION_LOG.md, automatically compact project state to `.claude/context/`.

**Skills manage JSON directly** — write the artifact using the Write tool without invoking Python subprocesses.

**Write `.claude/context/project_state.json`:**
```json
{
  "schema_version": 1,
  "generator_version": "009",
  "project": "[name from PROJECT_CONTEXT.md]",
  "active_feature": "",
  "workflow_mode": "idle",
  "risk_flags": ["[any risk flags from this session]"],
  "verification_readiness": "[high/medium/low/none from VERIFY.md]",
  "last_completed_feature": "[this feature ID]",
  "recent_files": ["[top changed files from this session]"],
  "command_registry": {"[key]": "[value from AGENTS.md command registry]"},
  "last_compacted": "[current ISO-8601 UTC timestamp]",
  "created_at": "[ISO-8601]",
  "updated_at": "[ISO-8601]",
  "derived_from": "vibe-done",
  "checksum": ""
}
```

**Write `.claude/context/feature_FEATURE-NNN.json`:**
```json
{
  "schema_version": 1,
  "generator_version": "009",
  "feature_id": "[FEATURE-NNN-slug]",
  "title": "[literal spec title]",
  "status": "[complete/partial/not-ready]",
  "changed_files": ["[files changed this session]"],
  "unresolved_items": ["[open criteria or empty]"],
  "contextual_pointer": "[context pointer from session log]",
  "evidence_grade": "[high/medium/low/none]",
  "commands_used": ["[verification commands run]"],
  "verification_summary": {"tests_run": null, "tests_failed": null},
  "active_risks": ["[any open risks]"],
  "complexity": "[trivial/normal/complex/high-risk from SPEC.md]",
  "checkpoint_id": "[sha256 prefix of active HEAD or 'no-git']",
  "created_at": "[ISO-8601]",
  "updated_at": "[ISO-8601]",
  "derived_from": "vibe-done"
}
```

**Rules:**
- Checksum field: compute SHA-256 of the artifact content excluding the checksum field itself (use `src/helpers/compaction.py` if available, or leave checksum as empty string — a missing checksum triggers reconstruction on resume, which is safe)
- Fail safely: if compaction write fails for any reason, log a warning in the closing report and do not block closure
- For Not Ready to Close: skip compaction (feature is still active)

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
