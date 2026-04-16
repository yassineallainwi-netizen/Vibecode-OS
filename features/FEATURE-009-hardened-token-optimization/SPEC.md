# Feature: Hardened Token Optimization Engine

- ID: FEATURE-009-token-optimization
- Status: Closed
- Date locked: 2026-03-20
- Complexity: complex
- Change kind: behavioral

## Goal
Extend effective session length under tight usage limits by compacting context into JSON artifacts, making `/vibe-resume` sharply delta-based, and adding a 24-hour dead-man's switch — without adding new commands or degrading output quality.

## Touches
- src/helpers/compaction.py
- src/helpers/context.py
- src/skills/vibe-resume/SKILL.md
- src/skills/vibe-done/SKILL.md
- src/skills/vibe-status/SKILL.md
- src/skills/vibe-start/SKILL.md
- install.py

## Acceptance criteria
- [x] [verify=cmd] `.claude/context/` directory created on first install
- [x] [verify=cmd] `.claude/runtime/` directory created on first install
- [x] [verify=cmd] Both directories preserved (not cleared) on second install
- [x] [verify=repo] `project_state.json` written by compaction.py has all required schema fields including schema_version and checksum
- [x] [verify=repo] `feature_FEATURE-NNN.json` has all required schema fields
- [x] [verify=spec] `/vibe-resume` prefers compact artifacts when fresh (reports "Context source: compact_ready")
- [x] [verify=spec] `/vibe-resume` falls back to full scan when artifacts missing or stale (reports "Context source: full_scan_required")
- [x] [verify=repo] Dead-man's switch triggers full reconstruction when artifact age exceeds 24 hours
- [x] [verify=spec] `/vibe-status` shows "Context pack" and token posture fields (compact_ready / mixed / full_scan_required)
- [x] [verify=spec] Complexity scoring added to `/vibe-start` — SPEC.md template includes Complexity field with four tiers
- [x] [verify=spec] `/vibe-done` triggers auto-compaction and writes feature state JSON after SESSION_LOG update
- [x] [verify=cmd] All existing smoke tests still pass (20/20)

## Verification plan
- AC-1: `python tests/smoke/run_smoke_tests.py --scenario context_directory_created` — exit 0.
- AC-2: `python tests/smoke/run_smoke_tests.py --scenario runtime_directory_created` — exit 0.
- AC-3: `python tests/smoke/run_smoke_tests.py --scenario context_directory_preserved` — exit 0.
- AC-4: `python tests/smoke/run_smoke_tests.py --scenario schema_version_present` — exit 0; schema_version=1 confirmed.
- AC-5: Read compaction.py write_feature_state(); all FEATURE_STATE_REQUIRED fields injected confirmed.
- AC-6: Read vibe-resume SKILL.md compact artifact check step; compact_ready path confirmed.
- AC-7: Read dead-man's switch rule in vibe-resume; artifact age > 24h → full_scan_required confirmed.
- AC-8: Read is_stale() in compaction.py; ISO-8601 UTC comparison with max_age_hours confirmed.
- AC-9: Read vibe-status SKILL.md; "Context pack" and token posture fields confirmed.
- AC-10: Read vibe-start SKILL.md; Complexity tier classification step confirmed.
- AC-11: Read vibe-done SKILL.md step 7.8; auto-compaction trigger after SESSION_LOG update confirmed.
- AC-12: `python tests/smoke/run_smoke_tests.py` — exit 0, 20/20 pass.

## Out of scope
- Replacing authoritative markdown files with compact artifacts (artifacts are acceleration layer only)
- Requiring Python subprocess calls for normal skill operation (Claude reads/writes JSON directly)
- Manual user-triggered compaction commands
- Using lean/normal/heavy terminology (compact_ready/mixed/full_scan_required used instead)

## Known risks
- JSON artifact written by Claude may have wrong field names; schema validation in compaction.py must catch on read
- Checksum mismatch must trigger reconstruction, not an error surfaced to the user
- Dead-man's switch timestamp comparison must work cross-platform with no timezone assumptions
