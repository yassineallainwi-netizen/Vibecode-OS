# Decisions Log

---

## Decision 001
- Date: 2026-03-18
- Status: Accepted
- Context: Choosing between YAML frontmatter and plain markdown for structured files
- Decision: Use plain markdown with structured sections (## headings) instead of YAML frontmatter
- Why: The target user is non-technical. YAML frontmatter is fragile (indentation, colons, missing delimiters) and requires a custom parser. Plain markdown is readable, editable, and Claude can parse it naturally without any custom code.
- Tradeoff: Slightly less machine-parseable than YAML. Acceptable because Claude is the primary reader, not a script.
- Consequence: No custom parser needed. Simpler codebase. Lower maintenance.

---

## Decision 002
- Date: 2026-03-18
- Status: Accepted
- Context: Should v1 include enforcement hooks that block the developer?
- Decision: No enforcement in v1. Skills guide and suggest. Hooks are v2.
- Why: Blocking a non-technical user mid-flow will cause rage-uninstalls. The product needs to build trust first by being helpful. Enforcement can be opt-in later once users understand the value.
- Tradeoff: Users can skip the structure. Acceptable — the goal is adoption first, discipline second.

---

## Decision 003
- Date: 2026-03-18
- Status: Accepted
- Context: Should we target agencies or individual vibe coders?
- Decision: Individual vibe coders first. Agency features (PR gates, proof links, client reports) are a future paid tier.
- Why: Much larger addressable market, easier to reach through content, lower price point but more buyers, no cold sales needed.
- Tradeoff: Slower path to high-value contracts. But faster path to any revenue at all.

---

## Decision 004
- Date: 2026-03-18
- Status: Accepted
- Context: Distribution method — npm, pip, marketplace, or raw files?
- Decision: Simple Python install script + GitHub repo. `python install.py` copies skills and templates into the current repo.
- Why: No ecosystem dependency. Works on any OS. No accounts or auth. Under 60 seconds to install. Target users may not know npm/pip.
- Tradeoff: No auto-updates. Acceptable for v1 — manual update is fine when there are few users.

---

## Decision 005
- Date: 2026-03-18
- Status: Accepted
- Context: How many structured files should a feature require?
- Decision: Two required (SPEC.md, VERIFY.md), one optional (HANDOFF.md for complex features). No PLAN.md or TASKS.md as separate files — those are sections within SPEC.md.
- Why: Four or five files per feature is too much ceremony for a solo vibe coder fixing a CSS bug. Two files (what are we building + did it work) is the minimum viable structure. Claude can expand SPEC.md with a plan and task breakdown internally when the feature is complex enough.
- Tradeoff: Less granularity than the full template pack. Acceptable — the user can always add more structure later.

---

## Decision 006
- Date: 2026-03-18
- Status: Accepted
- Context: The original spec assumed a single `vibecode.md` skill file containing all four commands. Claude Code's actual skill format uses `.claude/skills/<name>/SKILL.md` — one directory per skill. Additionally, command names like `/resume`, `/status`, and `/help` collide with built-in Claude Code commands.
- Decision: Use one skill directory per command in Claude Code's skills format. Namespace all commands with `vibe-` prefix (`/vibe-start`, `/vibe-resume`, `/vibe-status`, `/vibe-done`). Drop the custom `/help` command in v1 — rely on built-in `/help`.
- Why: Matches Claude Code's current recommended format. Each skill is self-contained and independently maintainable. The `vibe-` prefix avoids collisions with built-in commands now and in the future.
- Tradeoff: 4 skill directories instead of 1 file. Some instruction duplication across skills since each is self-contained. Acceptable — independence and correctness outweigh DRY concerns for skill files.
- Consequence: install.py copies 4 directories instead of 1 file. YAML frontmatter is used in SKILL.md files (Claude Code's required format) while all user-facing files remain plain markdown per Decision 001.

---

## Decision 007
- Date: 2026-03-20
- Feature: FEATURE-009-hardened-token-optimization
- Decision: Skills write compact JSON artifacts directly using Write/Edit tools, without spawning Python subprocesses for runtime operations
- Why: Subprocess calls add latency and failure surface in Claude Code environments where subprocess execution may not always be available; skills can write JSON inline
- Tradeoff: JSON schema validation and atomic writes are still handled by helper scripts (compaction.py, context.py) when called explicitly; skill-level writes may lack checksum — triggers reconstruction on resume, which is safe
