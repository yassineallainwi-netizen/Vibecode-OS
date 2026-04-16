# CLAUDE.md — Development Optimization & Lessons Learned

A living document tracking how VibeCode OS can be built more efficiently. Updated whenever a pattern repeats or a bottleneck is identified.

**Last Updated:** 2026-03-28
**Current Version:** v2.0.1 complete; v2.1+ optimizations in this doc

---

## 🎯 Core Principle

**Build less earlier, test sooner, refactor ruthlessly when patterns repeat.** Avoid speculative features. Token efficiency compounds — small wins on each feature multiply across 10+ iterations.

---

## What We Did Wrong (v1.0.0 → v2.0.1)

### 1. **Feature Creep via Sequential Stacking** ⚠️

**What happened:**
- FEATURE-007 (War Room discipline)
- FEATURE-008 (Verification grounding)
- FEATURE-009 (Token optimization)
- FEATURE-010 (Plugin delivery)

Each feature was full-scope before moving to the next. Total: ~4 weeks of AI time, 5000+ tokens per feature on average.

**Why it cost tokens:**
- No shared infrastructure planned upfront → each feature reinvented context bridges
- Git Ghost, CLAUDE.md sync, War Room manifest → needed across 3+ features but designed independently
- Verification workflow → baked into FEATURE-008 but should have been atomic in FEATURE-006
- Plugin format → came late (FEATURE-010), forcing adapter layer when it could have been parallel

**Optimization for v2.1+:**

```
BEFORE: Big feature → Test → Doc → Next feature
AFTER:  Atomic kernel → Parallel experiments → Merge winners → Ship
```

- **Plan feature dependencies upfront.** Before starting FEATURE-N, identify what FEATURE-N+1 will need.
- **Extract shared infrastructure to earliest possible feature.** (e.g., VERIFY.md should be v1.0.0 not FEATURE-008)
- **Use feature flags for experiments, not sequential features.** Run FEATURE-007 and FEATURE-010 in parallel via `.claude/feature_flags.json`.

---

### 2. **Plugin Format Discovery Was Too Late** ⚠️

**What happened:**
- Designed skill-pack format (FEATURE-001 through FEATURE-006)
- Discovered official Claude Code plugin spec midway through FEATURE-007
- Had to retrofit adapter layer in FEATURE-010

**Why it cost tokens:**
- 3 weeks of skill development before learning about `.claude-plugin/` standard
- Adapter logic (`src/adapter/`) added 400 lines of reconciliation code
- Install.py had to support dual-mode (skill-pack + plugin)
- Plugin migration docs had to explain two separate paths to users

**How to prevent:**

✅ **Do this first in any new tool/framework integration:**
1. **Spend 30 mins reading official spec** before designing anything
2. **Build a minimal proof-of-concept** against the official spec
3. **Only then** design abstractions on top

For Claude Code specifically:
- Check https://documentation.claude.ai/claude-code/plugins for latest plugin spec
- Build against `.claude-plugin/plugin.json` schema first
- Wrap skill-pack approach around it if needed

---

### 3. **Testing & Verification Came Late** ⚠️

**What happened:**
- FEATURE-001 through FEATURE-004: no test infrastructure
- FEATURE-005: Smoke tests added (but only ~24 surface-level tests)
- FEATURE-006: VERIFY.md introduced (but weak verification, no evidence grading)
- FEATURE-008: Evidence-graded verification finally added

**Why it cost tokens:**
- Shipped untested features, then reworked them (e.g., AGENTS.md heuristics in FEATURE-007)
- VERIFY.md format changed 3 times across features
- Command approval flow redesigned in FEATURE-008 after already doing basic validation in FEATURE-006
- Regression testing was manual until smoke tests existed

**How to build better for v2.1+:**

✅ **Verification should be atomic, not iterative:**
1. **FEATURE-001:** Include a basic VERIFY.md template with 3-5 acceptance criteria
2. **FEATURE-005:** Smoke tests should run acceptance criteria, not separate test suite
3. **FEATURE-008:** Evidence grading is a refinement, not a rework

Template structure (steal this):
```yaml
# FEATURE-XXX/VERIFY.md
## Acceptance Criteria
- [ ] Criterion A (command_verified: pytest runs, 5+ passing)
- [ ] Criterion B (repo_observed: file X exists with marker Y)
- [ ] Criterion C (user_reported: "looks right")
```

---

### 4. **Documentation Was Reactive, Not Proactive** ⚠️

**What happened:**
- Built features, then wrote docs (plugin_migration.md came after FEATURE-010)
- SESSION_LOG, DECISIONS, AGENTS — templates written after usage patterns emerged
- README incomplete until late in development

**Why it cost tokens:**
- Docs forced by user confusion instead of preventing it
- Had to backfill use-case examples into completed specs
- Plugin migration guide had to reverse-engineer feature timeline

**How to fix:**

✅ **Docs-first lightweight checklist for each feature:**

Before writing a single line of code:
1. **Write a one-liner** (2-3 sentences) of what this feature does
2. **Write the template** it will generate or modify
3. **Write 2-3 examples** of output from that template
4. **THEN** implement

Example (FEATURE-008 should have had):
```markdown
## What this does
Grounds feature completion in evidence. Each criterion gets tagged with verification method.

## Template (VERIFY.md excerpt)
- [ ] All tests pass (evidence: command_verified)

## Example output
FEATURE-007/VERIFY.md:
✓ War Room manifest synced (repo_observed: .claude/runtime/war_room.json exists)
✓ Session picked up correctly (command_verified: /vibe-resume ran without errors)
```

This prevents scope creep and forces clarity before implementation.

---

### 5. **Underestimated Token Cost of Iteration** ⚠️

**What happened:**
- FEATURE-009 was literally called "Hardened Token Optimization"
- This means features 1–8 were NOT optimized
- Compact artifacts, context source tracking, dead-man's switch → all retrofitted in FEATURE-009

**Why it cost tokens:**
- Each feature generated full feature context when resuming sessions
- AGENTS.md, DECISIONS.md, SESSION_LOG.md → all read fresh on every call
- Approval workflow logged everything verbosely
- Git history skimmed unnecessarily (full git log reads)

**Token-aware patterns for v2.1+:**

✅ **Compact-first design:**

```python
# WRONG: Read full SESSION_LOG.md every time
with open('SESSION_LOG.md') as f:
    full_log = f.read()

# RIGHT: Cache last 2 entries in JSON
with open('.claude/context/session.json') as f:
    compact = json.load(f)  # { 'last_feature_id': 'FEATURE-007', 'status': 'complete' }
```

✅ **Query-specific file reads:**
```
/vibe-resume: Read .claude/context/war_room.json (~200 bytes), not all of AGENTS.md
/vibe-start: Read .claude/active_feature only, not PROJECT_CONTEXT.md
/vibe-status: Read FEATURE-NNN/SPEC.md + FEATURE-NNN/VERIFY.md only (not SESSION_LOG)
```

✅ **Lazy-load with inference:**
```python
# Instead of: Read AGENTS.md and check every field
# Do this: Infer AGENTS fields from repo signals (python? → Python section)
```

---

### 6. **Over-engineering for Edge Cases Early** ⚠️

**What happened:**
- FEATURE-007 SPEC had 18 "Risks and edge cases"
- Some never manifested in testing
- Code to handle them added complexity and token cost

Examples:
- "Repo maturity must fail gracefully when git is unavailable" — git is always available in Claude Code context
- "CLAUDE.md may not exist" — we always create it on first run, so the defensive code wasn't needed
- "ANSI stripping" in verification — only needed because output was verbose; compact output doesn't have ANSI

**How to avoid:**

✅ **Only build edge case handling after the edge case happens in practice.**

For v2.1+:
- **Minimum viable risk handling:** Code for the happy path only
- **When a bug surfaces:** Add handling and mark it "Evidence: production_incident_YYYY-MM-DD"
- **After 3 features without incident:** Consider removing the edge case code

---

## Second Wave Findings (2026-03-28)

*Added from fresh git-history + architecture analysis. These gaps were not covered in the v1 retrospective above.*

---

### 7. **Feature Split Mid-Development Wastes the Most Tokens** ⚠️

**What happened:**
- FEATURE-002 was scoped too broadly
- One commit (dc0065b) split it mid-work into 3 separate features
- Forced re-planning, re-reading already-loaded files, and rewriting acceptance criteria

**Why it cost tokens:**
- Splitting mid-implementation = starting over with a warm context that has to be reloaded
- Every re-scoping adds a full round of: read current state → understand what's done → plan remaining → execute

**Rule:**
> If a feature requires changes to >4 files OR touches >2 subsystems, split it **before writing a single line of code.** Splitting during planning costs ~10% of the overhead of splitting mid-implementation.

---

### 8. **File Discovery Mechanism Took 3 Iterations** ⚠️

**What happened:**
- Feature discovery logic (how skills find FEATURE-NNN dirs) was never explicitly designed — it emerged from usage
- Wrong approach 1: Used `.claude/active_feature` as primary truth
- Fix 1 (bcfe67a): Switched to `features/` directory scan as ground truth
- Fix 2 (da4f7bc): Switched from directory Glob to SPEC.md Glob
- Same mechanism reworked twice

**Rule:**
> For any "find X in the repo" logic, write the discovery rule in the SPEC before coding it. Include:
> - Source of truth (which file/dir is canonical)
> - Fallback behavior (what if source is missing)
> - Tie-breaking rule (what if multiple matches)
>
> Test against 3 states: empty, one item, multiple items. Do this before implementation, not after the first bug.

---

### 9. **Dual Context Layers Create Sync Debt** ⚠️

**What happened:**
- FEATURE-009 added JSON compact artifacts (`.claude/context/`) on top of existing plain markdown files
- Two representations of the same state now exist in parallel
- This required: `compaction.py` (283 lines), dead-man's switch (24h staleness), checksum invalidation, parity tests

**Why it cost tokens:**
- Every state change must now be written to two places
- Bugs where one layer is stale require debugging two systems
- Parity validation logic exists purely to detect drift between layers — that's accidental complexity

**Rule:**
> Pick ONE canonical state format per domain. If markdown files are user-facing truth, don't add a JSON shadow. If JSON is a performance cache, mark it generated-only (`# THIS FILE IS A CACHE — edit SOURCE_FILE.md`) and never treat it as authoritative. Two canons = double the bugs.

---

### 10. **Code Duplication Across Deployment Modes** ⚠️

**What happened:**
- FEATURE-010 created `.claude-plugin/skills/` as a copy of `src/skills/`
- Same skill files exist in 2 places
- Required: 9 parity tests (test_plugin_parity.py) just to catch sync failures, install.py must update both, any skill change requires 2 edits

**Why it cost tokens:**
- 9 tests exist purely to detect drift between two copies — not to test behavior
- Plugin parity test failures are false alarms if someone edits `src/skills/` and forgets `.claude-plugin/skills/`

**Rule:**
> One source of truth. If a format requires a physical copy, automate the copy in install.py and add a generated-file header. Never maintain two canonical copies manually. Parity tests that only check "are these two copies the same?" are a design smell, not real test coverage.

---

### 11. **Recovery Logic Scattered Across 3 Features** ⚠️

**What happened:**
- FEATURE-003: Basic recovery (missing files, broken active_feature, empty templates)
- FEATURE-007: Advanced recovery (AGENTS.md detection, CLAUDE.md sync, repo maturity inference)
- FEATURE-009: Auto mini-resume (stale context, external active_feature change, SESSION_LOG mismatch)
- No single place owns "what to do when state is broken"

**Why it cost tokens:**
- Each recovery feature had to re-read existing recovery logic to avoid conflicts
- Edge cases in FEATURE-007 recovery conflicted with FEATURE-003 rules (fixed in v2.0.1)
- Developer touching one recovery case can't find the others without grepping 3 skill files

**Rule:**
> On first contact with any recovery case, create a dedicated recovery section or file. All future recovery additions extend that one place. If you catch yourself writing "if X is missing, do Y" in two different features, consolidate immediately.

---

### 12. **Advisory-Only Features Add Clutter Without Value** ⚠️

**What happened:**
- Git Ghost (FEATURE-007) generates copy-pasteable git commit messages
- Never executes git — purely advisory
- For non-technical users (the target audience), the suggestion is unactionable without confidence it's correct

**Why it cost tokens:**
- Feature design, implementation, and output formatting all spent on a suggestion the user can't validate
- Output clutter: non-technical users see commit message suggestions without knowing if they're correct

**Rule:**
> If a feature is purely advisory (never executes, never validates its own output), ask: does the target user benefit from seeing this? If the answer requires explanation, cut the feature. An unactionable suggestion from a tool is noise, not help.

---

### 13. **Meta: How We Used Claude Code Itself** ⚠️

**What happened in the 2026-03-28 retrospective session:**
- Launched 2 parallel Explore agents to analyze the codebase
- Both agents covered overlapping ground (feature list appeared in both outputs)
- Read full CLAUDE.md (390 lines) before confirming it existed
- Ran `git log --stat` (verbose) when `--oneline` would have been sufficient to triage

**Why it cost tokens:**
- Two agents with overlapping scopes = duplicate context reads billed twice
- `git log --stat` on 16 commits = 16x more output than needed to find the 3 interesting commits
- Pre-emptive full-file reads before existence check = wasted if file was empty or missing

**Rules for using Claude Code itself efficiently:**
1. **Before launching Explore agents:** Glob-check target files first (1 tool call) to scope the agents. Never assign overlapping file domains to parallel agents.
2. **For git history:** Start with `--oneline`, identify large insertions/deletions, then `git show <sha>` only those commits.
3. **Before reading a large file:** Confirm it exists and check its size (first 10 lines or line count) before reading all 390 lines.
4. **Parallel agents = parallel scopes:** Divide by subsystem (`src/`, `tests/`, `.claude/`), not by task type ("architecture" vs "history") — task type creates overlap, subsystem division doesn't.

---

## ✅ What We Did Right (Keep Doing)

### 1. **Atomic Skills (Never Changed Core Flow)**
- `/vibe-start`, `/vibe-resume`, `/vibe-status`, `/vibe-done` — these stayed stable
- New logic added inside skills, not new skills
- **Why:** Token cost of teaching Claude a new command > cost of expanding an existing one

### 2. **SPEC.md Before Implementation**
- Every feature had a written SPEC with acceptance criteria before code
- Prevented scope creep mid-feature
- **Why:** Saves rework; clear acceptance criteria = faster feature done

### 3. **Git Commits After Features Complete**
- Never mid-feature commits
- One commit per feature (or feature group)
- **Why:** Cleaner history; easier to revert; smaller context in git log reads

### 4. **File-Grounded Heuristics (Not Hallucination)**
- War Room manifest reads actual repo files
- AGENTS.md state inferred from byte size + markers (not naive `[TODO:]` search)
- **Why:** Reliable across repos; lower token cost than NLP/fuzzy matching

---

## 📋 Optimization Checklist for Future Features

Use this before starting FEATURE-N:

### Planning (5 mins)
- [ ] **Atomic?** Does this feature stand alone, or does FEATURE-N+1 need its outputs?
  - If interdependent → plan both features together, possibly parallel
- [ ] **Official spec exists?** (e.g., plugin standard, Python PEP, package.json schema)
  - If yes → build proof-of-concept against spec first (30 mins max)
- [ ] **Testable in isolation?** Can acceptance criteria be verified without FEATURE-N+1?
  - If no → extract testable kernel, defer nice-to-haves
- [ ] **Token budget?** Estimate context reads + output + iteration (aim for <2000 tokens for core logic)
  - If over → descope or defer
- [ ] **Docs needed?** Template format, example output, one-liner
  - Write these BEFORE implementation

### Implementation (during work)
- [ ] **Compact-first:** Cache in JSON before reading markdown
- [ ] **Query-specific reads:** Load only what this command needs (not all context files)
- [ ] **No speculative edge cases:** Code the happy path, add defensive code after actual incidents
- [ ] **VERIFY.md written alongside feature:** Evidence labels on every criterion

### Shipping (before closing feature)
- [ ] **Smoke tests pass** (command_verified evidence)
- [ ] **Production scenario tested** (not just happy path)
- [ ] **Plugin/dual-mode tested** (install.py --plugin succeeds)
- [ ] **Migration path documented** (if changing file format or command structure)

---

## 🔄 Pattern Library (Reuse These)

### Pattern: Safe File Reads (Token-Efficient)
```python
# Read with timeout, default fallback
def read_safe(path, default=""):
    try:
        with open(path, 'r') as f:
            return f.read(2000)  # Cap at 2000 bytes, not unlimited
    except:
        return default
```

### Pattern: Compact Artifact Caching
```python
# Instead of full AGENTS.md → synthesize .claude/context/config.json
{
  "version": "2.0.1",
  "last_feature": "FEATURE-010",
  "status": "complete",
  "risk_flags": ["plugin_mode_untested"],
  "next_action": "run smoke tests"
}
```

### Pattern: Evidence-Graded Verification
```yaml
# Every VERIFY.md should follow this
- [ ] Acceptance Criterion (evidence: command_verified)
  - Command: pytest tests/smoke/
  - Result: 24/24 passing
  - Timestamp: 2026-03-20T14:32Z
```

### Pattern: Atomic SPEC Writing
```markdown
## What it should do
- [ ] One concrete sentence per bullet
- [ ] No "maybe" or "could" — binary outcomes only

## Acceptance Criteria
- At least 5, at most 9
- Each has evidence method attached
- Testable without FEATURE-N+1
```

---

## 📊 Metrics to Track

For each new feature, log these numbers:

```
FEATURE-XXX Development Log
├── Planning time: X minutes
├── Implementation time: Y minutes (AI + human combined)
├── Token cost
│   ├── Context reads: N bytes
│   ├── Code written: M lines
│   ├── Estimated AI tokens: ~X (at ~1.3 tokens/word)
│   └── Rework iterations: Z (if Z > 2, investigate why)
├── Test coverage: A/B acceptance criteria verified
├── File output
│   ├── SPEC.md lines
│   ├── VERIFY.md lines
│   ├── Code changes (git diff --stat)
│   └── Templates added/modified
└── Issues found in production: N (track for FEATURE-N+2 edge case prevention)
```

Example (FEATURE-010):
```
Planning: 10 mins
Implementation: 180 mins total
Token cost:
  Context reads: ~8000 bytes (plugin.json ref, dual-mode logic, adapter code review)
  Code written: ~350 lines (plugin.json, adapter/, plugin migration docs)
  Estimated AI: ~2800 tokens
  Rework: 2 (adapter layer scope; install.py rollback flag)
Test: 9/9 parity tests, 24/24 smoke tests pass
File output: FEATURE-010/SPEC.md (180 lines), VERIFY.md (120 lines), docs/plugin_migration.md (140 lines)
Production issues: 0
```

This data helps you spot patterns:
- If rework > 2, your spec wasn't clear enough
- If token cost > 3000, feature is too big (split it)
- If production issues > 0, edge case checklist needs updating

---

## Next Steps for v2.1+

### Quick Wins (1–2 sessions each)
- [ ] Descope FEATURE-007 edge cases (don't rebuild on rare incidents)
- [ ] Replace full AGENTS.md reads with .claude/context/agents.json lookup
- [ ] Parallel test: Run /vibe-start and /vibe-done 10x, log token usage
- [ ] Compress SESSION_LOG to 3-entry JSON cache

### Medium-term (3–5 sessions)
- [ ] Feature flags infrastructure (allow A/B testing features without sequential stacking)
- [ ] Plugin format as primary (skill-pack becomes compatibility layer, not default)
- [ ] Verification dashboard (VERIFY.md aggregator showing cross-feature test health)

### Research (ongoing)
- [ ] Benchmark token cost per feature across v2.0.1 releases (track regression)
- [ ] Document token payoff of each optimization (which saves the most?)
- [ ] Experiment with streaming context reads (send only changed lines to Claude)

---

## How to Use This Document

1. **Before starting FEATURE-N:** Review "Optimization Checklist" section
2. **During development:** Reference "Pattern Library" for standard approaches
3. **After shipping:** Log metrics in "Metrics to Track" section
4. **Every 3 features:** Review what patterns repeated, update this doc with new insights
5. **When blocked:** Check "What We Did Wrong" — likely a documented pitfall

---

**Version History:**
- v1: Initial creation from VibeCode OS v2.0.1 retrospective (2026-03-28)
- v1.1: Add metrics tracking section (pending next feature)
- v1.2: Second wave findings added from git-history + architecture analysis (2026-03-28) — gaps 7-13
- v2: Parallel feature development guidelines (planned for FEATURE-011)
