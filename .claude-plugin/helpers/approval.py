#!/usr/bin/env python3
"""
VibeCode OS — command approval helpers (008+)
Manages .claude/approved_commands.json for first-run command approval.
Python 3.8+, stdlib only.
"""

import hashlib
import json
import os
import time

from context import atomic_write

SCHEMA_VERSION = 1


def _compute_cmd_hash(cmd: str) -> str:
    """SHA-256 of the normalized command string."""
    return hashlib.sha256(cmd.strip().encode("utf-8")).hexdigest()


def _get_repo_id(root: str) -> str:
    """
    Compute a stable repo identity marker from the repo root path.
    Uses the directory name + parent name for portability.
    """
    abs_root = os.path.realpath(os.path.abspath(root))
    parts = abs_root.replace("\\", "/").rstrip("/").split("/")
    identity = "/".join(parts[-2:]) if len(parts) >= 2 else parts[-1]
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]


def _compute_file_checksum(records: list) -> str:
    """Compute a checksum over the commands array for tamper detection."""
    content = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def load_approvals(path: str) -> dict:
    """
    Load the approved commands JSON file.
    Returns a validated dict or an empty structure on any failure.
    """
    empty = {"schema_version": SCHEMA_VERSION, "commands": []}

    if not os.path.exists(path):
        return empty

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return empty

    # Validate schema
    if not isinstance(data, dict):
        return empty
    if data.get("schema_version") != SCHEMA_VERSION:
        return empty
    if not isinstance(data.get("commands"), list):
        return empty

    # Validate checksum
    stored_checksum = data.get("checksum", "")
    expected_checksum = _compute_file_checksum(data["commands"])
    if stored_checksum and stored_checksum != expected_checksum:
        # Tamper detected — treat as empty, require re-approval
        return empty

    return data


def is_approved(cmd: str, root: str, approvals: dict) -> bool:
    """
    Return True if the command is approved for this repo.
    Re-prompts (returns False) if: command changed, repo identity changed,
    approval missing, or approval file was invalid.
    """
    cmd_hash = _compute_cmd_hash(cmd)
    repo_id = _get_repo_id(root)

    for record in approvals.get("commands", []):
        if (record.get("cmd_hash") == cmd_hash and
                record.get("repo_id") == repo_id):
            return True
    return False


def add_approval(cmd: str, root: str, approvals: dict) -> dict:
    """
    Add an approval record for the given command and repo.
    Returns the updated approvals dict (does not write to disk).
    """
    cmd_hash = _compute_cmd_hash(cmd)
    repo_id = _get_repo_id(root)

    new_record = {
        "cmd": cmd.strip(),
        "cmd_hash": cmd_hash,
        "repo_id": repo_id,
        "approved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "last_used_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "denied_count": 0,
    }

    commands = approvals.get("commands", [])
    # Remove any existing record for this command+repo (replace, don't duplicate)
    commands = [r for r in commands
                if not (r.get("cmd_hash") == cmd_hash and r.get("repo_id") == repo_id)]
    commands.append(new_record)

    updated = {
        "schema_version": SCHEMA_VERSION,
        "commands": commands,
    }
    updated["checksum"] = _compute_file_checksum(commands)
    return updated


def record_denial(cmd: str, root: str, approvals: dict) -> dict:
    """Increment denied_count for a command. Returns updated dict."""
    cmd_hash = _compute_cmd_hash(cmd)
    repo_id = _get_repo_id(root)

    commands = approvals.get("commands", [])
    for record in commands:
        if (record.get("cmd_hash") == cmd_hash and
                record.get("repo_id") == repo_id):
            record["denied_count"] = record.get("denied_count", 0) + 1
            break

    updated = dict(approvals)
    updated["commands"] = commands
    updated["checksum"] = _compute_file_checksum(commands)
    return updated


def save_approvals(path: str, approvals: dict) -> None:
    """
    Write the approvals dict to disk atomically.
    Creates parent directory if needed.
    """
    content = json.dumps(approvals, indent=2, ensure_ascii=False)
    atomic_write(path, content + "\n")


def validate_approval_file(path: str) -> tuple:
    """
    Validate the approval file structure.
    Returns (is_valid: bool, reason: str).
    """
    if not os.path.exists(path):
        return False, "File does not exist"

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except OSError as e:
        return False, f"Cannot read file: {e}"

    if not isinstance(data, dict):
        return False, "Root must be a JSON object"
    if "schema_version" not in data:
        return False, "Missing schema_version"
    if data["schema_version"] != SCHEMA_VERSION:
        return False, f"Unknown schema_version: {data['schema_version']}"
    if "commands" not in data:
        return False, "Missing commands array"
    if not isinstance(data["commands"], list):
        return False, "commands must be an array"

    return True, "Valid"
