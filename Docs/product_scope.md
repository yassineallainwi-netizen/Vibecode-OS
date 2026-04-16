# Product Scope

## Product Vision
VibeCode OS is the missing operating system for vibe coding. It gives Claude Code persistent memory, automatic structure, and verification — so projects built by non-engineers actually work and don't fall apart across sessions.

## Core Problem
People using AI coding tools (Claude Code, Cursor, etc.) to build real projects hit the same walls:
- Claude forgets everything between sessions
- Features get half-built with no record of what works
- No specs means Claude guesses requirements and builds the wrong thing
- No testing means bugs ship silently
- No handoff notes means you can't explain what was built to anyone (including yourself next week)

These problems compound. A project that starts exciting becomes a tangled mess within two weeks.

## Primary User
Solo builders using Claude Code who are NOT professional software engineers. They can describe what they want in plain language but cannot review code quality, write tests themselves, or debug complex issues without AI help. They are building real things — SaaS apps, internal tools, automations, websites — not just experimenting.

## Key Use Cases
1. Starting a new feature with a clear spec before any code is written
2. Resuming work after days or weeks away with full context restored
3. Knowing at any point what's been built, what's been tested, and what's still open
4. Finishing a feature with confidence that it actually works
5. Handing off or explaining what was built (to a client, a cofounder, or future-you)

## In Scope (v1 — Free, Open Source)
- `/vibe-start` command — creates spec, guides requirements gathering; inception mode for day-zero repos
- `/vibe-resume` command — restores context from session log
- `/vibe-status` command — shows what's done, what's open, what's broken
- `/vibe-done` command — runs verification, writes session summary, closes feature
- `/vibe-ship` command — readiness gate + security scan + release notes draft
- PROJECT_CONTEXT.md — persistent project identity and architecture notes
- SESSION_LOG.md — automatic session memory across conversations
- Feature folders with SPEC.md and VERIFY.md
- `install.py` — one-command setup for any repo

## Out of Scope (v1)
- Enforcement hooks (blocking writes, requiring specs) — v2 opt-in
- Cloud sync, dashboards, or web UI
- Team features, permissions, or collaboration
- GitHub Action / CI integration
- Paid tier billing or accounts
- PDF export or client-facing reports
- Support for non-Claude-Code tools (Cursor, Copilot, etc.)

## Future Paid Tier (v2+, $9-19/mo)
- Automatic enforcement hooks (opt-in)
- GitHub PR gate with verification summary
- Shareable proof-of-delivery links for client work
- Project health dashboard (local web UI)
- Priority support and templates for common project types

## Success Metrics
- 50+ GitHub stars within 3 months
- 10+ weekly active users within 3 months
- 3+ unsolicited testimonials or "this saved my project" stories
- Clear signal from users that they'd pay for enforcement/PR features
- Path to $1,000/mo MRR identified and validated

## Risks
- Product risk: Users may not adopt structure even when it's easy — Claude needs to do ALL the work
- Usability risk: Non-engineers may find even lightweight structure intimidating
- Market risk: Claude's built-in memory features may improve enough to reduce the need
- Competition risk: Similar tools may emerge from Anthropic, Cursor, or others
- Distribution risk: With no audience, reaching first users requires content that resonates
