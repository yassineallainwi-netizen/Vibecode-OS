#!/usr/bin/env python3
"""
VibeCode OS Installer
Copies skills and templates into the current repo.
Python 3.8+, stdlib only.

Usage:
    python install.py            # standalone mode (default)
    python install.py --plugin   # standalone + official plugin
    python install.py --rollback # remove plugin, keep standalone
"""

import argparse
import os
import shutil
import sys


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def install_standalone(target, src_dir, created, updated, unchanged, preserved):
    """Install standalone .claude/skills/ mode (always runs)."""
    # 1. Create .claude/skills/ directory
    skills_target = os.path.join(target, ".claude", "skills")
    os.makedirs(skills_target, exist_ok=True)

    # 2. Managed skill files — update if content differs, skip if identical
    skills_src = os.path.join(src_dir, "src", "skills")
    skill_names = ["vibe-start", "vibe-resume", "vibe-status", "vibe-done"]

    for skill_name in skill_names:
        skill_src_dir = os.path.join(skills_src, skill_name)
        skill_target_dir = os.path.join(skills_target, skill_name)
        skill_file = os.path.join(skill_target_dir, "SKILL.md")
        src_file = os.path.join(skill_src_dir, "SKILL.md")
        label = f".claude/skills/{skill_name}/SKILL.md"

        os.makedirs(skill_target_dir, exist_ok=True)

        if not os.path.exists(skill_file):
            shutil.copy2(src_file, skill_file)
            created.append(label)
        else:
            src_content = read_file(src_file)
            dst_content = read_file(skill_file)
            if src_content != dst_content:
                shutil.copy2(src_file, skill_file)
                updated.append(label)
            else:
                unchanged.append(label)

    # 3. User data files — never overwrite
    templates_src = os.path.join(src_dir, "src", "templates")
    template_files = [
        "PROJECT_CONTEXT.md",
        "AGENTS.md",
        "DECISIONS.md",
        "SESSION_LOG.md",
    ]

    for filename in template_files:
        target_path = os.path.join(target, filename)
        if os.path.exists(target_path):
            preserved.append(filename)
        else:
            shutil.copy2(os.path.join(templates_src, filename), target_path)
            created.append(filename)

    # 4. Create features/ directory (user data — never overwrite)
    features_dir = os.path.join(target, "features")
    if not os.path.isdir(features_dir):
        os.makedirs(features_dir)
        created.append("features/")
    else:
        preserved.append("features/")

    # 5. Create .claude/active_feature (user data — never overwrite)
    active_feature_path = os.path.join(target, ".claude", "active_feature")
    if not os.path.exists(active_feature_path):
        with open(active_feature_path, "w") as f:
            f.write("")
        created.append(".claude/active_feature")
    else:
        preserved.append(".claude/active_feature")

    # 6. Create .claude/approved_commands.json (user data — never overwrite)
    approved_commands_path = os.path.join(target, ".claude", "approved_commands.json")
    if not os.path.exists(approved_commands_path):
        with open(approved_commands_path, "w", encoding="utf-8") as f:
            f.write('{"schema_version": 1, "commands": [], "checksum": ""}\n')
        created.append(".claude/approved_commands.json")
    else:
        preserved.append(".claude/approved_commands.json")

    # 7. Create .claude/context/ directory (compact artifacts — created at runtime by skills)
    context_dir = os.path.join(target, ".claude", "context")
    if not os.path.isdir(context_dir):
        os.makedirs(context_dir)
        created.append(".claude/context/")
    else:
        preserved.append(".claude/context/")

    # 8. Create .claude/runtime/ directory (local runtime data — capability cache, etc.)
    runtime_dir = os.path.join(target, ".claude", "runtime")
    if not os.path.isdir(runtime_dir):
        os.makedirs(runtime_dir)
        created.append(".claude/runtime/")
    else:
        preserved.append(".claude/runtime/")

    # 9. Install SPEC.md template into .claude/templates/ — managed (update if differs)
    #    Skills read from .claude/templates/SPEC.md so it is available at runtime even
    #    when the VibeCode OS source directory is not present in the installed repo.
    templates_runtime_dir = os.path.join(target, ".claude", "templates")
    os.makedirs(templates_runtime_dir, exist_ok=True)
    spec_src = os.path.join(src_dir, "src", "templates", "SPEC.md")
    spec_dst = os.path.join(templates_runtime_dir, "SPEC.md")
    if os.path.exists(spec_src):
        label = ".claude/templates/SPEC.md"
        if not os.path.exists(spec_dst):
            shutil.copy2(spec_src, spec_dst)
            created.append(label)
        else:
            if read_file(spec_src) != read_file(spec_dst):
                shutil.copy2(spec_src, spec_dst)
                updated.append(label)
            else:
                unchanged.append(label)


def install_plugin(target, src_dir, created, updated, unchanged):
    """Install official Claude Code plugin to .claude-plugin/ (alongside standalone)."""
    plugin_target = os.path.join(target, ".claude-plugin")
    plugin_src = os.path.join(src_dir, ".claude-plugin")

    if not os.path.isdir(plugin_src):
        print("[Warning] .claude-plugin/ source not found — plugin install skipped.")
        return

    # plugin.json — managed (update if differs)
    plugin_json_src = os.path.join(plugin_src, "plugin.json")
    plugin_json_dst = os.path.join(plugin_target, "plugin.json")
    os.makedirs(plugin_target, exist_ok=True)
    if not os.path.exists(plugin_json_dst):
        shutil.copy2(plugin_json_src, plugin_json_dst)
        created.append(".claude-plugin/plugin.json")
    else:
        if read_file(plugin_json_src) != read_file(plugin_json_dst):
            shutil.copy2(plugin_json_src, plugin_json_dst)
            updated.append(".claude-plugin/plugin.json")
        else:
            unchanged.append(".claude-plugin/plugin.json")

    # skills/ — managed (update if differs), mirror from src/skills/
    skills_src = os.path.join(src_dir, "src", "skills")
    skills_plugin_dir = os.path.join(plugin_target, "skills")
    skill_names = ["vibe-start", "vibe-resume", "vibe-status", "vibe-done"]
    for skill_name in skill_names:
        src_file = os.path.join(skills_src, skill_name, "SKILL.md")
        dst_dir = os.path.join(skills_plugin_dir, skill_name)
        dst_file = os.path.join(dst_dir, "SKILL.md")
        label = f".claude-plugin/skills/{skill_name}/SKILL.md"
        os.makedirs(dst_dir, exist_ok=True)
        if not os.path.exists(dst_file):
            shutil.copy2(src_file, dst_file)
            created.append(label)
        elif read_file(src_file) != read_file(dst_file):
            shutil.copy2(src_file, dst_file)
            updated.append(label)
        else:
            unchanged.append(label)

    # helpers/ — managed (update if differs), mirror from src/helpers/
    helpers_src = os.path.join(src_dir, "src", "helpers")
    helpers_plugin_dir = os.path.join(plugin_target, "helpers")
    os.makedirs(helpers_plugin_dir, exist_ok=True)
    helper_files = ["context.py", "claude_md.py", "verification.py", "approval.py", "compaction.py"]
    for filename in helper_files:
        src_file = os.path.join(helpers_src, filename)
        dst_file = os.path.join(helpers_plugin_dir, filename)
        label = f".claude-plugin/helpers/{filename}"
        if not os.path.exists(src_file):
            continue
        if not os.path.exists(dst_file):
            shutil.copy2(src_file, dst_file)
            created.append(label)
        elif read_file(src_file) != read_file(dst_file):
            shutil.copy2(src_file, dst_file)
            updated.append(label)
        else:
            unchanged.append(label)

    # hooks/hooks.json — managed
    hooks_src = os.path.join(plugin_src, "hooks", "hooks.json")
    hooks_dir = os.path.join(plugin_target, "hooks")
    hooks_dst = os.path.join(hooks_dir, "hooks.json")
    os.makedirs(hooks_dir, exist_ok=True)
    if os.path.exists(hooks_src):
        if not os.path.exists(hooks_dst):
            shutil.copy2(hooks_src, hooks_dst)
            created.append(".claude-plugin/hooks/hooks.json")
        elif read_file(hooks_src) != read_file(hooks_dst):
            shutil.copy2(hooks_src, hooks_dst)
            updated.append(".claude-plugin/hooks/hooks.json")
        else:
            unchanged.append(".claude-plugin/hooks/hooks.json")


def rollback_plugin(target, removed):
    """Remove .claude-plugin/ directory, restoring standalone-only state."""
    plugin_dir = os.path.join(target, ".claude-plugin")
    if os.path.isdir(plugin_dir):
        shutil.rmtree(plugin_dir)
        removed.append(".claude-plugin/")
    else:
        print("  (no .claude-plugin/ to remove — already in standalone mode)")


def main():
    parser = argparse.ArgumentParser(
        description="VibeCode OS installer",
        add_help=True,
    )
    parser.add_argument(
        "--plugin",
        action="store_true",
        help="Also install official Claude Code plugin to .claude-plugin/ (alongside standalone)",
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Remove .claude-plugin/ and restore standalone-only state",
    )
    args = parser.parse_args()

    target = os.getcwd()
    src_dir = os.path.dirname(os.path.abspath(__file__))

    print("VibeCode OS Installer")
    print("=" * 40)
    print(f"Installing into: {target}")
    if args.plugin:
        print("Mode: standalone + plugin")
    elif args.rollback:
        print("Mode: rollback (remove plugin, keep standalone)")
    else:
        print("Mode: standalone")
    print()

    # Warn if not a git repo (don't block)
    if not os.path.isdir(os.path.join(target, ".git")):
        print("[Warning] This directory is not a git repo. That's fine, but git is recommended.")
        print()

    created = []
    updated = []
    unchanged = []
    preserved = []
    removed = []

    # Rollback: remove plugin, still install/update standalone
    if args.rollback:
        rollback_plugin(target, removed)

    # Always install standalone mode
    install_standalone(target, src_dir, created, updated, unchanged, preserved)

    # Plugin mode: install alongside standalone
    if args.plugin and not args.rollback:
        install_plugin(target, src_dir, created, updated, unchanged)

    # Report
    if removed:
        print("Removed:")
        for item in removed:
            print(f"  - {item}")
        print()

    if created:
        print("Created:")
        for item in created:
            print(f"  + {item}")
        print()

    if updated:
        print("Updated (skills refreshed):")
        for item in updated:
            print(f"  ~ {item}")
        print()

    if unchanged:
        print("Unchanged (skills already up to date):")
        for item in unchanged:
            print(f"  = {item}")
        print()

    if preserved:
        print("Preserved (your data, not touched):")
        for item in preserved:
            print(f"  - {item}")
        print()

    if not any([created, updated, removed]):
        print("  (nothing to do — skills up to date, user data preserved)")
        print()

    print("VibeCode OS installed.")
    if args.rollback:
        print("Plugin removed. Standalone .claude/skills/ mode is active.")
    elif args.plugin:
        print('Plugin installed. Both .claude-plugin/ and .claude/skills/ are active.')
        print('See docs/plugin_migration.md for coexistence rules.')
    else:
        print('Start with "/vibe-resume" to set up your project,')
        print('or "/vibe-start" to begin your first feature.')


if __name__ == "__main__":
    main()
