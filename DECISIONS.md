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

---

## Decision 010
- Date: 2026-04-16
- Feature: feature/spec-template-rewrite
- Status: Accepted
- Decision: Canonical `src/templates/SPEC.md` with required frontmatter (ID, Status, Complexity, Change kind), `## Touches`, per-criterion `[verify=cmd|repo|spec|user]` tags, and an explicit `## Verification plan`. All future features use this template. All historical specs rewritten to it (originals preserved as `SPEC_v1.md`).
- Why: Historical specs used 4 inconsistent schemas across 10 features; `## Complexity` appeared in 1/10 specs; `## Touches` in 0/10; evidence labels `user_reported` and `spec_expected` appeared in 0 VERIFY.md files — the label model was half-dead. A uniform schema makes the spec corpus a reliable substrate for self-improvement loops (hardening-round auto-detect, drift log, evidence-label coverage metrics).
- Tradeoff: Rewriting 10 historical specs is non-trivial effort; rewrites are documentation hygiene only (no scope changes, no reopened features). Original specs preserved as `SPEC_v1.md`.
- Consequence: `/vibe-start` now reads `.claude/templates/SPEC.md` to draft the spec, guaranteeing new features use the canonical format. `/vibe-done` honours `Change kind` and per-criterion `[verify=...]` tags when classifying evidence. `/vibe-status` runs scope-drift check against `## Touches`. Conformance test `tests/smoke/test_spec_conformance.py` gates all future features against the schema.

---

## Decision 009
- Date: 2026-03-21
- Feature: v2.0.1 hardening
- Status: Accepted
- Decision: Strict verification command allow-list — unknown executables are rejected; verification commands must be PATH-based only; no shell execution path
- Why: The advisory allow-list (v2.0.0) silently allowed arbitrary executables, undermining the security goal of the verification workflow. `shell=True` introduced a command-injection vector even after metacharacter filtering. Strict rejection of unknown tools and shell trampolines eliminates both attack surfaces.
- Rules enforced:
  - Executables normalized: basename → lowercase → strip .exe/.cmd/.bat
  - Shell trampolines blocked: cmd, powershell, pwsh, bash, sh, zsh, fish, csh
  - Path separators in executable name → rejected (PATH-based only)
  - Not in TRUSTED_TOOLS → rejected
  - subprocess.run uses `shell=False` + `shlex.split(posix=(os.name != "nt"))`
- Tradeoff: Users with unusual test runners not in TRUSTED_TOOLS must request additions. Acceptable — the trusted list covers all major runtimes and is easy to extend.

---

## Decision 008
- Date: 2026-03-20
- Feature: FEATURE-010-hardened-plugin-delivery
- Decision: Official Claude Code plugin format (`.claude-plugin/plugin.json`) rather than a custom Python runtime surface
- Why: Claude Code's official plugin format provides correct skill loading, capability negotiation, and marketplace distribution; a custom Python runtime would duplicate infrastructure and break future platform integration
- Tradeoff: Plugin not available in remote sessions — standalone `.claude/skills` is the documented fallback, which is fully functional
