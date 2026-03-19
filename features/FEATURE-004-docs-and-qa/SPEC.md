# FEATURE-004-docs-and-qa

## Goal

Improve the project documentation and add a practical QA checklist for validating the workflow.

## Why this feature exists

The skills are only usable as a product if a first-time user can understand:
- what this system is
- how to install it
- how to use it
- how to test it

This feature improves usability and maintainability.

## In scope

- improve templates
- create `README.md`
- add a manual QA checklist
- make docs concise and easy to follow

## Out of scope

- changes to skill recovery logic
- changes to skill prompt behavior beyond docs alignment
- plugin packaging

## Template improvements

Improve:
- `src/templates/PROJECT_CONTEXT.md`
- `src/templates/AGENTS.md`
- `src/templates/DECISIONS.md`
- `src/templates/SESSION_LOG.md`

Requirements:
- easy for a first-time user to understand
- short and useful
- easy for Claude to parse later
- no intimidating placeholder walls
- sections should map directly to what the skills later read

## README

Create `README.md` that explains:
- what VibeCode OS is
- who it is for
- what gets installed
- what each command does
- the normal workflow
- how to test it
- current limitations

Keep it concise and practical.

## Manual QA checklist

Include this checklist:

- [ ] Run installer in a fresh repo and confirm `.claude/` and templates exist
- [ ] Run installer again and confirm no user data is overwritten
- [ ] Run `/vibe-resume` on blank install and confirm setup guidance appears
- [ ] Run `/vibe-start` with a vague request and confirm clarifying questions happen before `SPEC.md`
- [ ] Check `.claude/active_feature` and confirm it matches the created feature ID
- [ ] Run `/vibe-status` and confirm the 5-part structure
- [ ] Run `/vibe-done` with partial work and confirm `VERIFY.md` is created and feature stays active
- [ ] Run `/vibe-done` with complete work and confirm the feature closes and `.claude/active_feature` is cleared
- [ ] Break `.claude/active_feature` and confirm recovery works
- [ ] Create multiple feature folders with no active feature and confirm Claude asks which one to resume

## Acceptance criteria

- [ ] templates are clearer and shorter
- [ ] `README.md` exists and is useful
- [ ] QA checklist exists and is actionable
- [ ] a first-time user can understand install and workflow without extra explanation

## Verification

- review each template for clarity
- read README as if you are a new user
- execute the manual QA checklist
- record any gaps in feature verification
