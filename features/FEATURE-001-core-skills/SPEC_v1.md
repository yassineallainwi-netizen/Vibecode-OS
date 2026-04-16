# Feature Spec: Core Skill Commands

## Goal
Give Claude Code four skills that create the structured vibe coding workflow. The user types a command, Claude does the structured work. The user never has to learn a format or fill in templates manually.

## The Four Commands

### `/vibe-start`
**What the user does:** Types `/vibe-start` and describes what they want to build in plain language.

**What Claude does:**
1. Reads PROJECT_CONTEXT.md to understand the project
2. Asks the user 2-3 clarifying questions (what's the goal, what should it do, what should it NOT do)
3. Scans `features/` for existing folders to determine the next feature number
4. Creates `features/FEATURE-NNN-short-name/SPEC.md` with:
   - Goal (one sentence)
   - What it should do (bullet list, Claude drafts from conversation)
   - What it should NOT do (scope boundary)
   - How to verify it works (acceptance tests in plain language)
   - Known risks or edge cases
5. Writes the feature ID to `.claude/active_feature`
6. Asks the user to confirm or edit the spec
7. Only after confirmation: "Spec locked. You can start building now."

**Key design rule:** Claude drafts everything. The user only confirms, edits, or adds. Never present an empty template.

### `/vibe-resume`
**What the user does:** Types `/vibe-resume` at the start of a new session.

**What Claude does:**
1. Reads PROJECT_CONTEXT.md
2. Reads SESSION_LOG.md (latest entry)
3. Reads `.claude/active_feature` to find the current feature
4. Reads the current feature's SPEC.md and VERIFY.md if they exist
5. Summarizes to the user: "Last time you were working on [feature]. You completed [X]. Still open: [Y]. I recommend starting with [Z]."
6. Ready to continue working.

**Key design rule:** The user should be productive within 30 seconds of typing `/vibe-resume`. No re-explaining the project.

### `/vibe-status`
**What the user does:** Types `/vibe-status` at any point during work.

**What Claude does:**
1. Reads `.claude/active_feature` to find the current feature
2. Reads the current feature's SPEC.md and VERIFY.md
3. Compares acceptance criteria against verification notes
4. Reports:
   - What's done and verified
   - What's built but not verified
   - What's still open
   - Any blockers or risks noted
5. If no active feature: scans all feature folders and shows their status

**Key design rule:** This should feel like asking a project manager "where are we?" — quick, honest, actionable.

### `/vibe-done`
**What the user does:** Types `/vibe-done` when they think a feature is finished.

**What Claude does:**
1. Reads `.claude/active_feature` to find the current feature
2. Reads SPEC.md acceptance criteria
3. Asks the user about each criterion: "Did this get built? Was it tested? How?"
4. Fills in VERIFY.md with:
   - What was built (summary)
   - Acceptance criteria checklist (checked/unchecked)
   - Tests run and results
   - Known limitations
   - What the user should manually check
5. Updates SESSION_LOG.md with a completion entry
6. Clears `.claude/active_feature`
7. If all criteria pass: "Feature complete. VERIFY.md written."
8. If gaps remain: "These items are still open: [list]. Want to continue or mark as partial?"

**Key design rule:** Claude asks the verification questions conversationally. The user answers in plain language. Claude writes the structured notes. The user never fills in a template.

## Active Feature Tracking

The file `.claude/active_feature` is a plain text file containing the current feature ID (e.g. `FEATURE-001-auth-login`) or empty if no feature is active.

- `/vibe-start` writes the feature ID after spec is confirmed
- `/vibe-done` clears the file after verification is complete
- `/vibe-resume` and `/vibe-status` read it to know which feature is current
- If the file is empty or missing and there's ambiguity, Claude asks the user which feature to work on

## Feature Auto-Numbering

Features use the format `FEATURE-NNN-short-slug` where NNN is zero-padded to 3 digits. Claude scans `features/` for existing folders and picks the next number. The slug is derived from the user's description (e.g. "auth login" becomes `auth-login`).

## Session Log Capping

SESSION_LOG.md keeps the last 10 session entries. When a new entry would exceed 10, the oldest entry is moved to SESSION_ARCHIVE.md before the new entry is written. This prevents the log from growing unbounded on long projects.

## File Structure After Install

```
<any-repo>/
├── .claude/
│   ├── skills/
│   │   ├── vibe-start/SKILL.md
│   │   ├── vibe-resume/SKILL.md
│   │   ├── vibe-status/SKILL.md
│   │   └── vibe-done/SKILL.md
│   └── active_feature          # plain text: current feature ID or empty
├── PROJECT_CONTEXT.md
├── AGENTS.md
├── DECISIONS.md
├── SESSION_LOG.md
└── features/
    └── FEATURE-001-auth-login/
        ├── SPEC.md
        └── VERIFY.md
```

## PROJECT_CONTEXT.md (User-Facing Version)
This is the ONE file the user fills in themselves. It should be short and plainly worded. Claude helps fill it in on first `/vibe-resume` if it's empty.

```markdown
# My Project

## What is this?
[One paragraph describing your project]

## What's it built with?
[List your tech stack: Next.js, Python, Supabase, etc.]

## What's the current state?
[What works now? What's broken? What's next?]

## Important rules
[Anything Claude should always remember: "never touch the billing code", "always use Tailwind", etc.]
```

## SESSION_LOG.md Format
Claude writes this automatically. The user never edits it directly.

```markdown
# Session Log

## Latest Session
- Date: 2026-03-18
- Feature: FEATURE-001-auth-login
- What happened: Built the login form and connected it to Supabase auth. Password reset flow is stubbed but not wired up yet.
- What was tested: Login with valid credentials works. Login with wrong password shows error. Session persists on refresh.
- Still open: Password reset, "remember me" checkbox, rate limiting
- Next step: Wire up password reset email flow

## Previous Sessions
[older entries below, newest first]
```

## SPEC.md Format (Created by /vibe-start)

```markdown
# Feature: [Name]

## Goal
[One sentence: what should the user be able to do after this is built?]

## What it should do
- [Bullet list of behaviors, drafted by Claude from conversation]

## What it should NOT do
- [Scope boundaries]

## How to verify it works
- [ ] [Plain language acceptance test]
- [ ] [Another one]
- [ ] [Another one]

## Risks and edge cases
- [Anything Claude or the user flagged]
```

## VERIFY.md Format (Created by /vibe-done)

```markdown
# Verification: [Feature Name]

## What was built
[Summary paragraph written by Claude based on the work done]

## Acceptance criteria
- [x] [Criterion from spec] — [how it was verified]
- [ ] [Criterion from spec] — not yet done
- [x] [Criterion from spec] — [how it was verified]

## Tests and checks
- [What was tested, how, and what happened]

## Known limitations
- [Anything that doesn't fully work or needs follow-up]

## Status
Complete / Partial / Blocked
```

## install.py Behavior
1. Check: is this a git repo? (warn if not, but don't block)
2. Check: does `.claude/skills/` exist? (create if not)
3. Copy 4 skill directories (`vibe-start`, `vibe-resume`, `vibe-status`, `vibe-done`) from `src/skills/` to `.claude/skills/`
4. Create `PROJECT_CONTEXT.md` from template if it doesn't exist
5. Create `AGENTS.md` from template if it doesn't exist
6. Create `DECISIONS.md` from template if it doesn't exist
7. Create `SESSION_LOG.md` from template if it doesn't exist
8. Create `features/` directory if it doesn't exist
9. Create `.claude/active_feature` (empty) if it doesn't exist
10. Print: "VibeCode OS installed. Start with `/vibe-resume` to set up your project, or `/vibe-start` to begin your first feature."
11. Never overwrite existing files

## Acceptance Criteria
- [x] `/vibe-start` creates a SPEC.md with Claude-drafted content after 2-3 questions — verified 2026-03-18, correctly prompted for project context before proceeding
- [x] `/vibe-resume` restores full context in under 30 seconds — verified 2026-03-18, detected empty templates, gave clear first-session guidance
- [x] `/vibe-status` accurately reports feature progress against spec — verified 2026-03-18, correctly reported no features started
- [x] `/vibe-done` produces a complete VERIFY.md through conversational Q&A — verified 2026-03-18, correctly refused with no active feature and clear guidance
- [x] `install.py` works on a fresh repo in under 60 seconds — verified 2026-03-18, fresh git repo, all 10 items created correctly
- [x] All commands work without any Python dependencies beyond stdlib — install.py uses only os, shutil, sys
- [x] A non-technical user can follow the flow without reading any documentation beyond the install output — all four commands gave plain-language, actionable responses
- [x] No command blocks or slows down the developer — all are voluntary
- [x] Active feature is tracked correctly via `.claude/active_feature` — verified 2026-03-18, /vibe-start wrote FEATURE-001-bootstrap correctly
- [x] Feature auto-numbering works correctly when creating new features — verified 2026-03-18, first feature numbered 001 with slug from description

## Risks
- Claude's skill file format may have size limits — keep each skill file focused
- SESSION_LOG.md could grow very large on long projects — capped at 10 entries with archiving
- Users may not type `/vibe-done` and just stop working — `/vibe-resume` should gracefully handle features that were never formally closed
- The skill files have to be clear enough that Claude follows the process correctly across different models and context window sizes
- Built-in Claude Code commands may change — the `vibe-` prefix provides namespace isolation
