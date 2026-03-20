#!/usr/bin/env python3
"""
VibeCode OS — stable workflow actions (010)
8 host-agnostic workflow actions. Semantics are stable across plugin/standalone/future hosts.
Host adapters map UI affordances to these actions. All outputs are representable as text.
Python 3.8+, stdlib only.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ActionResult:
    """Uniform return type for all actions."""
    success: bool
    action: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    next_step: str = ""
    error: str = ""


def start_feature(root: str, title: str, description: str = "") -> ActionResult:
    """
    Start a new feature: validate preconditions, return scaffolding intent.
    Does not write files — skills handle writes. Returns what should be created.
    """
    import re
    import os

    active_path = os.path.join(root, ".claude", "active_feature")
    active = ""
    if os.path.exists(active_path):
        raw = open(active_path, "r", encoding="utf-8").read().strip()
        if re.match(r"^FEATURE-\d{3}-[a-z0-9-]+$", raw):
            active = raw

    if active:
        return ActionResult(
            success=False,
            action="start_feature",
            message=f"Active feature exists: {active}",
            data={"active_feature": active},
            next_step="Close the active feature with /vibe-done, or use 'override' to force.",
            error="active_feature_conflict",
        )

    return ActionResult(
        success=True,
        action="start_feature",
        message=f"Ready to start feature: {title}",
        data={"title": title, "description": description, "active": active},
        next_step="Run /vibe-start to create the spec.",
    )


def resume_work(root: str) -> ActionResult:
    """
    Resume work: check compact artifacts, return context source.
    """
    import sys
    import os
    sys.path.insert(0, os.path.join(root, "src", "helpers"))
    try:
        from compaction import get_context_source, read_project_state
        import re
        active_path = os.path.join(root, ".claude", "active_feature")
        active = ""
        if os.path.exists(active_path):
            raw = open(active_path, "r", encoding="utf-8").read().strip()
            if re.match(r"^FEATURE-\d{3}-[a-z0-9-]+$", raw):
                active = raw
        context_source = get_context_source(root, active if active else None)
        state = read_project_state(root)
        return ActionResult(
            success=True,
            action="resume_work",
            message=f"Context source: {context_source}",
            data={"context_source": context_source, "active_feature": active, "project_state": state},
            next_step="Run /vibe-resume to see the full War Room manifest.",
        )
    except ImportError:
        return ActionResult(
            success=True,
            action="resume_work",
            message="Context source: full_scan_required (helpers unavailable)",
            data={"context_source": "full_scan_required"},
            next_step="Run /vibe-resume to see the full War Room manifest.",
        )


def show_status(root: str) -> ActionResult:
    """
    Show current feature status summary.
    """
    import os
    import re
    active_path = os.path.join(root, ".claude", "active_feature")
    active = ""
    if os.path.exists(active_path):
        raw = open(active_path, "r", encoding="utf-8").read().strip()
        if re.match(r"^FEATURE-\d{3}-[a-z0-9-]+$", raw):
            active = raw

    if not active:
        return ActionResult(
            success=True,
            action="show_status",
            message="No active feature",
            data={"active_feature": ""},
            next_step="Run /vibe-start to begin a feature.",
        )

    spec_path = os.path.join(root, "features", active, "SPEC.md")
    verify_path = os.path.join(root, "features", active, "VERIFY.md")
    has_spec = os.path.exists(spec_path)
    has_verify = os.path.exists(verify_path)
    mode = "building" if not has_verify else "verifying"

    return ActionResult(
        success=True,
        action="show_status",
        message=f"Active: {active} — {mode}",
        data={"active_feature": active, "has_spec": has_spec, "has_verify": has_verify, "mode": mode},
        next_step="Run /vibe-status for the full progress report.",
    )


def close_feature(root: str, force: bool = False) -> ActionResult:
    """
    Close the active feature: check preconditions, return close intent.
    """
    import os
    import re
    active_path = os.path.join(root, ".claude", "active_feature")
    active = ""
    if os.path.exists(active_path):
        raw = open(active_path, "r", encoding="utf-8").read().strip()
        if re.match(r"^FEATURE-\d{3}-[a-z0-9-]+$", raw):
            active = raw

    if not active:
        return ActionResult(
            success=False,
            action="close_feature",
            message="No active feature to close.",
            next_step="Run /vibe-start to begin a feature.",
            error="no_active_feature",
        )

    return ActionResult(
        success=True,
        action="close_feature",
        message=f"Ready to close: {active}{'(force)' if force else ''}",
        data={"active_feature": active, "force": force},
        next_step="Run /vibe-done to verify and close the feature.",
    )


def verify_state(root: str) -> ActionResult:
    """
    Verify compact artifacts and active state integrity.
    """
    import sys
    import os
    sys.path.insert(0, os.path.join(root, "src", "helpers"))
    try:
        from compaction import read_project_state, is_stale
        state = read_project_state(root)
        if state is None:
            return ActionResult(
                success=True,
                action="verify_state",
                message="No valid compact artifacts found",
                data={"artifacts_valid": False},
                next_step="Run /vibe-done to generate compact artifacts.",
            )
        stale = is_stale(state)
        return ActionResult(
            success=True,
            action="verify_state",
            message="Compact artifacts valid" + (" (stale)" if stale else " (fresh)"),
            data={"artifacts_valid": True, "stale": stale, "last_compacted": state.get("last_compacted", "")},
            next_step="Run /vibe-resume to load context." if not stale else "Artifacts stale — /vibe-resume will reconstruct.",
        )
    except ImportError:
        return ActionResult(
            success=False,
            action="verify_state",
            message="Compaction helpers unavailable",
            error="helpers_unavailable",
        )


def compact_context(root: str) -> ActionResult:
    """
    Trigger compaction of project state to .claude/context/.
    """
    import sys
    import os
    sys.path.insert(0, os.path.join(root, "src", "helpers"))
    try:
        from compaction import write_project_state, read_project_state
        existing = read_project_state(root) or {}
        write_project_state(root, existing)
        return ActionResult(
            success=True,
            action="compact_context",
            message="Compact artifacts written to .claude/context/",
            data={"path": os.path.join(root, ".claude", "context", "project_state.json")},
            next_step="Run /vibe-resume to use compact context.",
        )
    except Exception as e:
        return ActionResult(
            success=False,
            action="compact_context",
            message="Compaction failed — standalone files remain authoritative",
            error=str(e),
            next_step="Run /vibe-resume for full file scan.",
        )


def recover_active_feature(root: str) -> ActionResult:
    """
    Detect and recover from broken active_feature state.
    """
    import os
    import re
    active_path = os.path.join(root, ".claude", "active_feature")

    if not os.path.exists(active_path):
        return ActionResult(
            success=True,
            action="recover_active_feature",
            message="No active_feature file — clean state",
            next_step="Run /vibe-start to begin a feature.",
        )

    raw = open(active_path, "r", encoding="utf-8").read().strip()
    if not raw:
        return ActionResult(
            success=True,
            action="recover_active_feature",
            message="active_feature is empty — clean state",
            next_step="Run /vibe-start to begin a feature.",
        )

    if not re.match(r"^FEATURE-\d{3}-[a-z0-9-]+$", raw):
        # Clear malformed value
        with open(active_path, "w", encoding="utf-8") as f:
            f.write("")
        return ActionResult(
            success=True,
            action="recover_active_feature",
            message=f"Cleared malformed active_feature: {raw!r}",
            data={"cleared": raw},
            next_step="Run /vibe-resume to scan for features.",
        )

    feature_dir = os.path.join(root, "features", raw)
    if not os.path.isdir(feature_dir):
        with open(active_path, "w", encoding="utf-8") as f:
            f.write("")
        return ActionResult(
            success=True,
            action="recover_active_feature",
            message=f"Cleared broken reference: {raw} (directory not found)",
            data={"cleared": raw},
            next_step="Run /vibe-resume to scan for features.",
        )

    return ActionResult(
        success=True,
        action="recover_active_feature",
        message=f"active_feature is valid: {raw}",
        data={"active_feature": raw},
        next_step="Run /vibe-resume to continue work.",
    )


def draft_commit_suggestion(root: str, feature_id: str, spec_title: str, changed_files: list) -> ActionResult:
    """
    Draft a Git Ghost commit suggestion. Never executes git.
    """
    import re
    # Sanitize feature_id for commit message
    safe_id = re.sub(r"[^a-zA-Z0-9._/-]", "", feature_id)
    # Derive prefix
    prefix = "fix:" if any(w in spec_title.lower() for w in ("fix", "repair", "bug", "patch")) else "feat:"
    # Build subject, max 72 chars
    subject = f"{prefix} {safe_id} {spec_title}"
    if len(subject) > 72:
        max_title_len = 72 - len(f"{prefix} {safe_id} ")
        subject = f"{prefix} {safe_id} {spec_title[:max_title_len]}"

    changed_str = " ".join(changed_files[:5]) if changed_files else ""
    body = f"git add -A && git commit -m \"{subject}\""

    return ActionResult(
        success=True,
        action="draft_commit_suggestion",
        message=subject,
        data={
            "subject": subject,
            "command": body,
            "changed_files": changed_files,
        },
        next_step="Copy and run the git command yourself — VibeCode never executes git.",
    )
