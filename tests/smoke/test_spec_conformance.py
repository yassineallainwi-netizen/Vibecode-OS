#!/usr/bin/env python3
"""
Spec conformance test — validates that feature SPEC.md files follow the
canonical template introduced in Decision 010.

Walks features/*/SPEC.md and checks:
  - Required frontmatter fields present (ID, Status, Complexity, Change kind)
  - Required sections present (Goal, Touches, Acceptance criteria, Verification plan)
  - Each acceptance criterion line has a [verify=...] tag
  - SPEC_v1.md files are skipped (historical preservation copies)

Usage:
    python tests/smoke/test_spec_conformance.py
    python tests/smoke/test_spec_conformance.py --strict   # fail on warnings
    python tests/smoke/test_spec_conformance.py --feature FEATURE-001-core-skills
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FEATURES_DIR = REPO_ROOT / "features"

# Required frontmatter fields (plain markdown list: "- key: value")
REQUIRED_FRONTMATTER = ["ID:", "Status:", "Complexity:", "Change kind:"]

# Required section headings (## Heading)
REQUIRED_SECTIONS = [
    "## Goal",
    "## Touches",
    "## Acceptance criteria",
    "## Verification plan",
]

# Valid verify tags
VALID_VERIFY_TAGS = {"cmd", "repo", "spec", "user"}

# Pattern matching an acceptance criterion line
# e.g.  - [ ] [verify=cmd] criterion text
#       - [x] [verify=repo] criterion text
CRITERION_PATTERN = re.compile(r"^\s*-\s+\[[ xX]\]\s+(.+)$")

# Pattern matching a [verify=...] tag
VERIFY_TAG_PATTERN = re.compile(r"\[verify=(\w+)\]")


def check_spec(spec_path: Path, strict: bool = False) -> tuple[bool, list[str], list[str]]:
    """
    Check a single SPEC.md file for conformance.
    Returns (passed, errors, warnings).
    """
    content = spec_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    errors = []
    warnings = []

    # 1. Required frontmatter fields
    for field in REQUIRED_FRONTMATTER:
        found = any(field in line for line in lines)
        if not found:
            errors.append(f"Missing frontmatter field: '{field}'")

    # 2. Required sections
    for section in REQUIRED_SECTIONS:
        # Match as a heading line (start of line, exact heading text)
        found = any(line.strip() == section for line in lines)
        if not found:
            errors.append(f"Missing required section: '{section}'")

    # 3. Acceptance criteria — each criterion line must have a [verify=...] tag
    in_ac_section = False
    ac_count = 0
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped == "## Acceptance criteria":
            in_ac_section = True
            continue
        # Stop checking when we hit the next section
        if in_ac_section and stripped.startswith("## "):
            in_ac_section = False
            break
        if in_ac_section:
            m = CRITERION_PATTERN.match(line)
            if m:
                ac_count += 1
                criterion_text = m.group(1)
                tag_match = VERIFY_TAG_PATTERN.search(criterion_text)
                if not tag_match:
                    errors.append(
                        f"Line {i}: criterion missing [verify=...] tag: {line.strip()!r}"
                    )
                else:
                    tag = tag_match.group(1)
                    if tag not in VALID_VERIFY_TAGS:
                        errors.append(
                            f"Line {i}: unknown verify tag '[verify={tag}]' — "
                            f"valid: {sorted(VALID_VERIFY_TAGS)}"
                        )

    # 4. Soft checks (warnings)
    if ac_count == 0:
        warnings.append("No acceptance criteria found — spec may be empty")

    # Check Status value
    status_line = next((l for l in lines if "Status:" in l), None)
    if status_line:
        valid_statuses = {"Draft", "Locked", "In progress", "Verified", "Closed"}
        found_status = None
        for s in valid_statuses:
            if s in status_line:
                found_status = s
                break
        if not found_status:
            warnings.append(f"Unrecognised Status value: {status_line.strip()!r}")

    # Check Complexity value
    complexity_line = next((l for l in lines if "Complexity:" in l), None)
    if complexity_line:
        valid_complexity = {"trivial", "normal", "complex", "high-risk"}
        found_complexity = any(v in complexity_line for v in valid_complexity)
        if not found_complexity:
            warnings.append(
                f"Unrecognised Complexity value: {complexity_line.strip()!r}"
            )

    # Check Change kind value
    ck_line = next((l for l in lines if "Change kind:" in l), None)
    if ck_line:
        valid_ck = {"behavioral", "instruction-only", "mixed"}
        found_ck = any(v in ck_line for v in valid_ck)
        if not found_ck:
            warnings.append(
                f"Unrecognised Change kind value: {ck_line.strip()!r}"
            )

    passed = len(errors) == 0
    if strict and warnings:
        errors.extend(warnings)
        warnings = []
        passed = False

    return passed, errors, warnings


def run(feature_filter: str = None, strict: bool = False) -> tuple[int, int, int]:
    """Run conformance checks. Returns (passed, failed, skipped)."""
    if not FEATURES_DIR.exists():
        print(f"[ERROR] features/ directory not found at {FEATURES_DIR}")
        return 0, 1, 0

    spec_files = sorted(FEATURES_DIR.glob("*/SPEC.md"))
    if feature_filter:
        spec_files = [s for s in spec_files if feature_filter in str(s)]

    if not spec_files:
        print("[WARN] No SPEC.md files found to check.")
        return 0, 0, 0

    passed = 0
    failed = 0

    print("VibeCode OS — Spec Conformance Check")
    print("=" * 42)

    for spec_path in spec_files:
        feature_name = spec_path.parent.name
        ok, errors, warnings = check_spec(spec_path, strict=strict)
        if ok and not warnings:
            print(f"[PASS] {feature_name}")
            passed += 1
        elif ok and warnings:
            print(f"[WARN] {feature_name}")
            for w in warnings:
                print(f"       WARN  {w}")
            passed += 1
        else:
            print(f"[FAIL] {feature_name}")
            for e in errors:
                print(f"       ERROR {e}")
            for w in warnings:
                print(f"       WARN  {w}")
            failed += 1

    total = passed + failed
    print()
    print(f"{total} specs checked: {passed} passed, {failed} failed")
    return passed, failed, 0


def main():
    parser = argparse.ArgumentParser(description="VibeCode OS spec conformance check")
    parser.add_argument(
        "--feature",
        help="Only check the named feature folder (partial match)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    args = parser.parse_args()
    _, failed, _ = run(feature_filter=args.feature, strict=args.strict)
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
