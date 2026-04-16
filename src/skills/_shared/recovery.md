# VibeCode OS — Canonical Recovery Messages

Reference this file from any skill instead of duplicating recovery wording.
Single source of truth — edit here, propagate to all skills.

---

## R1: Broken feature reference

Trigger: `.claude/active_feature` exists but the referenced feature folder does not.

```
⚠️ VibeCode Recovery: Active feature reference is broken — `FEATURE-NNN-slug` doesn't exist.
Clear `.claude/active_feature`, then reply **restart** to scan for open features, or `/vibe-start` to begin a new one.
```

Action: Clear `.claude/active_feature`. Do not delete any feature folders.

---

## R2: Malformed feature (no SPEC.md)

Trigger: Feature folder exists but contains no SPEC.md.

```
⚠️ VibeCode Recovery: Feature `FEATURE-NNN-slug` is malformed — no SPEC.md found.
Cannot verify or report status without acceptance criteria.
Reply **Delete and reset** to clear `.claude/active_feature` (no files deleted), or write a SPEC.md manually and re-run.
```

Action: Wait for user reply. Do not proceed with verification.

---

## R3: Conflicting active feature

Trigger: `.claude/active_feature` points to an open feature, but user requests to start or close a different one.

```
⚠️ VibeCode Recovery: You have an active feature: `FEATURE-NNN-slug`.
Close it first with `/vibe-done`, or reply **override** to ignore it and proceed.
```

Action: Wait for reply. On **override**: clear `.claude/active_feature` and proceed. Record the override in SESSION_LOG.md.

---

## Usage in skills

Reference these by ID (R1, R2, R3). In each skill, link to this file in the YAML frontmatter:

```yaml
shared_references:
  - _shared/recovery.md
  - _shared/evidence.md
```

Then in the skill body, reference by ID:
```
→ See _shared/recovery.md R1
```
