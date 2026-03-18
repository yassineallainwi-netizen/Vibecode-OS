#!/usr/bin/env python3
"""
VibeCode OS Installer
Copies skills and templates into the current repo.
Python 3.8+, stdlib only.
"""

import os
import shutil
import sys


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
    skipped = []

    # 1. Create .claude/skills/ directory
    skills_target = os.path.join(target, ".claude", "skills")
    os.makedirs(skills_target, exist_ok=True)

    # 2. Copy skill directories
    skills_src = os.path.join(src_dir, "src", "skills")
    skill_names = ["vibe-start", "vibe-resume", "vibe-status", "vibe-done"]

    for skill_name in skill_names:
        skill_src_dir = os.path.join(skills_src, skill_name)
        skill_target_dir = os.path.join(skills_target, skill_name)
        skill_file = os.path.join(skill_target_dir, "SKILL.md")

        if os.path.exists(skill_file):
            skipped.append(f".claude/skills/{skill_name}/SKILL.md")
        else:
            os.makedirs(skill_target_dir, exist_ok=True)
            shutil.copy2(
                os.path.join(skill_src_dir, "SKILL.md"),
                skill_file,
            )
            created.append(f".claude/skills/{skill_name}/SKILL.md")

    # 3. Copy template files (never overwrite)
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
            skipped.append(filename)
        else:
            shutil.copy2(os.path.join(templates_src, filename), target_path)
            created.append(filename)

    # 4. Create features/ directory
    features_dir = os.path.join(target, "features")
    if not os.path.isdir(features_dir):
        os.makedirs(features_dir)
        created.append("features/")
    else:
        skipped.append("features/")

    # 5. Create .claude/active_feature (empty)
    active_feature_path = os.path.join(target, ".claude", "active_feature")
    if not os.path.exists(active_feature_path):
        with open(active_feature_path, "w") as f:
            f.write("")
        created.append(".claude/active_feature")
    else:
        skipped.append(".claude/active_feature")

    # Report
    print("Created:")
    if created:
        for item in created:
            print(f"  + {item}")
    else:
        print("  (nothing new — everything already exists)")

    if skipped:
        print()
        print("Skipped (already exist):")
        for item in skipped:
            print(f"  - {item}")

    print()
    print("VibeCode OS installed.")
    print('Start with "/vibe-resume" to set up your project,')
    print('or "/vibe-start" to begin your first feature.')


if __name__ == "__main__":
    main()
