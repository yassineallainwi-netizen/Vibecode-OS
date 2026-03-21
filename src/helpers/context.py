#!/usr/bin/env python3
"""
VibeCode OS — context helpers (007+)
Deterministic utilities for hashing, atomic writes, path safety,
ANSI stripping, and repo maturity detection.
Python 3.8+, stdlib only.
"""

import hashlib
import os
import re
import tempfile


def compute_sha256(text: str) -> str:
    """Return the SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atomic_write(path: str, content: str, validator=None) -> None:
    """
    Write content to path atomically: temp file → fsync → (validate) → rename.
    Never leaves a partial file at the destination on failure.

    validator: optional callable(content: str) -> Tuple[bool, str]
        If validator returns (False, reason): temp file is deleted and
        ValueError(reason) is raised — the destination file is never touched.
        Pass validator=None (default) to keep existing behavior.
    """
    dir_name = os.path.dirname(os.path.abspath(path))
    os.makedirs(dir_name, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=".vibe_tmp_")
    renamed = False
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        if validator is not None:
            # Re-open and validate temp file BEFORE renaming into place
            try:
                with open(tmp_path, "r", encoding="utf-8") as f:
                    written = f.read()
                ok, reason = validator(written)
            except Exception as exc:
                ok, reason = False, f"Validator read failed: {exc}"
            if not ok:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise ValueError(f"Pre-rename validation failed: {reason}")
        os.replace(tmp_path, path)
        renamed = True
    except Exception:
        if not renamed:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences and control characters from text."""
    # Remove ANSI escape sequences (CSI, OSC, etc.)
    ansi_escape = re.compile(
        r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))"
    )
    text = ansi_escape.sub("", text)
    # Remove remaining non-printable control characters (except \n, \r, \t)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text


def normalize_path(path: str, root: str) -> str:
    """
    Resolve path to absolute canonical form and verify it stays within root.
    Raises ValueError on path traversal attempts.
    """
    abs_root = os.path.realpath(os.path.abspath(root))
    abs_path = os.path.realpath(os.path.abspath(os.path.join(root, path)))
    if not abs_path.startswith(abs_root + os.sep) and abs_path != abs_root:
        raise ValueError(
            f"Path traversal rejected: '{path}' resolves outside root '{root}'"
        )
    return abs_path


def compute_repo_maturity(root: str) -> dict:
    """
    Compute a maturity snapshot for the repo at root.
    Returns a dict with boolean flags and an overall score.

    Score 0-2: newbie mode (interpretive output)
    Score 3+:  expert mode (terse output)
    """
    def exists(rel):
        return os.path.exists(os.path.join(root, rel))

    def file_has_content(rel, marker=None):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            return False
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            if not content.strip():
                return False
            if marker and marker not in content:
                return False
            return True
        except OSError:
            return False

    flags = {
        "agents_configured": file_has_content("AGENTS.md") and not _agents_is_template(os.path.join(root, "AGENTS.md")),
        "claude_md_present": exists("CLAUDE.md"),
        "verification_declared": _has_declared_commands(os.path.join(root, "AGENTS.md")),
        "git_present": exists(".git"),
        "has_features": _has_features(root),
        "recent_verify": _has_recent_verify(root),
        "recent_session_log": file_has_content("SESSION_LOG.md"),
    }
    score = sum(1 for v in flags.values() if v)
    flags["score"] = score
    flags["mode"] = "expert" if score >= 3 else "newbie"
    return flags


def _agents_is_template(path: str) -> bool:
    """Return True if AGENTS.md looks like an unmodified template."""
    if not os.path.exists(path):
        return True
    try:
        content = open(path, "r", encoding="utf-8", errors="replace").read()
        # Check for version marker (set in 007)
        if "<!-- vibecode:agents:v2 -->" in content:
            # Template if all project-specific sections still have [TODO:]
            ps_section = _extract_section(content, "## Project-specific rules")
            if ps_section and "[TODO:" in ps_section:
                return True
        # Legacy detection: small file with only boilerplate
        if len(content.encode("utf-8")) < 600:
            return True
        # Boilerplate fingerprints still present
        boilerplate = [
            "[TODO: e.g.",
            "e.g. \"Python 3.10+",
            "e.g. \"Flutter + Dart",
            "e.g. \"never modify auth.py",
            "e.g. \"run pytest before",
        ]
        hits = sum(1 for b in boilerplate if b in content)
        if hits >= 3:
            return True
        return False
    except OSError:
        return True


def _has_declared_commands(path: str) -> bool:
    """Return True if AGENTS.md has any non-empty command registry entries."""
    if not os.path.exists(path):
        return False
    try:
        content = open(path, "r", encoding="utf-8", errors="replace").read()
        for key in ("verify_cmd:", "test_cmd:", "lint_cmd:", "typecheck_cmd:", "build_cmd:"):
            if key in content:
                # Check the value is not just a [TODO:] placeholder
                idx = content.index(key)
                line = content[idx:content.find("\n", idx)]
                if "[TODO:" not in line and len(line.split(":", 1)[-1].strip()) > 0:
                    return True
        return False
    except OSError:
        return False


def _extract_section(content: str, heading: str) -> str:
    """Extract text of a markdown section (between heading and next ## heading)."""
    idx = content.find(heading)
    if idx == -1:
        return ""
    rest = content[idx + len(heading):]
    next_heading = re.search(r"\n##\s", rest)
    if next_heading:
        return rest[:next_heading.start()]
    return rest


def _has_features(root: str) -> bool:
    features_dir = os.path.join(root, "features")
    if not os.path.isdir(features_dir):
        return False
    pattern = re.compile(r"^FEATURE-\d{3}-[a-z0-9-]+$")
    for entry in os.listdir(features_dir):
        if pattern.match(entry) and os.path.isdir(os.path.join(features_dir, entry)):
            return True
    return False


def _has_recent_verify(root: str) -> bool:
    features_dir = os.path.join(root, "features")
    if not os.path.isdir(features_dir):
        return False
    for entry in os.listdir(features_dir):
        verify_path = os.path.join(features_dir, entry, "VERIFY.md")
        if os.path.exists(verify_path):
            return True
    return False
