#!/usr/bin/env python3
"""
VibeCode OS structural smoke tests.

Validates installer behavior, file integrity, idempotency, and template
markers. Does NOT test interactive Claude skill behavior.

Usage:
    python tests/smoke/run_smoke_tests.py
    python tests/smoke/run_smoke_tests.py --scenario template_markers
    python tests/smoke/run_smoke_tests.py --keep-temp --verbose
"""

import argparse
import os
import subprocess
import sys
import traceback
from pathlib import Path

# Ensure helpers can be imported from same directory
sys.path.insert(0, str(Path(__file__).parent))
from helpers import (  # noqa: E402
    assert_created_report,
    assert_dir_empty,
    assert_dir_exists,
    assert_exists,
    assert_file_empty,
    assert_file_equals,
    assert_file_unchanged,
    assert_preserved_report,
    assert_returncode,
    assert_unchanged_report,
    assert_updated_report,
    cleanup_temp_repo,
    create_temp_repo,
    normalize,
    read_file,
    run_command,
    run_installer,
    write_file,
)

# Auto-detect repo root (tests/smoke/run_smoke_tests.py -> ../../)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------- Config ----------


class Config:
    def __init__(self, install_script, src_dir, keep_temp, verbose, strict_cli):
        self.install_script = Path(install_script)
        self.src_dir = Path(src_dir)
        self.keep_temp = keep_temp
        self.verbose = verbose
        self.strict_cli = strict_cli


# ---------- Scenario helpers ----------


def _do_first_install(config):
    """Run a first install in a fresh temp repo. Returns (tmp_path, result)."""
    tmp = create_temp_repo()
    result = run_installer(config.install_script, tmp)
    assert_returncode(result)
    return tmp, result


SKILL_NAMES = ["vibe-start", "vibe-resume", "vibe-status", "vibe-done"]
USER_DATA_FILES = [
    "PROJECT_CONTEXT.md",
    "AGENTS.md",
    "DECISIONS.md",
    "SESSION_LOG.md",
]


# ---------- Scenarios ----------


def installer_first_run(config):
    """Verify first install creates the expected repo structure."""
    tmp, result = _do_first_install(config)
    output = normalize(result.stdout)

    try:
        # 4 skill files exist
        for name in SKILL_NAMES:
            skill_path = tmp / ".claude" / "skills" / name / "SKILL.md"
            assert_exists(skill_path)
            assert_created_report(output, f".claude/skills/{name}/SKILL.md")

        # 4 user data template files exist
        for filename in USER_DATA_FILES:
            assert_exists(tmp / filename)
            assert_created_report(output, filename)

        # features/ exists and is empty
        assert_dir_empty(tmp / "features")

        # .claude/active_feature exists and is empty
        assert_exists(tmp / ".claude" / "active_feature")
        assert_file_empty(tmp / ".claude" / "active_feature")

        # Installed skills match source
        for name in SKILL_NAMES:
            installed = tmp / ".claude" / "skills" / name / "SKILL.md"
            source = config.src_dir / "skills" / name / "SKILL.md"
            assert_file_equals(installed, source)

        return True, "All 10 paths created, skills match source"
    finally:
        if not config.keep_temp:
            cleanup_temp_repo(tmp)


def installer_second_run(config):
    """Verify second install preserves user data and doesn't rewrite skills."""
    tmp, _ = _do_first_install(config)

    try:
        # Modify PROJECT_CONTEXT.md with full user content (replaces template)
        pc_path = tmp / "PROJECT_CONTEXT.md"
        write_file(pc_path, "# My Real Project\nThis is actual user content, not a template.\n")

        # Partially edit AGENTS.md (append to existing template content)
        agents_path = tmp / "AGENTS.md"
        original_agents = read_file(agents_path)
        write_file(agents_path, original_agents + "\n## My Custom Rule\nNever touch the billing code.\n")

        # Snapshot all user data files before second run
        snapshots = {}
        for filename in USER_DATA_FILES:
            snapshots[filename] = read_file(tmp / filename)
        snapshots[".claude/active_feature"] = read_file(tmp / ".claude" / "active_feature")

        # Run installer again
        result = run_installer(config.install_script, tmp)
        assert_returncode(result)
        output = normalize(result.stdout)

        # All user data files must be unchanged
        for filename, before in snapshots.items():
            assert_file_unchanged(tmp / filename, before)

        # Output must show Preserved for user data
        for filename in USER_DATA_FILES:
            assert_preserved_report(output, filename)

        # Output must show Unchanged for skills (source hasn't changed)
        for name in SKILL_NAMES:
            assert_unchanged_report(output, f".claude/skills/{name}/SKILL.md")

        return True, "User data preserved (including partial edit), skills unchanged"
    finally:
        if not config.keep_temp:
            cleanup_temp_repo(tmp)


def managed_skill_updates(config):
    """Verify managed skills update when content differs from source."""
    tmp, _ = _do_first_install(config)

    try:
        # Modify one installed skill
        modified_skill = tmp / ".claude" / "skills" / "vibe-start" / "SKILL.md"
        write_file(modified_skill, "MODIFIED CONTENT\n")

        # Snapshot user data
        snapshots = {}
        for filename in USER_DATA_FILES:
            snapshots[filename] = read_file(tmp / filename)

        # Run installer again
        result = run_installer(config.install_script, tmp)
        assert_returncode(result)
        output = normalize(result.stdout)

        # vibe-start must be Updated
        assert_updated_report(output, ".claude/skills/vibe-start/SKILL.md")

        # Other skills must be Unchanged
        for name in SKILL_NAMES:
            if name != "vibe-start":
                assert_unchanged_report(output, f".claude/skills/{name}/SKILL.md")

        # Updated skill must now match source
        source = config.src_dir / "skills" / "vibe-start" / "SKILL.md"
        assert_file_equals(modified_skill, source)

        # User data must still be preserved
        for filename, before in snapshots.items():
            assert_file_unchanged(tmp / filename, before)

        return True, "Modified skill updated, others unchanged, user data preserved"
    finally:
        if not config.keep_temp:
            cleanup_temp_repo(tmp)


def template_markers(config):
    """Verify source templates contain required [TODO: markers."""
    templates_dir = config.src_dir / "templates"
    warnings = []

    for filename in USER_DATA_FILES:
        path = templates_dir / filename
        assert_exists(path)
        content = read_file(path)

        # Hard requirement: non-empty
        if not content.strip():
            raise AssertionError(f"Template is empty: {path}")

        # Hard requirement: contains [TODO: marker
        if "[TODO:" not in content:
            raise AssertionError(f"Template missing [TODO: marker: {path}")

        # Soft check: line count warning (not a failure)
        line_count = len(content.splitlines())
        if line_count > 30:
            warnings.append(f"{filename}: {line_count} lines (consider trimming)")

    msg = "All templates contain [TODO: markers"
    if warnings:
        msg += " | Warnings: " + "; ".join(warnings)
    return True, msg


def claude_probe(config):
    """Optional: check if Claude CLI is available."""
    try:
        result = run_command(["claude", "--version"], timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip().split("\n")[0]
            return True, f"Claude CLI found: {version}"
        else:
            if config.strict_cli:
                raise AssertionError(
                    f"Claude CLI returned exit code {result.returncode}"
                )
            return None, "Claude CLI returned non-zero (use --strict-cli to require)"
    except FileNotFoundError:
        if config.strict_cli:
            raise AssertionError("Claude CLI not found on PATH")
        return None, "Claude CLI not found (use --strict-cli to require)"
    except Exception as e:
        if config.strict_cli:
            raise AssertionError(f"Claude CLI probe failed: {e}")
        return None, f"Claude CLI probe failed: {e}"


# ---------- Scenario registry ----------
# (function, required)

SCENARIOS = {
    "installer_first_run": (installer_first_run, True),
    "installer_second_run": (installer_second_run, True),
    "managed_skill_updates": (managed_skill_updates, True),
    "template_markers": (template_markers, True),
    "claude_probe": (claude_probe, False),
}


# ---------- Runner ----------


def run_scenarios(config, scenario_filter=None):
    """Run scenarios and return (passed, failed, skipped) counts."""
    passed = 0
    failed = 0
    skipped = 0
    any_required_failed = False

    scenarios = SCENARIOS
    if scenario_filter:
        if scenario_filter not in scenarios:
            print(f"Unknown scenario: {scenario_filter}")
            print(f"Available: {', '.join(scenarios.keys())}")
            return 0, 1, 0
        scenarios = {scenario_filter: scenarios[scenario_filter]}

    print("VibeCode OS Smoke Tests")
    print("=" * 40)

    for name, (fn, required) in scenarios.items():
        try:
            result, message = fn(config)
            if result is None:
                # Skipped
                skipped += 1
                print(f"[SKIP] {name} — {message}")
            elif result:
                passed += 1
                if config.verbose:
                    print(f"[PASS] {name} — {message}")
                else:
                    print(f"[PASS] {name}")
            else:
                failed += 1
                if required:
                    any_required_failed = True
                print(f"[FAIL] {name} — {message}")
        except AssertionError as e:
            failed += 1
            if required:
                any_required_failed = True
            print(f"[FAIL] {name}")
            for line in str(e).splitlines():
                print(f"       {line}")
        except subprocess.TimeoutExpired as e:
            failed += 1
            if required:
                any_required_failed = True
            print(f"[FAIL] {name}")
            print(f"       Timed out after {e.timeout}s")
        except Exception:
            failed += 1
            if required:
                any_required_failed = True
            print(f"[FAIL] {name}")
            if config.verbose:
                for line in traceback.format_exc().splitlines():
                    print(f"       {line}")
            else:
                print(f"       Unexpected error (use --verbose for traceback)")

    total = passed + failed + skipped
    print()
    print(f"{total} scenarios: {passed} passed, {failed} failed, {skipped} skipped")

    return passed, failed, skipped


def main():
    parser = argparse.ArgumentParser(
        description="VibeCode OS structural smoke tests"
    )
    parser.add_argument(
        "--scenario",
        help="Run only the named scenario",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detail even on pass",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Preserve temp repos for debugging",
    )
    parser.add_argument(
        "--install-script",
        default=str(REPO_ROOT / "install.py"),
        help="Path to install.py (default: auto-detected from repo root)",
    )
    parser.add_argument(
        "--strict-cli",
        action="store_true",
        help="Make Claude CLI probe a required failure if unavailable",
    )

    args = parser.parse_args()

    config = Config(
        install_script=args.install_script,
        src_dir=REPO_ROOT / "src",
        keep_temp=args.keep_temp,
        verbose=args.verbose,
        strict_cli=args.strict_cli,
    )

    # Verify install script exists
    if not config.install_script.exists():
        print(f"Error: install.py not found at {config.install_script}")
        sys.exit(1)

    _, failed, _ = run_scenarios(config, args.scenario)
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
