# FEATURE-002-workflow-polish

## Goal

Polish the current VibeCode OS workflow so it feels clear, reliable, and low-friction for a solo builder using Claude Code.

This feature improves usability and consistency. It does not change the core architecture.

## Why this feature exists

Feature 001 proved the core system works:
- installer creates the repo OS
- Claude Code discovers the skills
- `/vibe-start`, `/vibe-resume`, `/vibe-status`, and `/vibe-done` run
- active feature tracking and auto-numbering work

But the experience still has rough edges:
- some wording is inaccurate
- outputs are not standardized enough
- templates can be easier to use
- edge cases are not defined tightly enough
- responses can waste tokens

## Desired outcome

A first-time user should be able to:
1. install VibeCode OS
2. understand the system quickly
3. start a feature without confusion
4. inspect status in a predictable format
5. close or partially close a feature cleanly
6. avoid token waste during normal use

## In scope

- polish `/vibe-start`
- polish `/vibe-resume`
- polish `/vibe-status`
- polish `/vibe-done`
- improve templates
- add `README.md`
- define strict recovery paths
- reduce unnecessary file reads and verbose output

## Out of scope

- plugin packaging
- MCP, hooks, external integrations
- multi-user features
- cloud sync
- architecture redesign

## Product rules

### 1. UX and wording rules

All four skills must follow these rules:

- **Zero-hallucination:** never claim a file, folder, or feature state without checking it first
- **Action-oriented:** every response ends with one recommended next step
- **Command fidelity:** only show real `vibe-*` command names
- **Consistent voice:** short, direct, calm, structured
- **No filler:** avoid phrases like "It looks like", "Here is the status", "Let me check"
- **Minimal questioning:** ask only what is needed to proceed

### 2. Token-efficiency rules

Skills must avoid wasting tokens.

Rules:
- read only the minimum files needed for the current command
- do not scan the whole repo unless recovery requires it
- do not repeat file contents back to the user
- do not restate obvious context already established in the same command
- keep normal responses under 8 short bullets or equivalent short paragraphs
- ask at most 2 focused questions at a time
- prefer one concrete recommendation over multiple optional suggestions
- avoid "verification theater": do not perform or describe checks that do not change the answer

Command-specific limits:
- `/vibe-resume`: read `PROJECT_CONTEXT.md`, `DECISIONS.md`, `SESSION_LOG.md`, `.claude/active_feature`, and only the active feature files if an active feature exists
- `/vibe-status`: read `.claude/active_feature`, active feature `SPEC.md`, and `VERIFY.md` if present; do not read unrelated files
- `/vibe-done`: read `.claude/active_feature`, active feature `SPEC.md`, and existing `VERIFY.md`; only inspect more if completion is unclear
- `/vibe-start`: read only enough global context to create a correct feature spec

### 3. Standard output contracts

#### `/vibe-resume`
Output must use this structure:
- project
- current state
- active feature
- important decisions
- recommended next step

First-run behavior:
- if templates are still blank, give numbered setup guidance
- prompt the user to fill `PROJECT_CONTEXT.md` before feature work

#### `/vibe-status`
Output must always use this exact structure:
- feature goal
- completed
- missing
- risks / unknowns
- recommended next step

#### `/vibe-done`
Must classify the feature as one of:
- complete
- partially complete
- not ready to close

File updates and messaging must match that state.

### 4. Template improvements

Improve:
- `src/templates/PROJECT_CONTEXT.md`
- `src/templates/AGENTS.md`
- `src/templates/DECISIONS.md`
- `src/templates/SESSION_LOG.md`

Requirements:
- easy for a first-time user to fill
- short and useful
- easy for Claude to parse later
- no intimidating placeholder walls
- each section should directly support later resume/status/done behavior

### 5. README

Create `README.md` that explains:
- what VibeCode OS is
- who it is for
- what gets installed
- what each command does
- normal workflow
- how to test it
- current limitations

Keep it concise and practical.

### 6. Edge-case recovery paths

The skills must handle these states deterministically.

#### Case: `features/` exists but is empty
Response:
- say "No features have been started yet."
- recommend `/vibe-start`

#### Case: `.claude/active_feature` is missing or empty
Behavior:
- scan `features/` only when needed
- if no feature folders exist: recommend `/vibe-start`
- if one feature folder exists: ask whether to resume it or start a new one
- if multiple feature folders exist: suggest the most recently modified one and ask the user to confirm

#### Case: `.claude/active_feature` points to a missing folder
Behavior:
- notify the user that the active feature reference is broken
- clear the invalid value
- ask whether to resume an existing feature or start a new one

#### Case: active feature exists but has no `SPEC.md`
Behavior:
- report the feature as malformed
- do not invent status
- recommend repairing the spec first

#### Case: `VERIFY.md` does not exist during `/vibe-done`
Behavior:
- create it from the feature `SPEC.md`
- then record the completion state

#### Case: templates are still blank placeholders
Behavior:
- ask 2–3 specific setup questions
- use the answers to help generate initial content

#### Case: premature `/vibe-done`
Behavior:
- default to **partially complete**
- write what is done and what remains
- keep the feature active

#### Case: `SESSION_LOG.md` exceeds cap
Behavior:
- keep newest 10 entries in `SESSION_LOG.md`
- move older entries to `SESSION_ARCHIVE.md`
- preserve chronological order

## Blank placeholder rule

A file counts as a blank placeholder if it still contains only template headings, instructional text, or obvious placeholder markers and no project-specific content.

Skills should treat blank placeholders as missing real context.

## Implementation notes

### Known wording bug to fix
`/vibe-status` must not say the `features/` folder is missing when it exists but contains no feature folders.

Preferred wording:
- "No feature folders exist yet."
- or "No features have been started yet."

### Done-state rule
`/vibe-done` must:
- create or update `VERIFY.md`
- record what is complete, checked, and remaining
- clear `.claude/active_feature` only when the feature is truly complete
- keep the feature active when work is partial

### Most-recent feature rule
When choosing a likely feature candidate during recovery, use the most recently modified feature directory.

## Acceptance criteria

### Core UX
- `/vibe-resume` gives clear first-run guidance on a blank install
- `/vibe-start` asks focused clarifying questions
- `/vibe-status` always uses the 5-part structure
- `/vibe-done` uses explicit complete / partial / not-ready logic

### Accuracy
- no message contradicts actual repo state
- command names shown to users always use `vibe-*`
- active feature state is reported accurately
- Claude never invents feature state without checking the needed files

### Token efficiency
- commands read only the files needed for their task
- responses are concise and do not repeat file contents
- recovery scans happen only when necessary
- no unnecessary repo-wide verification is performed

### Templates and docs
- templates are clearer and shorter
- `README.md` exists and is useful to a first-time user

### Edge cases
- all listed edge cases produce deterministic recovery behavior

## Manual QA checklist

- [ ] Run installer in a fresh repo and confirm `.claude/` and templates exist
- [ ] Run installer again and confirm no user data is overwritten
- [ ] Run `/vibe-resume` on blank install and confirm setup guidance appears
- [ ] Run `/vibe-start` with a vague request and confirm Claude asks clarifying questions before writing `SPEC.md`
- [ ] Check `.claude/active_feature` and confirm it matches the created feature ID
- [ ] Run `/vibe-status` and confirm the 5-part structure
- [ ] Run `/vibe-done` with partial work and confirm `VERIFY.md` is created, remaining work is recorded, and feature stays active
- [ ] Run `/vibe-done` with complete work and confirm the feature closes and `.claude/active_feature` is cleared
- [ ] Break `.claude/active_feature` and confirm recovery is correct
- [ ] Create multiple feature folders with no active feature and confirm Claude asks which one to resume

## Definition of done

This feature is done when:
- the workflow feels clearer and more consistent
- token use is noticeably leaner
- known wording issues are fixed
- templates are improved
- `README.md` exists
- edge cases are deterministic
- manual QA confirms a first-time user can follow the happy path without confusion