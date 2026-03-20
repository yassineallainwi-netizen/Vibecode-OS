#!/usr/bin/env python3
"""
VibeCode OS — capability probing (010)
Detects available host capabilities with timeout and local caching.
Python 3.8+, stdlib only.
"""

import json
import os
import time

CAPABILITY_CACHE_PATH = os.path.join(".claude", "runtime", "capability_cache.json")
PROBE_TIMEOUT_MS = 500
CACHE_TTL_HOURS = 24

KNOWN_CAPABILITIES = [
    "file_read",
    "file_write",
    "command_exec",
    "settings_surface",
    "rich_rendering",
]


def _cache_path(root: str) -> str:
    return os.path.join(root, ".claude", "runtime", "capability_cache.json")


def _load_cache(root: str) -> dict:
    path = _cache_path(root)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        # Check TTL
        cached_at = data.get("cached_at", "")
        if cached_at:
            try:
                ts_clean = cached_at.rstrip("Z").replace("T", " ")
                t = time.strptime(ts_clean, "%Y-%m-%d %H:%M:%S")
                age_hours = (time.time() - time.mktime(t)) / 3600
                if age_hours > CACHE_TTL_HOURS:
                    return {}
            except (ValueError, TypeError):
                return {}
        return data
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(root: str, capabilities: dict) -> None:
    path = _cache_path(root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = dict(capabilities)
    payload["cached_at"] = now
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except OSError:
        pass  # Cache failure is non-fatal


def _probe_file_read(root: str) -> bool:
    """Check if file reading works within the project root."""
    try:
        test_path = os.path.join(root, ".claude", "active_feature")
        if os.path.exists(test_path):
            with open(test_path, "r", encoding="utf-8") as f:
                f.read(100)
        return True
    except OSError:
        return False


def _probe_file_write(root: str) -> bool:
    """Check if writing to .claude/runtime/ works."""
    try:
        test_path = os.path.join(root, ".claude", "runtime", ".write_probe")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("")
        os.remove(test_path)
        return True
    except OSError:
        return False


def _probe_command_exec() -> bool:
    """Check if subprocess execution is available."""
    import subprocess
    try:
        result = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            timeout=2,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def probe_capabilities(root: str = ".", timeout_ms: int = PROBE_TIMEOUT_MS) -> dict:
    """
    Detect available host capabilities. Returns capability dict.
    Timeboxed at timeout_ms. Caches result locally for CACHE_TTL_HOURS.

    Returns:
        {
            "file_read": bool,
            "file_write": bool,
            "command_exec": bool,
            "settings_surface": bool,
            "rich_rendering": bool,
            "cached_at": str,
            "probe_duration_ms": float,
            "unsupported": [list of missing required caps],
        }
    """
    # Check cache first
    cached = _load_cache(root)
    if cached and "file_read" in cached:
        return cached

    start = time.time()
    capabilities = {}

    # Probe within timeout budget
    try:
        capabilities["file_read"] = _probe_file_read(root)
    except Exception:
        capabilities["file_read"] = False

    if (time.time() - start) * 1000 < timeout_ms:
        try:
            capabilities["file_write"] = _probe_file_write(root)
        except Exception:
            capabilities["file_write"] = False
    else:
        capabilities["file_write"] = False

    if (time.time() - start) * 1000 < timeout_ms:
        try:
            capabilities["command_exec"] = _probe_command_exec()
        except Exception:
            capabilities["command_exec"] = False
    else:
        capabilities["command_exec"] = False

    # Settings surface and rich rendering are environment-detected, not probeable
    capabilities["settings_surface"] = False
    capabilities["rich_rendering"] = False

    capabilities["probe_duration_ms"] = round((time.time() - start) * 1000, 1)

    # Compute unsupported required capabilities
    required = ["file_read", "file_write"]
    capabilities["unsupported"] = [c for c in required if not capabilities.get(c, False)]

    _save_cache(root, capabilities)
    return capabilities


def emit_capability_manifest(capabilities: dict) -> str:
    """Return a compact human-readable capability summary."""
    lines = ["**Capability manifest:**"]
    for cap in KNOWN_CAPABILITIES:
        status = "available" if capabilities.get(cap) else "unavailable"
        lines.append(f"- {cap}: {status}")
    unsupported = capabilities.get("unsupported", [])
    if unsupported:
        lines.append(f"\n**Missing required capabilities:** {', '.join(unsupported)}")
        lines.append("Fallback: standalone `.claude/skills` mode")
    return "\n".join(lines)
