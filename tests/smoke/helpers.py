"""
VibeCode OS smoke test helpers.
Reusable fixtures, assertions, and subprocess wrappers.
Python 3.8+, stdlib only.
"""

import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


# ---------- Fixtures ----------


def create_temp_repo():
    """Create an empty temp directory and return its Path."""
    return Path(tempfile.mkdtemp(prefix="vibecode_smoke_"))


def cleanup_temp_repo(path):
    """Windows-safe recursive delete (handles read-only files)."""
    def _onerror(func, fpath, exc_info):
        os.chmod(fpath, stat.S_IWRITE)
        func(fpath)

    shutil.rmtree(str(path), onerror=_onerror)


# ---------- Subprocess ----------


def _python():
    """Return the current Python interpreter path, with fallback."""
    return sys.executable or "python"


def run_installer(install_script, cwd, timeout=30):
    """Run install.py in the given working directory."""
    result = subprocess.run(
        [_python(), str(install_script)],
        cwd=str(cwd),
        capture_output=True,
        timeout=timeout,
    )
    # Decode bytes manually with error tolerance (Windows console may use cp1252)
    result.stdout = result.stdout.decode("utf-8", errors="replace")
    result.stderr = result.stderr.decode("utf-8", errors="replace")
    return result


def run_command(cmd, cwd=None, timeout=5):
    """Run an arbitrary command and return CompletedProcess."""
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        timeout=timeout,
    )
    result.stdout = result.stdout.decode("utf-8", errors="replace")
    result.stderr = result.stderr.decode("utf-8", errors="replace")
    return result


# ---------- File I/O ----------


def read_file(path):
    """Read a file with explicit UTF-8 encoding."""
    with open(str(path), "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    """Write a file with explicit UTF-8 encoding, creating parent dirs."""
    os.makedirs(os.path.dirname(str(path)), exist_ok=True)
    with open(str(path), "w", encoding="utf-8") as f:
        f.write(content)


def normalize(text):
    """Normalize line endings to LF for cross-platform comparison."""
    if text is None:
        return ""
    return text.replace("\r\n", "\n").replace("\r", "\n")


# ---------- Filesystem assertions ----------


def assert_exists(path):
    if not os.path.exists(str(path)):
        raise AssertionError(f"Expected to exist: {path}")


def assert_not_exists(path):
    if os.path.exists(str(path)):
        raise AssertionError(f"Expected NOT to exist: {path}")


def assert_dir_exists(path):
    if not os.path.isdir(str(path)):
        raise AssertionError(f"Expected directory: {path}")


def assert_dir_empty(path):
    """Assert path is a directory and contains no entries."""
    assert_dir_exists(path)
    contents = os.listdir(str(path))
    if contents:
        raise AssertionError(
            f"Expected empty directory: {path} — contains: {contents}"
        )


def assert_file_contains(path, text):
    """Assert a file's content includes the given substring."""
    content = read_file(path)
    if text not in content:
        raise AssertionError(f"{path} does not contain: {text!r}")


def assert_file_equals(path_a, path_b):
    """Assert two files have identical content (line-ending normalized)."""
    a = normalize(read_file(path_a))
    b = normalize(read_file(path_b))
    if a != b:
        pos = _first_diff(a, b)
        raise AssertionError(
            f"File content mismatch:\n"
            f"  {path_a}\n"
            f"  {path_b}\n"
            f"  First diff at char {pos}"
        )


def assert_file_unchanged(path, before_content):
    """Assert a file's content has not changed (line-ending normalized)."""
    after = read_file(path)
    if normalize(after) != normalize(before_content):
        raise AssertionError(f"File was modified: {path}")


def assert_file_empty(path):
    """Assert a file exists and contains only whitespace or nothing."""
    content = read_file(path)
    if content.strip():
        raise AssertionError(
            f"Expected empty file: {path} — got: {content[:50]!r}"
        )


# ---------- Text assertions ----------


def assert_text_contains(text, expected):
    if expected not in text:
        raise AssertionError(f"Text does not contain: {expected!r}")


def assert_returncode(result, expected=0):
    """Assert subprocess exit code, surfacing stderr on failure."""
    if result.returncode != expected:
        stderr_preview = (result.stderr or "")[:200]
        raise AssertionError(
            f"Expected exit code {expected}, got {result.returncode}\n"
            f"  stderr: {stderr_preview}"
        )


# ---------- Installer output assertions ----------
# These check BOTH the category label AND the glyph+path line.
# install.py output format:
#   Created:
#     + .claude/skills/vibe-start/SKILL.md
#   Updated (skills refreshed):
#     ~ .claude/skills/vibe-start/SKILL.md
#   Unchanged (skills already up to date):
#     = .claude/skills/vibe-start/SKILL.md
#   Preserved (your data, not touched):
#     - PROJECT_CONTEXT.md


def assert_created_report(output, path_fragment):
    _assert_category_line(output, "Created", "+", path_fragment)


def assert_updated_report(output, path_fragment):
    _assert_category_line(output, "Updated", "~", path_fragment)


def assert_unchanged_report(output, path_fragment):
    _assert_category_line(output, "Unchanged", "=", path_fragment)


def assert_preserved_report(output, path_fragment):
    _assert_category_line(output, "Preserved", "-", path_fragment)


def _assert_category_line(output, category_label, glyph, path_fragment):
    """Check output contains both a category header and a glyph+path line."""
    norm = normalize(output)
    if category_label.lower() not in norm.lower():
        raise AssertionError(
            f"Installer output missing '{category_label}' category"
        )
    marker = f"{glyph} {path_fragment}"
    if marker not in norm:
        # Try with OS-native path separators (Windows backslash)
        marker_win = f"{glyph} {path_fragment.replace('/', os.sep)}"
        if marker_win not in norm:
            raise AssertionError(
                f"Installer output missing '{glyph} {path_fragment}' "
                f"under '{category_label}'"
            )


# ---------- Internal helpers ----------


def _first_diff(a, b):
    """Return the character position of the first difference."""
    for i, (ca, cb) in enumerate(zip(a, b)):
        if ca != cb:
            return i
    return min(len(a), len(b))
