# Feature: Workflow Compression and Enforcement

## Goal
Make VibeCode OS lighter for solo developers while making completion harder to fake, without adding new commands or making the 4 core skills fragile.

## What it should do
- `/vibe-start`: trivial-feature fast path with negative filters and hard blocker rule
- `/vibe-done`: strict evidence classification, zero-diff short-circuit, force-close escape hatch, VERIFY.md overwrite, passive decision capture, compressed session log
- `/vibe-resume`: transparent blank-state detection, strict read-only enforcement
- `/vibe-status`: criteria visibility with default-to-unverified rule
- `DECISIONS.md` template: compressed with machine-detectable placeholders
- `SESSION_LOG.md` template: compressed to 3-bullet format

## What it should NOT do
- Add new commands (`/vibe-checkpoint`, `/vibe-decide`, `/vibe-revert`, `/vibe-reopen`)
- Break existing recovery behavior, install behavior, or smoke tests
- Over-compress templates to the point of losing `[TODO:]` markers

## Acceptance Criteria
- [ ] Trivial features can be started with little or no clarification
- [ ] `/vibe-start` still tracks trivial features correctly (SPEC.md + active_feature)
- [ ] No new required commands introduced
- [ ] `/vibe-resume` cannot mutate user context except clearing invalid active feature
- [ ] `/vibe-resume` explains blank-state detection transparently
- [ ] `/vibe-done` does not classify features as complete without meaningful evidence
- [ ] Unchecked major criteria trigger warnings during closeout
- [ ] Repeated `/vibe-done` runs keep one clean VERIFY.md (overwrite, not append)
- [ ] Zero-diff short-circuit stops early when no work was done
- [ ] Force-close escape hatch allows closure with dropped scope tracking
- [ ] `DECISIONS.md` populated naturally during real work without extra commands
- [ ] Trivial work does not generate decision spam
- [ ] `SESSION_LOG.md` entries stay short (max 3 bullets, 15 words each)
- [ ] `/vibe-status` shows remaining criteria with unverified state
- [ ] All four vibe-* commands remain coherent and predictable
- [ ] Structural smoke tests still pass
- [ ] Parse compatibility: trivial specs use same headings as normal specs

## Risks and edge cases
- Parse drift between trivial and normal specs could break status/done parsing
- Template compression must preserve `[TODO:]` markers for smoke tests
- Force-close must not silently count as normal "Complete"
