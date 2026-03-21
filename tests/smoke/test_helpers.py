#!/usr/bin/env python3
"""
VibeCode OS v2.0.1 — focused helper regression tests.
Tests compaction.py, verification.py, and capabilities.py.
Python 3.8+, stdlib only.
"""

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HELPERS_PATH = REPO_ROOT / "src" / "helpers"
ADAPTER_PATH = REPO_ROOT / "src" / "adapter"

sys.path.insert(0, str(HELPERS_PATH))
sys.path.insert(0, str(ADAPTER_PATH))


# ---------- Helpers ----------


def _minimal_project_data():
    return {
        "project": "test",
        "active_feature": "",
        "workflow_mode": "idle",
        "risk_flags": [],
        "verification_readiness": "none",
        "last_completed_feature": "",
        "recent_files": [],
        "command_registry": {},
    }


# ---------- compaction.py regressions ----------


class TestIsStale(unittest.TestCase):

    def _make_artifact(self, hours_ago):
        epoch = time.time() - hours_ago * 3600
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))
        return {"last_compacted": ts, "schema_version": 1}

    def test_is_stale_fresh(self):
        """Fresh artifact (0h old) must not be stale."""
        from compaction import is_stale
        self.assertFalse(is_stale(self._make_artifact(0)),
                         "Fresh artifact should not be stale")

    def test_is_stale_old(self):
        """Artifact 25h old must be stale."""
        from compaction import is_stale
        self.assertTrue(is_stale(self._make_artifact(25)),
                        "25h-old artifact should be stale")

    def test_is_stale_malformed_timestamp(self):
        """Malformed timestamp must yield stale."""
        from compaction import is_stale
        artifact = {"last_compacted": "not-a-timestamp", "schema_version": 1}
        self.assertTrue(is_stale(artifact),
                        "Malformed timestamp should yield stale")

    def test_is_stale_missing_timestamp(self):
        """Missing last_compacted and updated_at must yield stale."""
        from compaction import is_stale
        artifact = {"schema_version": 1}
        self.assertTrue(is_stale(artifact),
                        "Missing timestamp should yield stale")


class TestWriteProjectState(unittest.TestCase):

    def test_write_project_state_roundtrip(self):
        """write then read; schema_version must be 1."""
        from compaction import write_project_state, read_project_state
        with tempfile.TemporaryDirectory() as tmpdir:
            ok, reason = write_project_state(tmpdir, _minimal_project_data())
            self.assertTrue(ok, f"write_project_state failed: {reason}")
            artifact = read_project_state(tmpdir)
            self.assertIsNotNone(artifact, "read_project_state returned None")
            self.assertEqual(artifact.get("schema_version"), 1)

    def test_post_rename_validation_rejects_corrupt(self):
        """Patched atomic_write raising ValueError returns (False, ...) and leaves prior artifact intact."""
        from compaction import write_project_state, read_project_state
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write a valid artifact first
            ok, _ = write_project_state(tmpdir, _minimal_project_data())
            self.assertTrue(ok)
            valid_artifact = read_project_state(tmpdir)
            self.assertIsNotNone(valid_artifact)

            # Now simulate a corrupt write by raising in atomic_write
            with patch("compaction.atomic_write",
                       side_effect=ValueError("simulated corrupt write")):
                ok2, reason2 = write_project_state(tmpdir, _minimal_project_data())
                self.assertFalse(ok2,
                                 "Should return False when atomic_write raises")
                self.assertIn("corrupt", reason2.lower(),
                              f"Reason should mention the error: {reason2!r}")

            # Original valid artifact must still be readable
            artifact_after = read_project_state(tmpdir)
            self.assertIsNotNone(artifact_after,
                                 "Valid artifact should survive failed write")

    def test_checksum_mismatch_fails_closed(self):
        """Corrupt checksum in stored artifact causes read to return None."""
        from compaction import write_project_state, read_project_state
        with tempfile.TemporaryDirectory() as tmpdir:
            write_project_state(tmpdir, _minimal_project_data())
            path = os.path.join(tmpdir, ".claude", "context", "project_state.json")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["checksum"] = "deadbeef00000000"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            result = read_project_state(tmpdir)
            self.assertIsNone(result,
                              "Corrupt checksum should cause read to return None")


# ---------- verification.py regressions ----------


class TestValidateCommand(unittest.TestCase):

    def test_exe_normalization(self):
        """pytest.exe and npm.cmd are accepted; cmd.exe is rejected."""
        from verification import validate_command
        ok, _ = validate_command("pytest.exe")
        self.assertTrue(ok, "pytest.exe should be accepted after .exe normalization")
        ok, _ = validate_command("npm.cmd test")
        self.assertTrue(ok, "npm.cmd should be accepted after .cmd normalization")
        ok, _ = validate_command("cmd.exe /c echo hi")
        self.assertFalse(ok, "cmd.exe should be rejected as a shell trampoline")

    def test_pwsh_rejected(self):
        """pwsh is a shell trampoline and must be rejected."""
        from verification import validate_command
        ok, reason = validate_command("pwsh -c evil")
        self.assertFalse(ok, f"pwsh should be rejected, got: {reason!r}")

    def test_absolute_path_rejected(self):
        """Absolute paths to executables must be rejected."""
        from verification import validate_command
        ok, reason = validate_command("C:\\Windows\\System32\\cmd.exe /c evil")
        self.assertFalse(ok, f"Windows absolute path should be rejected: {reason!r}")
        ok, reason = validate_command("/usr/bin/python test.py")
        self.assertFalse(ok, f"Unix absolute path should be rejected: {reason!r}")

    def test_empty_argv_rejected(self):
        """Whitespace-only command must be rejected."""
        from verification import validate_command
        ok, reason = validate_command("   ")
        self.assertFalse(ok, f"Whitespace command should be rejected: {reason!r}")

    def test_unknown_tool_rejected(self):
        """Unknown executable not in trusted list must be rejected."""
        from verification import validate_command
        ok, reason = validate_command("unknown_tool_xyz arg1")
        self.assertFalse(ok, f"Unknown tool should be rejected: {reason!r}")

    def test_nonzero_exit_not_verified(self):
        """classify_evidence with nonzero exit must never produce command_verified."""
        from verification import classify_evidence, triage_log
        output = "Error: something went wrong"
        triage = triage_log(output)
        label = classify_evidence(1, output, triage)
        self.assertNotEqual(label, "command_verified",
                            f"Nonzero exit must not produce command_verified, got: {label!r}")

    def test_shell_false_asserted(self):
        """subprocess.run must be called with shell=False."""
        from verification import run_verified_command

        captured = {}

        def capturing_run(args, **kwargs):
            captured["shell"] = kwargs.get("shell", "NOT_SET")
            result = MagicMock()
            result.returncode = 0
            result.stdout = b""
            result.stderr = b""
            return result

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("verification.subprocess.run",
                       side_effect=capturing_run):
                run_verified_command("python --version", tmpdir, timeout=5)

        self.assertIn("shell", captured,
                      "subprocess.run should have been called")
        self.assertIs(captured["shell"], False,
                      f"subprocess.run must use shell=False, got: {captured.get('shell')!r}")


# ---------- capabilities.py regressions ----------


class TestProbeCommandExec(unittest.TestCase):

    def test_sys_executable_tried_first(self):
        """sys.executable must be the first candidate tried."""
        from capabilities import _probe_command_exec

        tried = []

        def fake_run(args, **kwargs):
            tried.append(args[0])
            result = MagicMock()
            result.returncode = 0
            return result

        with patch("capabilities.subprocess.run", side_effect=fake_run):
            _probe_command_exec(timeout_ms=100000)

        self.assertTrue(len(tried) > 0, "subprocess.run was never called")
        self.assertEqual(tried[0], sys.executable,
                         f"First candidate must be sys.executable ({sys.executable!r}), "
                         f"got: {tried[0]!r}")

    def test_dedupe_candidates(self):
        """No duplicate entries in the candidate launcher list."""
        from capabilities import _probe_command_exec

        tried = []

        def fake_run(args, **kwargs):
            tried.append(args[0])
            result = MagicMock()
            result.returncode = 1  # All fail so all are tried
            return result

        with patch("capabilities.subprocess.run", side_effect=fake_run):
            _probe_command_exec(timeout_ms=100000)  # Large budget — won't expire

        self.assertEqual(len(tried), len(set(tried)),
                         f"Duplicate candidates found in tried list: {tried}")

    def test_deadline_respected(self):
        """Budget exhaustion before first iteration must skip all candidates."""
        from capabilities import _probe_command_exec

        tried = []

        def fake_run(args, **kwargs):
            tried.append(args[0])
            result = MagicMock()
            result.returncode = 1
            return result

        # budget_end = time() + 0.5; first remaining = budget_end - time()
        # Sequence: [0.0 → budget_end=0.5, 1.0 → remaining=0.5-1.0=-0.5 → break]
        time_sequence = iter([0.0, 1.0])
        with patch("capabilities.subprocess.run", side_effect=fake_run):
            with patch("capabilities.time.time", side_effect=time_sequence):
                _probe_command_exec(timeout_ms=500)

        self.assertEqual(len(tried), 0,
                         f"No candidates should run after budget exhausted, got: {tried}")


if __name__ == "__main__":
    unittest.main()
