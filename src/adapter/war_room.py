#!/usr/bin/env python3
"""
VibeCode OS — War Room manifest (010)
Stable payload contract across plugin, standalone, and future hosts.
Python 3.8+, stdlib only.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class WarRoomManifest:
    """
    Stable War Room payload. All fields are optional strings or lists.
    Hosts render this as text, rich UI, or any other format.
    """
    project: str = ""
    project_rules: str = ""
    mode: str = ""                  # building / verifying / closing / idle
    risk_flags: List[str] = field(default_factory=list)
    current_state: str = ""
    active_feature: str = ""
    git_branch: str = ""
    git_clean: Optional[bool] = None
    recent_files: List[str] = field(default_factory=list)
    last_hard_problem: str = ""
    next_file: str = ""
    next_action: str = ""
    context_pointer: str = ""
    verification_readiness: str = ""   # ready / degraded / none
    verification_strength: str = ""    # high / medium / low / none
    verification_last_cmd: str = ""
    verification_freshness: str = ""   # fresh / reused / stale / missing
    verification_blocker: str = ""
    verification_next_action: str = ""
    context_source: str = ""           # compact_ready / mixed / full_scan_required
    reconstruction_reason: str = ""
    complexity: str = ""               # trivial / normal / complex / high-risk
    # Novice-only (set only when maturity score 0-2)
    why_safe: str = ""
    first_file_to_open: str = ""


def render_as_text(manifest: WarRoomManifest) -> str:
    """
    Render a WarRoomManifest as a markdown blockquote string.
    Omits fields that are empty or None.
    This is the default host-agnostic text renderer.
    """
    lines = []

    def add(label: str, value: str) -> None:
        if value and value.strip():
            lines.append(f"> **{label}:** {value}")

    def add_list(label: str, items: List[str]) -> None:
        if items:
            lines.append(f"> **{label}:** {', '.join(items)}")

    add("Project", manifest.project)
    add("Project rules", manifest.project_rules)
    add("Mode", manifest.mode)
    add_list("Risk flags", manifest.risk_flags)
    add("Current state", manifest.current_state)
    add("Active feature", manifest.active_feature)

    if manifest.git_branch:
        clean_str = "clean" if manifest.git_clean else "dirty" if manifest.git_clean is False else "unknown"
        add("Git", f"{manifest.git_branch} — {clean_str}")

    add_list("Recent files", manifest.recent_files)
    add("Last hard problem solved", manifest.last_hard_problem)
    add("Next file to edit", manifest.next_file)
    add("Next concrete code action", manifest.next_action)
    add("Context pointer", manifest.context_pointer)

    # Verification line
    verification_parts = []
    if manifest.verification_readiness:
        verification_parts.append(manifest.verification_readiness)
    if manifest.verification_strength:
        verification_parts.append(manifest.verification_strength)
    if manifest.verification_last_cmd:
        verification_parts.append(manifest.verification_last_cmd)
    if manifest.verification_freshness:
        verification_parts.append(manifest.verification_freshness)
    if manifest.verification_blocker:
        verification_parts.append(manifest.verification_blocker)
    if manifest.verification_next_action:
        verification_parts.append(manifest.verification_next_action)
    if verification_parts:
        lines.append(f"> **Verification:** {' | '.join(verification_parts)}")

    # Context source line
    if manifest.context_source:
        ctx_line = manifest.context_source
        if manifest.reconstruction_reason:
            ctx_line += f" — {manifest.reconstruction_reason}"
        add("Context source", ctx_line)

    add("Complexity", manifest.complexity)

    # Novice-only fields
    if manifest.why_safe:
        lines.append(">")
        add("Why this is safe to start", manifest.why_safe)
    if manifest.first_file_to_open:
        add("First file to open", manifest.first_file_to_open)

    return "\n".join(lines)
