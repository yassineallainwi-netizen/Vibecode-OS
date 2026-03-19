# VibeCode OS

A structured feature-by-feature workflow for solo vibe coders using Claude Code.

## What it does

Four project skills that give you memory, structure, and verification:

- **`/vibe-resume`** — Restore context at the start of a session. Reads your project files and tells you where you left off.
- **`/vibe-start`** — Spec a new feature. Claude asks questions, drafts a SPEC.md, and sets it as the active feature.
- **`/vibe-status`** — Check progress on the active feature. Shows what's done, what's missing, and what to do next.
- **`/vibe-done`** — Verify and close a feature. Walks through acceptance criteria, writes VERIFY.md, updates the session log.

## Who it's for

Solo developers using Claude Code who want structure without overhead. If you've ever lost track of what you were building, forgotten a decision, or shipped something untested — this is for you.

## What gets installed

```
your-project/
├── .claude/
│   ├── skills/
│   │   ├── vibe-start/SKILL.md
│   │   ├── vibe-resume/SKILL.md
│   │   ├── vibe-status/SKILL.md
│   │   └── vibe-done/SKILL.md
│   └── active_feature          # tracks the current feature ID
├── PROJECT_CONTEXT.md           # what this project is and how it works
├── AGENTS.md                    # working rules for Claude
├── DECISIONS.md                 # why things were built a certain way
├── SESSION_LOG.md               # what happened in each session
└── features/                    # one folder per feature (SPEC.md + VERIFY.md)
```

## Install

**Prerequisites:** Python 3.8+ and the [Claude Code CLI](https://claude.ai/claude-code).

```bash
# Navigate to YOUR project (not the VibeCode OS repo)
cd /path/to/your-project

# Run the installer, pointing to where you cloned VibeCode OS
python /path/to/VibeCodeOS/install.py
```

If you don't have VibeCode OS yet:
```bash
git clone https://github.com/yassineallainwi-netizen/Vibecode-OS.git
```

Running the installer again is safe — skills update if changed, your data files are never overwritten.

## Workflow

1. **`/vibe-resume`** — Start every session here. Get a summary of where things stand.
2. **`/vibe-start`** — Describe what you want to build. Claude drafts a spec, you confirm.
3. **Build it** — Write code normally. Claude has context from the spec.
4. **`/vibe-status`** — Check what's done and what's left.
5. **`/vibe-done`** — Walk through verification. Claude writes the record and closes the feature.

## Commands

| Command | What it does | When to use it |
|---------|-------------|----------------|
| `/vibe-resume` | Reads context files, summarizes project state | Start of every session |
| `/vibe-start` | Asks questions, drafts SPEC.md, sets active feature | When you want to build something new |
| `/vibe-status` | Reports progress against acceptance criteria | Mid-feature, to check where you are |
| `/vibe-done` | Verifies work, writes VERIFY.md, updates session log | When you think a feature is finished |

## QA Checklist

Use this to verify a fresh VibeCode OS installation works correctly:

- [ ] Run `python install.py` in a fresh repo — confirm `.claude/skills/` and all templates exist
- [ ] Run `python install.py` again — confirm no user data is overwritten (skills update if changed)
- [ ] Type `/` in Claude Code — confirm `/vibe-start`, `/vibe-resume`, `/vibe-status`, `/vibe-done` appear
- [ ] Confirm built-in commands (`/help`, `/clear`, etc.) still appear separately
- [ ] Run `/vibe-resume` on a blank install — confirm setup guidance appears (not hallucinated project details)
- [ ] Run `/vibe-start` with a vague request — confirm clarifying questions happen before SPEC.md is written
- [ ] Check `.claude/active_feature` — confirm it matches the created feature ID
- [ ] Run `/vibe-status` — confirm the 5-part structure (goal, completed, missing, risks, next step)
- [ ] Run `/vibe-done` with partial work — confirm VERIFY.md is created and feature stays active
- [ ] Run `/vibe-done` with complete work — confirm feature closes and `.claude/active_feature` is cleared
- [ ] Break `.claude/active_feature` (write a fake ID) — confirm recovery message appears
- [ ] Create multiple feature folders with no active feature — confirm Claude asks which one to resume

## Automated Smoke Tests

The smoke suite validates installer integrity and file layout — not interactive Claude skill behavior.

Runs automatically on push and pull requests via GitHub Actions.

**Prerequisites:** Python 3.8+. Claude CLI is optional.

```bash
# Run all scenarios
python tests/smoke/run_smoke_tests.py

# Run one scenario
python tests/smoke/run_smoke_tests.py --scenario template_markers

# Debug a failure
python tests/smoke/run_smoke_tests.py --keep-temp --verbose
```

Covers: installer first run, idempotency, managed skill updates, template marker integrity.

Interactive skill behavior still requires manual QA — see the checklist above.

## Limitations

- **Prompt-based skills:** Claude may occasionally deviate from instructions.
- **Project-local installation:** Skills are injected into your repo, not installed globally as a packaged Claude plugin.
- **Structural tests only:** Automated smoke tests cover the installer and file integrity. Interactive skill behavior still requires manual QA.
- **Single-developer focus:** Designed for solo builders, not multi-player team environments.
- **Log capping:** The active session log is capped at 10 entries. Older sessions roll over to SESSION_ARCHIVE.md.
