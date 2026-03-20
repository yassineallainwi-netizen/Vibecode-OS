# Feature: Hardened Token Optimization Engine

## Goal
Extend session length under tight usage limits by reducing repeated context load, compressing routine evidence before reasoning, and making resume state sharply delta-based without degrading quality or adding new bureaucracy.

## What it should do
- Create compact JSON artifacts (.claude/context/project_state.json and feature_FEATURE-NNN.json) automatically after /vibe-done
- Make /vibe-resume delta-based: prefer compact artifacts over full file scan when fresh
- Dead-man's switch: if artifacts are older than 24h or invalid, fall back to full reconstruction
- Skills manage JSON directly using Write/Edit tools (no separate Python subprocess required for runtime)
- Deterministic helper scripts handle JSON schema validation, atomic writes, delta computation, stack deduplication
- /vibe-resume emits dense War Room delta (What changed / What's open / Last hard problem / Current blocker / Next file / Next action / Verification posture / Active risks / Context source)
- Auto mini-resume on lost-state: stale context, active_feature changed externally, SESSION_LOG mismatch
- Verification/log triage before reasoning: compress to structured summary (from 008's triage_log)
- Digest-based reuse: same output SHA-256 + same file digests + same command → skip re-analysis, label as reused
- Complexity scoring stored in SPEC.md and feature JSON: trivial/normal/complex/high-risk
- /vibe-status: compact token-efficiency fields (Context pack, Verification summary, token posture as compact_ready/mixed/full_scan_required)

## What it should NOT do
- Replace authoritative markdown files — compact artifacts are an acceleration layer only
- Require Python helpers to be called as subprocesses for normal skill operation (Claude reads/writes JSON directly)
- Ask users to manage or trigger compaction manually — it's automatic after /vibe-done
- Use lean/normal/heavy for token posture — use compact_ready/mixed/full_scan_required

## Acceptance Criteria
- [ ] .claude/context/ directory created on install
- [ ] .claude/runtime/ directory created on install
- [ ] Both directories preserved on second install
- [ ] project_state.json has all required schema fields including schema_version and checksum
- [ ] feature_FEATURE-NNN.json has all required schema fields
- [ ] /vibe-resume prefers compact artifacts when fresh (Context source: compact_ready)
- [ ] /vibe-resume falls back to full scan when artifacts missing/stale (Context source: full_scan_required)
- [ ] Dead-man's switch triggers on stale artifacts (>24h)
- [ ] /vibe-status shows Context pack and token posture fields
- [ ] Complexity scoring added to /vibe-start SPEC.md output
- [ ] Digest-based reuse documented in /vibe-done instructions
- [ ] All existing smoke tests still pass

## Risks and edge cases
- JSON artifact may be written by Claude with wrong field names — schema validation in compaction.py catches this
- Checksum mismatch must trigger reconstruction, not error
- Dead-man's switch timestamp comparison must work cross-platform (no TZ assumptions)
- Context source: mixed state must be clearly explained to the user
