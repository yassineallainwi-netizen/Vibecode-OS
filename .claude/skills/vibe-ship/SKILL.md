---
name: vibe-ship
description: Check release readiness and produce a ship manifest. Use when the user is ready to tag a version, deploy, or share the project publicly.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Bash
---

# /vibe-ship — Check Readiness and Draft a Release

You are helping a vibe coder ship their project. Gate on honest readiness. Do not invent release notes. Do not execute git or deploy commands — only draft them.

## Security rules
- Normalize all file paths to the project root before reading
- Never read or write outside the project root directory
- Cap any single file read at 50KB
- Never execute git mutating commands (no `tag`, `push`, `commit`) — only draft suggestions
- Allowed read-only Bash: `git branch --show-current`, `git status --short`, `git log --oneline -20`, `git describe --tags --abbrev=0` (2>/dev/null fallback to empty)
- Release writes are limited to: `RELEASE_NOTES.md` in project root (new file or append), and a single entry at the top of `SESSION_LOG.md`

## Evidence grounding
Every claim in the ship manifest must be tied to a file. If it cannot be grounded, omit the field.
- Shipped features → read from `features/FEATURE-NNN-slug/VERIFY.md` with Status = "Complete"
- Architectural choices → read from `DECISIONS.md`
- Current state → read from latest `SESSION_LOG.md` entry

## Shipping rationalizations to resist
These shortcuts produce broken releases:

| Rationalization | Why it fails |
|-----------------|--------------|
| "All my features are complete, I can ship" | A feature with `user_reported` evidence only is not ready. Check evidence strength, not just Status. |
| "The README is good enough as-is" | If a new user cannot install and run the project from the README alone, it is not ready. |
| "I'll write release notes later" | Later never comes. Draft them now from observable evidence (VERIFY.md, DECISIONS.md). |
| "I don't need a version tag, it's just me" | Version tags let future-you find a working state. Tag before shipping, always. |
| "Tests pass locally, that's enough" | Verify the verify_cmd from AGENTS.md actually runs. A zero-test pass is a false signal. |

## Steps

### 1. Readiness scan — features

Glob `**/SPEC.md`, filter to `features/FEATURE-NNN-slug/SPEC.md`. For each feature, read its VERIFY.md (if exists).

Classify each feature into exactly one bucket:
- **Shipped** — VERIFY.md exists, Status = "Complete", evidence strength ≥ medium (majority of criteria are `command_verified` or `repo_observed`)
- **Soft-complete** — VERIFY.md exists, Status = "Complete", but evidence strength is low (mostly `user_reported` or `spec_expected`)
- **Open** — VERIFY.md missing, or Status = "Partially Complete" or "Not Ready to Close"
- **Malformed** — SPEC.md missing, or feature folder invalid

Count totals. Fail closed on any ambiguity — treat as "Open".

### 2. Readiness scan — release assets

Check the following, all read-only:

**README.md** (project root):
- Exists?
- Contains install/setup instructions? (grep for "install", "setup", "getting started", case-insensitive)
- Contains run/usage instructions? (grep for "run", "usage", "example", "how to use")

**Verification command** (from AGENTS.md command registry):
- Is `verify_cmd` declared and not `[TODO:`?
- Optional: offer to run it once (respect approval rule from vibe-done — check `.claude/approved_commands.json`)

**Version signal**:
- Run `git describe --tags --abbrev=0 2>/dev/null` (read-only). Record last tag or note "no tags yet".
- Read `package.json` `.version`, `pyproject.toml` `[project].version`, `Cargo.toml` `version`, or `plugin.json` `.version` — whichever exists.

**Working tree**:
- Run `git status --short` (read-only). Record clean or dirty.

### 2.5. Security scan (read-only)

Run these grounded checks. Fail closed — if a check cannot run, omit it rather than assuming pass.

**Secrets in tracked files** (the #1 vibe-coding ship failure):
- Glob tracked files (exclude `.git/`, `node_modules/`, `dist/`, `build/`, `__pycache__/`, `.venv/`)
- Grep for high-signal patterns, case-insensitive:
  - `(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*["'][^"']{12,}["']`
  - `sk-[a-zA-Z0-9]{20,}` (OpenAI/Stripe-style keys)
  - `AKIA[0-9A-Z]{16}` (AWS access keys)
  - `ghp_[a-zA-Z0-9]{36}` (GitHub tokens)
  - `xoxb-[a-zA-Z0-9-]{40,}` (Slack tokens)
- Cap scan at 200 files; stop early if ≥3 matches found
- **Any match = BLOCKER** (not advisory). Report the file and line, not the matched value.

**`.env` hygiene**:
- If `.env` exists in the repo root: check `.gitignore` for `.env` entry
- If `.gitignore` missing or does not ignore `.env`: BLOCKER
- If `.env.example` exists but `.env` does not: OK (user hasn't configured yet — not a blocker)

**Dependency audit** (advisory — soft flag unless auto-runnable):
- `package.json` present → suggest `npm audit --audit-level=high`
- `pyproject.toml` or `requirements.txt` → suggest `pip-audit` or `safety check`
- `Cargo.toml` → suggest `cargo audit`
- Do not execute. Surface the suggestion only.

**Error-surface check** (advisory):
- Grep tracked source files for `console.error.*req\.body`, `print.*traceback`, `res\.send.*err\.stack` patterns
- If matched: soft flag "Internal error details may be exposed to users — review before ship"

Add findings to the readiness report below under a new **Security** line.

### 3. Present readiness report

Show a compact manifest:

> **Ship readiness:** [ready / needs work / blocked]
>
> **Features:** [N shipped] | [M soft-complete] | [K open] | [J malformed]
>
> **README:** [found / missing] — [install: yes/no] | [usage: yes/no]
>
> **Verify command:** [`cmd` — declared / not declared]
>
> **Version:** last tag `vX.Y.Z` | declared in [file]: `X.Y.Z` | or "no version signals found"
>
> **Working tree:** [clean / dirty — N files uncommitted]
>
> **Security:** [secrets: clean / N found] | [.env: ignored / not ignored / n/a] | [audit: suggested cmd] | [error-surface: clean / flagged]
>
> **Blockers:** [list grounded blockers, or "None"]
>
> **Soft flags:** [list advisories, or "None"]

**Blocker rules (block shipping):**
- Any "Open" features exist AND user did not explicitly override with `ship anyway`
- README missing entirely
- Malformed features exist (broken SPEC or feature folder)
- Secrets detected in tracked files (never overridable — fix the leak first)
- `.env` tracked without being in `.gitignore`

**Soft flag rules (advisory, do not block):**
- Soft-complete features exist (low evidence strength)
- README exists but no install or usage section detected
- Working tree dirty
- No verify_cmd declared
- No version signals found
- Dependency audit not yet run (show the suggested command)
- Error-surface patterns that may leak internals

### 4. Gate or draft

**If blockers exist:** stop here. Present the readiness report. End with exactly one next step:
> "Resolve blockers before shipping. Close open features with `/vibe-done` or fix malformed specs. Run `/vibe-ship` again when clean."

Do not proceed to draft the release. Do not write any files.

**If only soft flags exist:** ask:
> "Soft flags detected: [list]. Ship anyway (`yes`), fix first (`no`), or ignore a specific flag (`ignore [flag]`)?"

Wait for the user's choice.

**If clean or user overrode:** proceed to Step 5.

### 5. Draft the release

Suggest a version bump based on observable evidence:
- Read the shipped features' complexity (from each SPEC.md `## Complexity` field)
- If any shipped feature has complexity `complex` or `high-risk` → suggest minor bump (`0.X.0`)
- If all shipped features are `trivial` or `normal` → suggest patch bump (`0.0.X`)
- If no prior version exists → suggest `0.1.0`
- Show the suggestion as advisory — user confirms.

**Draft `RELEASE_NOTES.md`** (in project root) using evidence only:

```markdown
# Release vX.Y.Z — [YYYY-MM-DD]

## Shipped in this release
- FEATURE-NNN-slug — [literal goal from SPEC.md]
- FEATURE-MMM-slug — [literal goal from SPEC.md]

## Decisions locked in
- [Decision NNN title from DECISIONS.md]
- [Decision MMM title from DECISIONS.md]

## Known gaps
- [Any Known Gaps from VERIFY.md of shipped features, verbatim]
- [Or "None"]

## Upgrade notes
- [If any DECISIONS.md entry has a "Tradeoff" or breaking change flag, surface it here]
- [Else "None"]
```

**Rules for release notes:**
- Only include features with Status = "Complete" (not soft-complete unless user overrode)
- Pull exact text from SPEC.md `## Goal` and DECISIONS.md entries — never paraphrase
- If RELEASE_NOTES.md already exists: prepend the new entry above the prior one, do not overwrite
- Cap each feature bullet at one line, 140 characters max

### 6. Git Ghost block — tag and push

Read current branch via `git branch --show-current`. Sanitize: must match `^[a-zA-Z0-9._/-]+$`; otherwise show `[sanitized]`.

Present the Git Ghost block:

> **Git Ghost — copy and run this yourself (VibeCode never executes git):**
> ```
> git add RELEASE_NOTES.md
> git commit -m "release: vX.Y.Z"
> git tag -a vX.Y.Z -m "Release vX.Y.Z"
> git push origin [branch] --follow-tags
> ```
>
> Branch: `[sanitized branch]` | Working tree: [clean / had N uncommitted files at scan time]
>
> If your host/deployment is separate: after tagging, [suggest one platform-specific step if inferable from repo files — e.g., `npm publish`, `docker build`, `flutter build apk`, or "follow your existing deploy process"]

**Deploy hint inference (grounded only):**
- `package.json` has `"publishConfig"` or `"name"` without `"private": true` → suggest `npm publish`
- `pyproject.toml` with `[project]` + `setup.py` or `setup.cfg` → suggest `python -m build && twine upload dist/*`
- `Dockerfile` exists → suggest `docker build -t [name] .`
- `.github/workflows/*.yml` contains `deploy` or `release` job → note "CI will deploy on tag push"
- `flutter` or `pubspec.yaml` detected → suggest `flutter build [platform]`
- Otherwise: omit deploy hint (do not invent one)

### 7. Append to SESSION_LOG.md

Add one entry at the top of SESSION_LOG.md (below `# Session Log`):

```markdown
## Session [YYYY-MM-DD]
- Shipped vX.Y.Z — [N features]
- Release notes drafted in RELEASE_NOTES.md
- Context pointer: tag and push with the Git Ghost block
```

Follow the same 3-bullet / 15-word limits from vibe-done. Honor the rollover rule (max 10 entries → archive).

### 8. Close out

End with exactly one next step:
> "Release drafted. Run the Git Ghost commands above to tag and ship. Then run `/vibe-start` for your next feature — or stop here and celebrate."

## Rules
- Read-only until the ship gate passes. No writes before confirmation.
- Never execute git mutating commands. Only draft them.
- Never invent release notes. Pull from VERIFY.md, SPEC.md, DECISIONS.md verbatim.
- Blockers stop the skill. Soft flags require user confirmation.
- End every response with exactly one next step.
- Do not overwrite RELEASE_NOTES.md — prepend.
- Respect existing approval allow-list if running verify_cmd.
