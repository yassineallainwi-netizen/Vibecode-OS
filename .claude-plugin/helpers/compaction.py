#!/usr/bin/env python3
"""
VibeCode OS — compaction helpers (009+)
Manages .claude/context/ compact artifacts for token-efficient session resumption.
Skills write JSON directly; this module provides schema validation, atomic I/O,
delta computation, and staleness checks.
Python 3.8+, stdlib only.
"""

import calendar
import hashlib
import json
import os
import re
import time
from typing import Optional

from context import atomic_write

SCHEMA_VERSION = 1
GENERATOR_VERSION = "009"
STALE_HOURS = 24


# ---------- Schema definitions ----------

PROJECT_STATE_REQUIRED = [
    "schema_version", "generator_version", "project", "active_feature",
    "workflow_mode", "risk_flags", "verification_readiness",
    "last_completed_feature", "recent_files", "command_registry",
    "last_compacted", "created_at", "updated_at", "derived_from",
]

FEATURE_STATE_REQUIRED = [
    "schema_version", "generator_version", "feature_id", "title", "status",
    "changed_files", "unresolved_items", "contextual_pointer",
    "evidence_grade", "commands_used", "verification_summary",
    "active_risks", "complexity", "checkpoint_id",
    "created_at", "updated_at", "derived_from",
]


# ---------- Schema validation ----------


def validate_schema(data: dict, required_fields: list) -> tuple:
    """
    Validate a compact artifact dict against required fields.
    Returns (is_valid: bool, reason: str).
    """
    if not isinstance(data, dict):
        return False, "Not a dict"
    if data.get("schema_version") != SCHEMA_VERSION:
        return False, f"schema_version mismatch: got {data.get('schema_version')!r}"
    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing fields: {missing}"
    return True, "OK"


def _compute_artifact_checksum(data: dict) -> str:
    """Compute checksum over artifact content (excluding the checksum field itself)."""
    d = {k: v for k, v in data.items() if k != "checksum"}
    content = json.dumps(d, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


# ---------- Project state ----------


def write_project_state(root: str, data: dict) -> tuple:
    """
    Write project_state.json atomically to .claude/context/.
    Adds schema metadata and checksum automatically.
    Returns (True, "ok") on success, (False, reason) on failure.
    Skills treat False as compact-path unavailable — never as a blocker.
    """
    path = os.path.join(root, ".claude", "context", "project_state.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    artifact = dict(data)
    artifact["schema_version"] = SCHEMA_VERSION
    artifact["generator_version"] = GENERATOR_VERSION
    artifact["updated_at"] = now
    if "created_at" not in artifact:
        artifact["created_at"] = now
    artifact["last_compacted"] = now

    # Ensure required fields have defaults
    artifact.setdefault("project", "")
    artifact.setdefault("active_feature", "")
    artifact.setdefault("workflow_mode", "idle")
    artifact.setdefault("risk_flags", [])
    artifact.setdefault("verification_readiness", "none")
    artifact.setdefault("last_completed_feature", "")
    artifact.setdefault("recent_files", [])
    artifact.setdefault("command_registry", {})
    artifact.setdefault("derived_from", "vibe-done")

    # Validate in memory before writing
    ok, reason = validate_schema(artifact, PROJECT_STATE_REQUIRED)
    if not ok:
        return False, f"In-memory validation failed: {reason}"

    artifact["checksum"] = _compute_artifact_checksum(artifact)
    content = json.dumps(artifact, indent=2, ensure_ascii=False) + "\n"

    def _post_write_validator(written: str) -> tuple:
        try:
            parsed = json.loads(written)
        except json.JSONDecodeError as exc:
            return False, f"JSON parse failed: {exc}"
        v_ok, v_reason = validate_schema(parsed, PROJECT_STATE_REQUIRED)
        if not v_ok:
            return False, f"Post-write schema invalid: {v_reason}"
        return True, "ok"

    try:
        atomic_write(path, content, validator=_post_write_validator)
    except Exception as exc:
        return False, str(exc)
    return True, "ok"


def read_project_state(root: str) -> Optional[dict]:
    """
    Read and validate project_state.json.
    Returns None on any failure (missing, corrupt, schema mismatch, checksum fail).
    """
    path = os.path.join(root, ".claude", "context", "project_state.json")
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    valid, reason = validate_schema(data, PROJECT_STATE_REQUIRED)
    if not valid:
        return None

    # Verify checksum
    stored = data.get("checksum", "")
    expected = _compute_artifact_checksum(data)
    if stored and stored != expected:
        return None

    return data


# ---------- Feature state ----------


def write_feature_state(root: str, feature_id: str, data: dict) -> tuple:
    """
    Write feature_FEATURE-NNN.json atomically to .claude/context/.
    Returns (True, "ok") on success, (False, reason) on failure.
    Skills treat False as compact-path unavailable — never as a blocker.
    """
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", feature_id)
    path = os.path.join(root, ".claude", "context", f"feature_{safe_id}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    artifact = dict(data)
    artifact["schema_version"] = SCHEMA_VERSION
    artifact["generator_version"] = GENERATOR_VERSION
    artifact["feature_id"] = feature_id
    artifact["updated_at"] = now
    if "created_at" not in artifact:
        artifact["created_at"] = now

    # Ensure required fields have defaults
    artifact.setdefault("title", "")
    artifact.setdefault("status", "open")
    artifact.setdefault("changed_files", [])
    artifact.setdefault("unresolved_items", [])
    artifact.setdefault("contextual_pointer", "")
    artifact.setdefault("evidence_grade", "none")
    artifact.setdefault("commands_used", [])
    artifact.setdefault("verification_summary", {})
    artifact.setdefault("active_risks", [])
    artifact.setdefault("complexity", "normal")
    artifact.setdefault("checkpoint_id", "")
    artifact.setdefault("derived_from", "vibe-done")

    # Validate in memory before writing
    ok, reason = validate_schema(artifact, FEATURE_STATE_REQUIRED)
    if not ok:
        return False, f"In-memory validation failed: {reason}"

    artifact["checksum"] = _compute_artifact_checksum(artifact)
    content = json.dumps(artifact, indent=2, ensure_ascii=False) + "\n"

    def _post_write_validator(written: str) -> tuple:
        try:
            parsed = json.loads(written)
        except json.JSONDecodeError as exc:
            return False, f"JSON parse failed: {exc}"
        v_ok, v_reason = validate_schema(parsed, FEATURE_STATE_REQUIRED)
        if not v_ok:
            return False, f"Post-write schema invalid: {v_reason}"
        return True, "ok"

    try:
        atomic_write(path, content, validator=_post_write_validator)
    except Exception as exc:
        return False, str(exc)
    return True, "ok"


def read_feature_state(root: str, feature_id: str) -> Optional[dict]:
    """Read and validate a feature compact artifact. Returns None on any failure."""
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", feature_id)
    path = os.path.join(root, ".claude", "context", f"feature_{safe_id}.json")
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    valid, reason = validate_schema(data, FEATURE_STATE_REQUIRED)
    if not valid:
        return None

    stored = data.get("checksum", "")
    expected = _compute_artifact_checksum(data)
    if stored and stored != expected:
        return None

    return data


# ---------- Staleness ----------


def is_stale(artifact: dict, max_age_hours: int = STALE_HOURS) -> bool:
    """
    Return True if the artifact is older than max_age_hours.
    Compares last_compacted or updated_at to current UTC time.
    """
    ts_str = artifact.get("last_compacted") or artifact.get("updated_at", "")
    if not ts_str:
        return True

    try:
        # Parse ISO-8601 UTC timestamp
        # Format: YYYY-MM-DDTHH:MM:SSZ
        ts_str_clean = ts_str.rstrip("Z").replace("T", " ")
        t = time.strptime(ts_str_clean, "%Y-%m-%d %H:%M:%S")
        # calendar.timegm treats t as UTC — no local-TZ distortion
        artifact_epoch = calendar.timegm(t)
        now_epoch = time.time()
        age_hours = (now_epoch - artifact_epoch) / 3600
        return age_hours > max_age_hours
    except (ValueError, TypeError):
        return True


def get_context_source(root: str, feature_id: str = None) -> str:
    """
    Determine the context source for /vibe-resume.
    Returns: 'compact_ready' | 'mixed' | 'full_scan_required'
    """
    ps = read_project_state(root)
    if ps is None:
        return "full_scan_required"
    if is_stale(ps):
        return "full_scan_required"

    if feature_id:
        fs = read_feature_state(root, feature_id)
        if fs is None:
            return "mixed"  # project state OK, feature state missing
        if is_stale(fs):
            return "mixed"

    return "compact_ready"


# ---------- Delta computation ----------


def compute_delta(old_state: dict, new_state: dict) -> dict:
    """
    Compute a minimal delta between two project state dicts.
    Returns a dict with only the changed fields.
    """
    if not old_state:
        return new_state

    delta = {}
    for key in new_state:
        old_val = old_state.get(key)
        new_val = new_state.get(key)
        if old_val != new_val:
            delta[key] = {"from": old_val, "to": new_val}
    return delta


# ---------- Log compression ----------


def dedupe_stack_traces(log_text: str, max_lines: int = 5) -> str:
    """
    Remove duplicate stack trace blocks from log output.
    Keeps only the first occurrence of each unique stack (by first max_lines lines).
    """
    if not log_text:
        return log_text

    # Split into blocks separated by blank lines
    blocks = re.split(r"\n{2,}", log_text.strip())
    seen_prefixes = set()
    unique_blocks = []

    for block in blocks:
        lines = block.strip().splitlines()
        prefix = "\n".join(lines[:max_lines])
        if prefix not in seen_prefixes:
            seen_prefixes.add(prefix)
            unique_blocks.append(block)

    return "\n\n".join(unique_blocks)
