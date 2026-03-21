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


# ---------- FEATURE-007 scenarios ----------


def agents_version_marker(config):
    """Verify AGENTS.md template contains the vibecode:agents:v2 version marker."""
    agents_path = config.src_dir / "templates" / "AGENTS.md"
    assert_exists(agents_path)
    content = read_file(agents_path)
    marker = "<!-- vibecode:agents:v2 -->"
    if marker not in content:
        raise AssertionError(
            f"AGENTS.md template missing version marker: {marker!r}\n"
            f"  path: {agents_path}"
        )
    return True, f"AGENTS.md template contains version marker"


def agents_command_registry(config):
    """Verify AGENTS.md template contains all 5 command registry keys."""
    agents_path = config.src_dir / "templates" / "AGENTS.md"
    assert_exists(agents_path)
    content = read_file(agents_path)
    required_keys = ["verify_cmd:", "test_cmd:", "lint_cmd:", "typecheck_cmd:", "build_cmd:"]
    missing = [k for k in required_keys if k not in content]
    if missing:
        raise AssertionError(
            f"AGENTS.md template missing command registry keys: {missing}\n"
            f"  path: {agents_path}"
        )
    return True, f"AGENTS.md template contains all 5 command registry keys"


def session_log_context_pointer(config):
    """Verify SESSION_LOG.md template uses 'Context pointer' wording."""
    log_path = config.src_dir / "templates" / "SESSION_LOG.md"
    assert_exists(log_path)
    content = read_file(log_path)
    if "Context pointer:" not in content:
        raise AssertionError(
            f"SESSION_LOG.md template missing 'Context pointer:' wording\n"
            f"  path: {log_path}"
        )
    return True, "SESSION_LOG.md template uses contextual pointer wording"


def active_feature_sanitized(config):
    """Verify installer creates an empty active_feature (safe for format validation)."""
    tmp, _ = _do_first_install(config)
    try:
        af_path = tmp / ".claude" / "active_feature"
        assert_exists(af_path)
        assert_file_empty(af_path)
        return True, "active_feature created empty (safe for format validation)"
    finally:
        if not config.keep_temp:
            cleanup_temp_repo(tmp)


def installer_creates_required_dirs(config):
    """Verify installer creates .claude/skills/ and features/ directories."""
    tmp, result = _do_first_install(config)
    try:
        assert_dir_exists(tmp / ".claude" / "skills")
        assert_dir_exists(tmp / "features")
        return True, ".claude/skills/ and features/ directories created"
    finally:
        if not config.keep_temp:
            cleanup_temp_repo(tmp)


# ---------- FEATURE-008 scenarios ----------


def approved_commands_created(config):
    """Verify .claude/approved_commands.json is created on first install with valid JSON."""
    import json as _json
    tmp, _ = _do_first_install(config)
    try:
        path = tmp / ".claude" / "approved_commands.json"
        assert_exists(path)
        content = read_file(path)
        data = _json.loads(content)
        if "schema_version" not in data:
            raise AssertionError("approved_commands.json missing schema_version")
        if "commands" not in data:
            raise AssertionError("approved_commands.json missing commands array")
        if not isinstance(data["commands"], list):
            raise AssertionError("commands must be an array")
        assert_created_report(normalize(
            __import__("subprocess").run(
                [__import__("sys").executable, str(config.install_script)],
                cwd=str(create_temp_repo()),
                capture_output=True,
                timeout=30,
            ).stdout.decode("utf-8", errors="replace")
        ), ".claude/approved_commands.json")
        return True, "approved_commands.json created with valid schema"
    finally:
        if not config.keep_temp:
            cleanup_temp_repo(tmp)


def approved_commands_preserved(config):
    """Verify .claude/approved_commands.json is NOT overwritten on second install."""
    import json as _json
    tmp, _ = _do_first_install(config)
    try:
        path = tmp / ".claude" / "approved_commands.json"
        # Modify the file to simulate user data
        custom = {"schema_version": 1, "commands": [{"cmd": "pytest", "cmd_hash": "abc123", "repo_id": "test"}], "checksum": "custom"}
        write_file(path, _json.dumps(custom, indent=2))
        snapshot = read_file(path)

        # Run installer again
        result = run_installer(config.install_script, tmp)
        assert_returncode(result)
        output = normalize(result.stdout)

        # Must be preserved, not overwritten
        assert_file_unchanged(path, snapshot)
        assert_preserved_report(output, ".claude/approved_commands.json")
        return True, "approved_commands.json preserved on second install"
    finally:
        if not config.keep_temp:
            cleanup_temp_repo(tmp)


def command_validation_rejects_metacharacters(config):
    """Verify the validation helper rejects shell metacharacters."""
    import sys as _sys
    helpers_path = REPO_ROOT / "src" / "helpers"
    _sys.path.insert(0, str(helpers_path))
    try:
        from verification import validate_command
        dangerous = ["npm test | rm -rf /", "pytest; echo pwned", "$(malicious)", "cmd > /dev/null", "sudo pytest"]
        for cmd in dangerous:
            valid, reason = validate_command(cmd)
            if valid:
                raise AssertionError(f"Should have rejected: {cmd!r} — reason: {reason}")
        # Valid commands should pass
        valid_cmds = ["pytest", "npm test", "flutter test", "cargo test", "make test"]
        for cmd in valid_cmds:
            valid, reason = validate_command(cmd)
            if not valid:
                raise AssertionError(f"Should have accepted: {cmd!r} — reason: {reason}")
        return True, "Dangerous commands rejected, trusted commands accepted"
    except ImportError as e:
        raise AssertionError(f"Cannot import verification helper: {e}")


def ansi_stripping(config):
    """Verify strip_ansi removes escape sequences without corrupting text."""
    import sys as _sys
    helpers_path = REPO_ROOT / "src" / "helpers"
    _sys.path.insert(0, str(helpers_path))
    try:
        from verification import strip_ansi
        raw = "\x1b[31mFAILED\x1b[0m test_foo.py::test_bar\n\x1b[32m5 passed\x1b[0m"
        cleaned = strip_ansi(raw)
        if "\x1b" in cleaned:
            raise AssertionError(f"ANSI escape sequences not removed: {cleaned!r}")
        if "FAILED" not in cleaned or "5 passed" not in cleaned:
            raise AssertionError(f"Text content corrupted: {cleaned!r}")
        return True, "ANSI stripping removes escapes, preserves text content"
    except ImportError as e:
        raise AssertionError(f"Cannot import verification helper: {e}")


def downgrade_on_zero_tests(config):
    """Verify classify_evidence downgrades when 0 tests detected."""
    import sys as _sys
    helpers_path = REPO_ROOT / "src" / "helpers"
    _sys.path.insert(0, str(helpers_path))
    try:
        from verification import triage_log, classify_evidence
        # Output that looks like success but has 0 tests
        output = "============================= 0 passed =============================="
        triage = triage_log(output)
        label = classify_evidence(0, output, triage)
        if label == "command_verified":
            raise AssertionError(f"Should have downgraded 0-test output, got: {label!r}")
        return True, f"0-test output correctly downgraded to: {label!r}"
    except ImportError as e:
        raise AssertionError(f"Cannot import verification helper: {e}")


# ---------- FEATURE-009 scenarios ----------


def context_directory_created(config):
    """Verify .claude/context/ directory is created on first install."""
    tmp, _ = _do_first_install(config)
    try:
        assert_dir_exists(tmp / ".claude" / "context")
        return True, ".claude/context/ directory created on install"
    finally:
        if not config.keep_temp:
            cleanup_temp_repo(tmp)


def context_directory_preserved(config):
    """Verify .claude/context/ is preserved (not removed) on second install."""
    tmp, _ = _do_first_install(config)
    try:
        context_dir = tmp / ".claude" / "context"
        assert_dir_exists(context_dir)
        # Write a file inside to confirm it is not cleared
        sentinel = context_dir / "sentinel.txt"
        write_file(sentinel, "user data\n")

        result = run_installer(config.install_script, tmp)
        assert_returncode(result)

        if not sentinel.exists():
            raise AssertionError(".claude/context/ was cleared on second install — sentinel file removed")
        return True, ".claude/context/ preserved on second install"
    finally:
        if not config.keep_temp:
            cleanup_temp_repo(tmp)


def runtime_directory_created(config):
    """Verify .claude/runtime/ directory is created on first install."""
    tmp, _ = _do_first_install(config)
    try:
        assert_dir_exists(tmp / ".claude" / "runtime")
        return True, ".claude/runtime/ directory created on install"
    finally:
        if not config.keep_temp:
            cleanup_temp_repo(tmp)


def schema_version_present(config):
    """Verify compaction.py write_project_state produces schema_version field."""
    import sys as _sys
    import json as _json
    import tempfile
    helpers_path = REPO_ROOT / "src" / "helpers"
    _sys.path.insert(0, str(helpers_path))
    try:
        from compaction import write_project_state, read_project_state
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".claude" / "context").mkdir(parents=True)
            data = {
                "project": "test",
                "active_feature": "",
                "workflow_mode": "idle",
                "risk_flags": [],
                "verification_readiness": "none",
                "last_completed_feature": "FEATURE-009-test",
                "recent_files": [],
                "command_registry": {},
            }
            write_project_state(str(root), data)
            artifact = read_project_state(str(root))
            if artifact is None:
                raise AssertionError("read_project_state returned None after write")
            if artifact.get("schema_version") != 1:
                raise AssertionError(f"schema_version missing or wrong: {artifact.get('schema_version')!r}")
        return True, "write_project_state produces valid artifact with schema_version=1"
    except ImportError as e:
        raise AssertionError(f"Cannot import compaction helper: {e}")


def atomic_write_safety(config):
    """Verify atomic_write in context.py writes cleanly and does not leave temp files."""
    import sys as _sys
    import tempfile
    helpers_path = REPO_ROOT / "src" / "helpers"
    _sys.path.insert(0, str(helpers_path))
    try:
        from context import atomic_write
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_output.json"
            atomic_write(str(target), '{"ok": true}\n')
            if not target.exists():
                raise AssertionError("atomic_write did not create the target file")
            content = target.read_text(encoding="utf-8")
            if '"ok": true' not in content:
                raise AssertionError(f"atomic_write output corrupted: {content!r}")
            # Verify no temp files left behind
            temp_files = list(Path(tmpdir).glob("*.tmp"))
            if temp_files:
                raise AssertionError(f"atomic_write left temp files: {temp_files}")
        return True, "atomic_write creates file cleanly with no leftover temp files"
    except ImportError as e:
        raise AssertionError(f"Cannot import context helper: {e}")


# ---------- FEATURE-010 scenarios ----------


def plugin_manifest_valid(config):
    """Verify .claude-plugin/plugin.json exists and has required fields."""
    import json as _json
    plugin_json = REPO_ROOT / ".claude-plugin" / "plugin.json"
    assert_exists(plugin_json)
    try:
        data = _json.loads(read_file(plugin_json))
    except Exception as e:
        raise AssertionError(f"plugin.json is not valid JSON: {e}")
    required = ["name", "version", "skills", "capabilities_required", "fallback_mode"]
    missing = [f for f in required if f not in data]
    if missing:
        raise AssertionError(f"plugin.json missing fields: {missing}")
    if data.get("fallback_mode") != "standalone":
        raise AssertionError(f"fallback_mode must be 'standalone', got: {data.get('fallback_mode')!r}")
    return True, f"plugin.json valid — {data['name']} v{data['version']}"


def plugin_skills_present(config):
    """Verify all 4 skill files exist under .claude-plugin/skills/."""
    skill_names = ["vibe-start", "vibe-resume", "vibe-status", "vibe-done"]
    for skill in skill_names:
        path = REPO_ROOT / ".claude-plugin" / "skills" / skill / "SKILL.md"
        assert_exists(path)
    return True, f"All 4 skill files present under .claude-plugin/skills/"


def plugin_helpers_present(config):
    """Verify all helper scripts present under .claude-plugin/helpers/."""
    helpers = ["context.py", "claude_md.py", "verification.py", "approval.py", "compaction.py"]
    missing = []
    for h in helpers:
        path = REPO_ROOT / ".claude-plugin" / "helpers" / h
        if not path.exists():
            missing.append(h)
    if missing:
        raise AssertionError(f"Missing plugin helpers: {missing}")
    return True, f"All {len(helpers)} helpers present under .claude-plugin/helpers/"


def standalone_mode_unchanged(config):
    """Verify install.py --plugin still installs .claude/skills/ alongside plugin."""
    tmp = create_temp_repo()
    try:
        result = run_command(
            [__import__("sys").executable, str(config.install_script), "--plugin"],
            cwd=str(tmp),
            timeout=30,
        )
        assert_returncode(result)
        # Both standalone and plugin skills must be present
        skill_names = ["vibe-start", "vibe-resume", "vibe-status", "vibe-done"]
        for skill in skill_names:
            assert_exists(tmp / ".claude" / "skills" / skill / "SKILL.md")
            assert_exists(tmp / ".claude-plugin" / "skills" / skill / "SKILL.md")
        return True, "Both .claude/skills/ and .claude-plugin/skills/ installed by --plugin"
    finally:
        if not config.keep_temp:
            cleanup_temp_repo(tmp)


# ---------- FEATURE-011 / v2.0.1 scenarios ----------


def py38_compatible_imports(config):
    """Verify all Python helper files are compatible with Python 3.8 syntax."""
    import ast
    helpers_dir = REPO_ROOT / "src" / "helpers"
    adapter_dir = REPO_ROOT / "src" / "adapter"
    py_files = list(helpers_dir.glob("*.py")) + list(adapter_dir.glob("*.py"))
    errors = []
    for py_file in py_files:
        source = py_file.read_text(encoding="utf-8")
        try:
            try:
                ast.parse(source, feature_version=(3, 8))
            except TypeError:
                # feature_version not supported — fall back to basic parse + banned scan
                ast.parse(source)
                # Banned 3.10+ construct scan
                import re as _re
                if _re.search(r"(?<!\w)match\s+\w.*:\s*$", source, _re.MULTILINE):
                    errors.append(f"{py_file.name}: may use structural match (3.10+)")
        except SyntaxError as exc:
            errors.append(f"{py_file.name}: {exc}")
    if errors:
        raise AssertionError(
            "Python 3.8 compatibility failures:\n" + "\n".join(errors)
        )
    return True, f"All {len(py_files)} helper files pass Python 3.8 compatibility check"


def probe_capabilities_command_exec_true(config):
    """Verify probe_capabilities() reports command_exec: True in current env."""
    import sys as _sys
    import tempfile as _tempfile
    adapter_path = REPO_ROOT / "src" / "adapter"
    _sys.path.insert(0, str(adapter_path))
    try:
        from capabilities import probe_capabilities
        with _tempfile.TemporaryDirectory() as tmpdir:
            caps = probe_capabilities(tmpdir)
        if not caps.get("command_exec"):
            raise AssertionError(
                f"probe_capabilities() returned command_exec=False in current env; "
                f"full caps: {caps}"
            )
        return True, "probe_capabilities() correctly reports command_exec: True"
    except ImportError as exc:
        raise AssertionError(f"Cannot import capabilities: {exc}")


def verified_command_no_shell(config):
    """Verify run_verified_command('python --version', cwd) exits 0 with shell=False."""
    import sys as _sys
    import tempfile as _tempfile
    helpers_path = REPO_ROOT / "src" / "helpers"
    _sys.path.insert(0, str(helpers_path))
    try:
        from verification import run_verified_command
        with _tempfile.TemporaryDirectory() as tmpdir:
            result = run_verified_command("python --version", tmpdir, timeout=10)
        if result["exit_code"] != 0:
            raise AssertionError(
                f"run_verified_command('python --version') failed: "
                f"exit_code={result['exit_code']}, error={result.get('error')!r}"
            )
        return True, f"run_verified_command succeeds with shell=False: exit_code=0"
    except ImportError as exc:
        raise AssertionError(f"Cannot import verification helper: {exc}")


# ---------- Scenario registry ----------
# (function, required)

SCENARIOS = {
    "installer_first_run": (installer_first_run, True),
    "installer_second_run": (installer_second_run, True),
    "managed_skill_updates": (managed_skill_updates, True),
    "template_markers": (template_markers, True),
    "agents_version_marker": (agents_version_marker, True),
    "agents_command_registry": (agents_command_registry, True),
    "session_log_context_pointer": (session_log_context_pointer, True),
    "active_feature_sanitized": (active_feature_sanitized, True),
    "installer_creates_required_dirs": (installer_creates_required_dirs, True),
    "approved_commands_created": (approved_commands_created, True),
    "approved_commands_preserved": (approved_commands_preserved, True),
    "command_validation_rejects_metacharacters": (command_validation_rejects_metacharacters, True),
    "ansi_stripping": (ansi_stripping, True),
    "downgrade_on_zero_tests": (downgrade_on_zero_tests, True),
    "context_directory_created": (context_directory_created, True),
    "context_directory_preserved": (context_directory_preserved, True),
    "runtime_directory_created": (runtime_directory_created, True),
    "schema_version_present": (schema_version_present, True),
    "atomic_write_safety": (atomic_write_safety, True),
    "plugin_manifest_valid": (plugin_manifest_valid, True),
    "plugin_skills_present": (plugin_skills_present, True),
    "plugin_helpers_present": (plugin_helpers_present, True),
    "standalone_mode_unchanged": (standalone_mode_unchanged, True),
    "py38_compatible_imports": (py38_compatible_imports, True),
    "probe_capabilities_command_exec_true": (probe_capabilities_command_exec_true, True),
    "verified_command_no_shell": (verified_command_no_shell, True),
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
