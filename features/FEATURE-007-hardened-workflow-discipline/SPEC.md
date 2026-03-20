# Feature: Hardened Workflow Discipline and Project Rules

## Goal
Make VibeCode OS materially stronger on documentation completeness, workflow discipline, and session recovery without turning the workflow into ceremony.

## What it should do
- Replace low-density session recap with a War Room manifest grounded in repo files
- Detect AGENTS.md configuration state using concrete heuristics (byte size, version marker, boilerplate fingerprints) instead of naive `[TODO:]` scan
- Auto-patch AGENTS.md on first feature when confidence is high; offer compact Accept/Edit/Skip when mixed
- Generate and sync a CLAUDE.md bridge from AGENTS.md + PROJECT_CONTEXT.md for native Claude Code session loading
- Scan project root for tech-stack signals before prompting (package.json, pyproject.toml, Cargo.toml, etc.)
- Sanitize feature slugs and validate active_feature format before use
- Detect and halt on FEATURE-NNN collision without guessing
- Draft copy-pasteable git commit suggestions (Git Ghost) after Complete or Force Close — never execute git
- Auto-trigger compressed War Room mini-resume on lost-state conditions
- Surface workflow mode and risk flags from repo evidence
- Switch between novice (interpretive) and expert (terse) output based on repo maturity

## What it should NOT do
- Add new commands
- Block the developer — all guidance is advisory
- Prompt for AGENTS rules on every feature (first feature only, or skip if customized)
- Execute git commands
- Invent rules not supported by repo files
- Halt on AGENTS.md vs CLAUDE.md timestamp drift alone

## Acceptance Criteria
- [ ] AGENTS.md blank detection uses concrete heuristics (version marker, byte size, boilerplate strings)
- [ ] High-confidence uncustomized AGENTS.md → auto-draft from repo scan, no interview
- [ ] Mixed-confidence AGENTS.md → one compact Accept/Edit/Skip prompt only
- [ ] Customized AGENTS.md → skip AGENTS step entirely on new features
- [ ] CLAUDE.md bridge is generated/synced after AGENTS patch
- [ ] CLAUDE.md critical field conflict → halt with user-resolution message
- [ ] /vibe-resume outputs the War Room manifest (all required fields)
- [ ] All War Room fields grounded in files; missing fields omitted (fail closed)
- [ ] Lost-state triggers auto mini-resume, not a questionnaire
- [ ] /vibe-done outputs Git Ghost copy-paste block (Complete + Force Close only)
- [ ] Git commands are never executed
- [ ] Feature slug sanitized to `^[a-z0-9]+(-[a-z0-9]+){0,3}$` max 40 chars
- [ ] FEATURE-NNN collision → halt with explicit message, no guessing
- [ ] Repo maturity inferred; novice vs expert output adapted accordingly
- [ ] /vibe-status surfaces Mode and Risk flags
- [ ] SESSION_LOG.md template uses contextual pointer wording
- [ ] AGENTS.md template has version marker and command registry
- [ ] All existing smoke tests still pass

## Risks and edge cases
- Skill file growth: vibe-done and vibe-resume will grow significantly; track line count
- Template changes must preserve `[TODO:]` markers (smoke test gate)
- CLAUDE.md may not exist in all repos; sync must be safe on first run
- Repo maturity must fail gracefully when git is unavailable
