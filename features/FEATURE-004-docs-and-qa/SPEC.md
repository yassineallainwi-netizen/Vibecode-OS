# Feature: Docs and QA

- ID: FEATURE-004-docs-and-qa
- Status: Closed
- Date locked: 2026-03-18
- Complexity: trivial
- Change kind: mixed

## Goal
Improve project documentation and add a practical QA checklist so any first-time user can install, understand the workflow, and test it without extra guidance.

## Touches
- README.md
- src/templates/PROJECT_CONTEXT.md
- src/templates/AGENTS.md
- src/templates/DECISIONS.md
- src/templates/SESSION_LOG.md

## Acceptance criteria
- [x] [verify=spec] Templates are clearer and shorter than F-001 originals (filler reduced, structure preserved)
- [x] [verify=repo] `README.md` exists at repo root with all required sections: what it is, who it is for, what gets installed, what each command does, normal workflow, known limitations
- [x] [verify=spec] QA checklist exists (in README or as separate file) and every item is actionable without interpretation
- [x] [verify=spec] A first-time user can understand install and workflow by reading only README.md and the template guidance
- [x] [verify=repo] Template section headings align with section names the skills actually read (no structural mismatch)
- [x] [verify=spec] Templates contain helpful `[TODO:]` guidance without walls of boilerplate text

## Verification plan
- AC-1: Compared template line counts and structure to F-001 originals; reduction confirmed, key sections preserved.
- AC-2: Inspected README.md for all six required sections; all present.
- AC-3: Executed QA checklist top-to-bottom; every item produced a pass/fail result without ambiguity.
- AC-4: Read README.md as a simulated first-time user; install and workflow were self-explanatory.
- AC-5: Compared template headings against skill SKILL.md file read steps; all headings matched.
- AC-6: Scanned all four templates for `[TODO:`; guidance present, no excessive boilerplate.

## Out of scope
- Changes to skill recovery or prompt behaviour (FEATURE-003)
- Automated test harness (FEATURE-005)
- Plugin packaging (FEATURE-010)

## Known risks
- Documentation must not trade completeness for brevity; QA checklist must remain valid as skills evolve
