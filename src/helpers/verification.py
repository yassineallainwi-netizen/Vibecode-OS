#!/usr/bin/env python3
"""
VibeCode OS — verification helpers (008+)
Evidence labeling, command validation, ANSI stripping, output triage,
audit trail management, and VERIFY.md parsing.
Python 3.8+, stdlib only.
"""

import hashlib
import os
import re
import shlex
import subprocess


# ---------- Evidence model ----------

# Ordered evidence states (weakest to strongest)
EVIDENCE_ORDER = ["none", "weak", "partial", "strong", "fresh_strong"]

# Display mapping for skill output
EVIDENCE_DISPLAY = {
    "none": "none",
    "weak": "low",
    "partial": "medium",
    "strong": "high",
    "fresh_strong": "high",
}

# Label → state mapping
LABEL_TO_STATE = {
    "command_verified": "fresh_strong",
    "repo_observed": "strong",
    "user_reported": "partial",
    "spec_expected": "weak",
}


def evidence_strength_display(labels: list) -> str:
    """
    Given a list of evidence labels (from criteria in VERIFY.md),
    return the display strength: high / medium / low / none.
    Uses the best label found (highest ordered state).
    """
    if not labels:
        return "none"
    best = "none"
    best_idx = 0
    for label in labels:
        state = LABEL_TO_STATE.get(label, "none")
        idx = EVIDENCE_ORDER.index(state) if state in EVIDENCE_ORDER else 0
        if idx > best_idx:
            best_idx = idx
            best = state
    return EVIDENCE_DISPLAY.get(best, "none")


# ---------- Command validation ----------

# Trusted PATH-resolved tool names (no absolute paths)
TRUSTED_TOOLS = {
    "python", "python3", "py", "node", "npm", "npx", "yarn", "pnpm",
    "pytest", "py.test", "unittest",
    "flutter", "dart",
    "cargo", "rustc",
    "go",
    "make", "gradle", "mvn", "ant",
    "jest", "mocha", "vitest", "jasmine",
    "rspec", "bundle",
    "php", "composer",
    "dotnet",
    "swift", "xcodebuild",
    "tsc", "eslint", "flake8", "mypy", "ruff", "pylint",
}

# Shell trampolines — never allowed as the executable
SHELL_TRAMPOLINES = {"cmd", "powershell", "pwsh", "bash", "sh", "zsh", "fish", "csh"}

# Shell metacharacters that are never allowed
SHELL_METACHARACTERS = re.compile(r'[|&;`$<>]|\$\(|\$\{')

# Privileged commands never allowed
PRIVILEGED_COMMANDS = {"sudo", "su", "doas", "pkexec", "runas"}

# Absolute path pattern (starts with / on Unix or X:\ on Windows)
ABSOLUTE_PATH = re.compile(r'^(/|[A-Za-z]:[/\\])')


def validate_command(cmd: str) -> tuple:
    """
    Validate a verification command against the strict allow-list.
    Returns (is_valid: bool, reason: str).

    Rejection order:
    1. Empty / whitespace-only
    2. Multiline (\\n or \\r)
    3. Shell metacharacters
    4. shlex.split produces empty argv
    5. Normalize executable: basename → lower → strip .exe/.cmd/.bat
    6. Privileged commands
    7. Absolute paths
    8. Path separators in executable name (PATH-based only)
    9. Shell trampolines (cmd, powershell, pwsh, bash, sh, zsh, fish, csh)
    10. Not in TRUSTED_TOOLS
    """
    if not cmd or not cmd.strip():
        return False, "Empty command"

    stripped = cmd.strip()

    # Block newlines (command injection via multiline)
    if "\n" in stripped or "\r" in stripped:
        return False, "Newlines not allowed in commands"

    # Block shell metacharacters
    if SHELL_METACHARACTERS.search(stripped):
        return False, f"Shell metacharacters not allowed: {stripped!r}"

    # Parse into tokens (Windows-aware)
    try:
        parts = shlex.split(stripped, posix=(os.name != "nt"))
    except ValueError as exc:
        return False, f"Command parse error: {exc}"
    if not parts:
        return False, "Empty command after parsing"

    executable = parts[0]

    # Normalize: basename → lowercase → strip .exe / .cmd / .bat
    exec_base = os.path.basename(executable).lower()
    for suffix in (".exe", ".cmd", ".bat"):
        if exec_base.endswith(suffix):
            exec_base = exec_base[: -len(suffix)]
            break

    # Block privileged commands
    if exec_base in PRIVILEGED_COMMANDS:
        return False, f"Privileged command not allowed: {executable!r}"

    # Block absolute paths to executables
    if ABSOLUTE_PATH.match(executable):
        return False, f"Absolute executable paths not allowed: {executable!r}"

    # Block path separators in executable name (must be PATH-based)
    if "/" in executable or "\\" in executable:
        return False, f"Path separators in executable not allowed: {executable!r}"

    # Block shell trampolines
    if exec_base in SHELL_TRAMPOLINES:
        return False, f"Shell trampoline not allowed: {executable!r}"

    # Strict allow-list — unknown executables are rejected
    if exec_base not in TRUSTED_TOOLS:
        return False, f"Executable not in trusted list: {executable!r}"

    return True, "OK"


# ---------- Command execution ----------


def run_verified_command(cmd: str, cwd: str, timeout: int = 30, max_output: int = 51200) -> dict:
    """
    Run a validated verification command safely.

    Returns dict with:
      - success: bool
      - exit_code: int
      - stdout: str (ANSI-stripped, capped)
      - stderr: str (ANSI-stripped, capped)
      - truncated: bool
      - error: Optional[str] (on execution failure)
    """
    is_valid, reason = validate_command(cmd)
    if not is_valid:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
            "truncated": False,
            "error": f"Command blocked: {reason}",
        }

    # Minimal trusted environment
    safe_env = {k: os.environ[k] for k in ("PATH", "HOME", "PWD") if k in os.environ}
    # On Windows, also pass USERPROFILE and APPDATA for tools that need them
    for k in ("USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "SystemRoot", "WINDIR"):
        if k in os.environ:
            safe_env[k] = os.environ[k]

    try:
        parts = shlex.split(cmd, posix=(os.name != "nt"))
        if not parts:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": "",
                "truncated": False,
                "error": "Command parse produced empty argv",
            }
        result = subprocess.run(
            parts,
            shell=False,
            cwd=str(cwd),
            capture_output=True,
            timeout=timeout,
            env=safe_env,
        )
        raw_stdout = result.stdout.decode("utf-8", errors="replace")
        raw_stderr = result.stderr.decode("utf-8", errors="replace")

        stdout = strip_ansi(raw_stdout)
        stderr = strip_ansi(raw_stderr)
        combined = stdout + stderr

        truncated = len(combined.encode("utf-8")) > max_output
        if truncated:
            # Truncate to max_output bytes
            combined_bytes = combined.encode("utf-8")[:max_output]
            stdout = combined_bytes.decode("utf-8", errors="replace")
            stderr = ""

        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "truncated": truncated,
            "error": None,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
            "truncated": False,
            "error": f"Command timed out after {timeout}s",
        }
    except Exception as e:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
            "truncated": False,
            "error": f"Execution failed: {e}",
        }


# ---------- Output analysis ----------


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences and control characters from text."""
    ansi_escape = re.compile(
        r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))"
    )
    text = ansi_escape.sub("", text)
    # Remove non-printable control chars (keep \n, \r, \t)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text


def compute_output_hash(text: str) -> str:
    """Return SHA-256 hex digest of ANSI-stripped, UTF-8 encoded output."""
    cleaned = strip_ansi(text)
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()


def is_binary_output(raw_bytes: bytes) -> bool:
    """Return True if output appears to be binary (high density of non-text bytes)."""
    if not raw_bytes:
        return False
    non_text = sum(1 for b in raw_bytes[:512] if b < 32 and b not in (9, 10, 13))
    return non_text / min(len(raw_bytes), 512) > 0.3


def triage_log(output: str) -> dict:
    """
    Parse test/lint output into a structured summary.
    Returns dict with: tests_run, tests_failed, top_failing_files, top_error_classes, raw_summary.
    """
    result = {
        "tests_run": None,
        "tests_failed": None,
        "top_failing_files": [],
        "top_error_classes": [],
        "raw_summary": "",
    }

    # Try common test output patterns
    # pytest: "X passed", "X failed", "X error"
    m = re.search(r"(\d+)\s+passed", output)
    if m:
        result["tests_run"] = int(m.group(1))
    m = re.search(r"(\d+)\s+failed", output)
    if m:
        result["tests_failed"] = int(m.group(1))
        if result["tests_run"] is not None:
            result["tests_run"] += result["tests_failed"]

    # Jest/mocha: "X tests passed", "X tests failed"
    if result["tests_run"] is None:
        m = re.search(r"(\d+)\s+tests?\s+passed", output, re.IGNORECASE)
        if m:
            result["tests_run"] = int(m.group(1))
        m = re.search(r"(\d+)\s+tests?\s+failed", output, re.IGNORECASE)
        if m:
            result["tests_failed"] = int(m.group(1))

    # Flutter: "All tests passed!" or "X tests failed"
    if "All tests passed!" in output:
        result["tests_failed"] = 0

    # Extract top failing files (lines with FAILED or ERROR prefix)
    failing = re.findall(r"(?:FAILED|ERROR)\s+([\w./\\-]+\.[\w]+)", output)
    result["top_failing_files"] = list(dict.fromkeys(failing))[:5]

    # Extract error class names
    error_classes = re.findall(r"\b([A-Z][a-zA-Z]+(?:Error|Exception|Failure))\b", output)
    result["top_error_classes"] = list(dict.fromkeys(error_classes))[:3]

    # Build a compact raw summary (last 5 lines of output)
    lines = [l for l in output.strip().splitlines() if l.strip()]
    result["raw_summary"] = "\n".join(lines[-5:]) if lines else ""

    return result


def classify_evidence(exit_code: int, output: str, triage: dict) -> str:
    """
    Given execution results, return the evidence label.
    Never returns command_verified for non-zero exit code.
    """
    if exit_code != 0:
        return "repo_observed"  # command ran but failed

    # Downgrade weak success cases
    if not output.strip():
        return "repo_observed"  # empty output

    tests_run = triage.get("tests_run")
    tests_failed = triage.get("tests_failed")

    if tests_run is not None and tests_run == 0:
        return "repo_observed"  # 0 tests detected

    if tests_failed is not None and tests_failed > 0:
        return "repo_observed"  # tests ran but failed

    return "command_verified"


# ---------- VERIFY.md parsing ----------


def parse_verify_md(path: str) -> dict:
    """
    Parse a VERIFY.md file and return structured data.
    Returns dict with: criteria, status, audit_trail, known_gaps, what_was_built.
    """
    result = {
        "criteria": [],
        "status": None,
        "audit_trail": [],
        "known_gaps": "",
        "what_was_built": "",
    }

    if not os.path.exists(path):
        return result

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError:
        return result

    # Extract status
    m = re.search(r"^## Status\s*\n(.+)", content, re.MULTILINE)
    if m:
        result["status"] = m.group(1).strip()

    # Extract what was built
    m = re.search(r"^## What was built\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL | re.MULTILINE)
    if m:
        result["what_was_built"] = m.group(1).strip()

    # Extract known gaps
    m = re.search(r"^## Known gaps.*?\n(.*?)(?=\n## |\Z)", content, re.DOTALL | re.MULTILINE)
    if m:
        result["known_gaps"] = m.group(1).strip()

    # Extract criteria
    criteria_section = re.search(r"^## Acceptance criteria\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL | re.MULTILINE)
    if criteria_section:
        for line in criteria_section.group(1).splitlines():
            m = re.match(r"\s*-\s*\[([ x?])\]\s*(.+)", line)
            if m:
                check, text = m.group(1), m.group(2).strip()
                # Extract evidence label if present (pattern: "criterion — label: ...")
                label = None
                lm = re.search(r"—\s*(command_verified|repo_observed|user_reported|spec_expected):", text)
                if lm:
                    label = lm.group(1)
                result["criteria"].append({
                    "checked": check == "x",
                    "unverified": check == "?",
                    "text": text,
                    "label": label,
                })

    # Extract audit trail from HTML comment
    audit_m = re.search(r"<!--\s*audit_trail\s*\n(.*?)-->", content, re.DOTALL)
    if audit_m:
        for line in audit_m.group(1).splitlines():
            if "|" in line and not line.strip().startswith("|---"):
                parts = [p.strip() for p in line.strip().strip("|").split("|")]
                if len(parts) >= 5:
                    result["audit_trail"].append(parts)

    return result


# ---------- Audit trail ----------


def format_audit_trail_entry(criterion: str, label: str, command: str,
                              exit_code: int, timestamp: str, output_hash: str) -> str:
    """Format a single audit trail table row."""
    # Truncate criterion for table readability
    crit_display = criterion[:40] + "..." if len(criterion) > 40 else criterion
    cmd_display = command[:30] + "..." if len(command) > 30 else command
    return f"| {crit_display} | {label} | {cmd_display} | {exit_code} | {timestamp} | {output_hash[:12]}... |"


def build_audit_trail_block(entries: list) -> str:
    """Build the full HTML comment audit trail block."""
    if not entries:
        return ""
    header = "| criterion | label | command | exit_code | timestamp | output_sha256 |"
    separator = "|-----------|-------|---------|-----------|-----------|--------------|"
    rows = [format_audit_trail_entry(*e) for e in entries]
    return "<!-- audit_trail\n" + header + "\n" + separator + "\n" + "\n".join(rows) + "\n-->"
