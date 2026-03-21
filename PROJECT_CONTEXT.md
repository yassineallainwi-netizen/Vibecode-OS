# Project Context

## Project Identity
- Name: VibeCode OS
- One-line summary: A Claude Code skill pack that gives vibe coders structured memory, automatic context persistence, and verification — so AI-assisted projects stop falling apart across sessions.
- Current stage: v2.0.1 — shipped
- Primary owner: Solo founder (side hustle)
- Repository: Local (will move to GitHub when ready)

## Product Goal
Solve the five core problems that cause vibe coding projects to fail:
1. Context decay — Claude forgets what happened last session
2. Scope drift — Claude builds things nobody asked for
3. No verification — no record of what was tested or works
4. No structure — features start mid-conversation with no plan
5. Session fragmentation — work gets lost between chat windows

## Target Users
- Primary: Solo vibe coders using Claude Code to build real projects (SaaS, tools, automations, websites). They are NOT professional engineers. They may be founders, freelancers, designers, or business people who can describe what they want but cannot review code quality themselves.
- Secondary: Technical freelancers using Claude Code for client work who want lightweight delivery evidence.

## Non-Goals
- This is NOT an IDE or editor
- This is NOT a project management tool (no boards, sprints, assignments)
- This is NOT a CI/CD system
- This is NOT targeting teams or enterprises in v1
- This is NOT trying to replace Git workflows — it augments them
- No custom YAML parser — use plain markdown that humans and Claude can both read easily
- No enforcement hooks that block the developer in v1 — helpful, not restrictive

## Core User Outcomes
- Users should be able to: start a session and have Claude immediately know what happened last time
- Users should be able to: describe a feature and get a clear spec before any code is written
- Users should be able to: see what was built, tested, and what's still open at any point
- Users should never have to: manually write long context summaries to remind Claude what's going on
- Users should never have to: wonder "did this feature actually get tested?"
- The product must never: block or slow down the developer — it should feel like a helpful copilot, not a bureaucracy

## Tech Stack
- Runtime: Claude Code (skill files + hooks)
- Language: Python 3.8+ (stdlib only for hooks/scripts)
- File format: Plain markdown (no YAML frontmatter in v1 — just structured markdown sections)
- Storage: Local files in the repo (no database, no cloud, no accounts)
- Distribution: GitHub repo + `install.py` script that copies skills into any project

## Architecture Summary
The product is a set of Claude Code skills (`.claude/skills/<name>/SKILL.md`) and optional hook scripts that live inside the user's repo:

- **Skills** provide four commands: `/vibe-start`, `/vibe-resume`, `/vibe-status`, `/vibe-done` — each is a self-contained skill directory using Claude Code's skills format with YAML frontmatter
- **Context files** (PROJECT_CONTEXT.md, AGENTS.md, DECISIONS.md, SESSION_LOG.md) are structured plain markdown that Claude reads at session start and writes at session end
- **Active feature tracking** via `.claude/active_feature` (plain text file with current feature ID)
- **Compact artifacts** in `.claude/context/` — JSON snapshots for token-efficient session resumption; dead-man's switch triggers full reconstruction after 24h
- **Plugin mode** — `.claude-plugin/` directory with official Claude Code plugin format; coexists with standalone mode; not available in remote sessions
- **Adapter layer** — `src/adapter/` bridges skill-pack and plugin modes: capability detection, War Room bridge, action dispatch
- **No backend, no API, no cloud dependency** — everything is local files

Main data flow:
1. User says `/vibe-start` → Claude reads PROJECT_CONTEXT.md, creates feature folder with SPEC.md, sets active feature
2. User works on tasks → Claude tracks changes in SESSION_LOG.md
3. User says `/vibe-done` → Claude writes verification notes, session summary, clears active feature
4. Next session: user says `/vibe-resume` → Claude reads SESSION_LOG.md and picks up where it left off

## Conventions
### File naming
- All context files: UPPER_CASE.md (PROJECT_CONTEXT.md, AGENTS.md, DECISIONS.md, SESSION_LOG.md)
- Feature folders: features/FEATURE-NNN-short-name/
- Skills: .claude/skills/vibe-*/SKILL.md (one directory per command)

### Principles
- Plain markdown everywhere — no custom formats, no YAML frontmatter
- Claude does the writing — the user describes, Claude fills in structure
- Minimal files — only create what's needed, not a template empire
- Progressive structure — simple projects get simple structure, complex projects get more

## Constraints
- Must work with Claude Code as-is (no modifications to Claude itself)
- Must work offline (no network calls in any script)
- Must be installable in under 60 seconds
- Must not break existing repos (additive only, never overwrites)
- Python 3.8+ only (stdlib, no pip installs)
- Total overhead per session: under 30 seconds of Claude time for context loading

## Definition of Success
The project is successful when:
- A non-technical vibe coder can install it in any repo and immediately get structured sessions
- Context persists reliably across sessions with no manual effort
- At least 50 people star the GitHub repo within 3 months of launch
- At least 10 people actively use it weekly within 3 months
- The path to a paid tier ($9-19/mo) is clear and validated by user feedback

## Current Priorities
1. Runtime hardening and behavioral QA (v2.0.1)
2. Distribution — publish to GitHub and Claude Code plugin marketplace
3. User feedback loop — early adopters, iterate on skill wording
4. Paid tier scoping ($9-19/mo agency features)

## Open Risks
- Claude Code skill format may change — keep skills simple and adaptable
- Users may not read/follow the install instructions — make install as automated as possible
- "Structure" may feel like overhead to casual users — make Claude do all the structural work, user just describes intent
- Competition from similar tools (Claude memory, Cursor rules, etc.) — differentiate on the structured verification and session persistence, not just "rules for AI"
