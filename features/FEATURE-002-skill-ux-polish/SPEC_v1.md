# FEATURE-002-skill-ux-polish

## Goal

Polish the behavior and wording of the four core skills so they feel clear, consistent, and low-friction.

## Why this feature exists

The current skills work, but the UX still feels rough:
- some wording is inaccurate
- outputs are not fully standardized
- responses can be longer than needed
- first-run guidance can be clearer

This feature improves the user-facing experience without changing the core architecture.

## In scope

- polish `/vibe-start`
- polish `/vibe-resume`
- polish `/vibe-status`
- polish `/vibe-done`
- standardize response structures
- reduce token waste in normal operation
- fix known wording inconsistencies

## Out of scope

- template redesign
- README creation
- broken-state recovery logic beyond small wording fixes
- QA checklist creation
- plugin packaging

## Requirements

### UX rules
- responses must be short, direct, and structured
- avoid filler such as "It looks like" or "Let me check"
- every response must end with one clear recommended next step
- all commands shown to the user must use `vibe-*` names only

### Token-efficiency rules
- read only the minimum files needed for the command
- do not repeat file contents back to the user
- do not scan the repo unless needed
- ask at most 2 focused questions at a time

### Output contracts

#### `/vibe-resume`
Must always use:
- project
- current state
- active feature
- important decisions
- recommended next step

#### `/vibe-status`
Must always use:
- feature goal
- completed
- missing
- risks / unknowns
- recommended next step

#### `/vibe-done`
Must classify work as:
- complete
- partially complete
- not ready to close

## Known bug to fix

- `/vibe-status` must not say the `features/` folder is missing when it exists but is empty
- preferred wording:
  - "No feature folders exist yet."
  - or "No features have been started yet."

## Acceptance criteria

- [ ] `/vibe-resume` gives clearer first-run guidance
- [ ] `/vibe-start` asks focused questions
- [ ] `/vibe-status` always uses the 5-part structure
- [ ] `/vibe-done` uses explicit complete / partial / not-ready language
- [ ] responses are shorter and more consistent
- [ ] no command output uses old non-namespaced command names

## Verification

- run `/vibe-resume` on a blank install
- run `/vibe-start` with a vague feature request
- run `/vibe-status` with and without an active feature
- run `/vibe-done` on incomplete work
- confirm responses are concise and structured
