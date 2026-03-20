#!/usr/bin/env python3
"""
VibeCode OS Installer
Copies skills and templates into the current repo.
Python 3.8+, stdlib only.
"""

import os
import shutil
import sys


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    target = os.getcwd()
    src_dir = os.path.dirname(os.path.abspath(__file__))

    print("VibeCode OS Installer")
    print("=" * 40)
    print(f"Installing into: {target}")
    print()

    # Warn if not a git repo (don't block)
    if not os.path.isdir(os.path.join(target, ".git")):
        print("[Warning] This directory is not a git repo. That's fine, but git is recommended.")
        print()

    created = []
    updated = []
    unchanged = []
    preserved = []

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

    # Report
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

    if not any([created, updated]):
        print("  (nothing to do — skills up to date, user data preserved)")
        print()

    print("VibeCode OS installed.")
    print('Start with "/vibe-resume" to set up your project,')
    print('or "/vibe-start" to begin your first feature.')


if __name__ == "__main__":
    main()
