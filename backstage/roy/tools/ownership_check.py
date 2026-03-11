#!/usr/bin/env python3
"""
Ownership Check Tool
Author: Roy
Date: 2026-03-08

People don't read instructions, so this script verifies that no one is modifying files outside of their own backstage directories. It checks git diff for the current branch.
"""
import subprocess
import sys
import re

def get_changed_files():
    try:
        # Check files changed against main
        result = subprocess.run(
            ["git", "diff", "--name-only", "main...HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error checking git diff: {e}")
        return []

def extract_actor_from_branch():
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()
        # Branches usually format like `roy-round-30` or just contain the actor name
        match = re.match(r'^([a-zA-Z]+)-?', branch)
        if match:
            return match.group(1).lower()
        return branch
    except subprocess.CalledProcessError:
        return "unknown"

def check_ownership(files, current_actor):
    violations = []
    for file in files:
        if not file:
            continue

        # All characters must write in backstage/{actor}/
        if file.startswith('backstage/'):
            parts = file.split('/')
            if len(parts) > 1:
                owner = parts[1]
                if owner != current_actor and owner not in ['STATE.md']:
                    # Exception: updating STATE.md is allowed for certain roles
                    violations.append(f"File {file} belongs to {owner}, modified by {current_actor}")
        elif file.startswith('sessions/'):
            # Only Franklin should edit sessions directly, others read
            if current_actor != 'franklin':
                 violations.append(f"File {file} modified by {current_actor}. Only Franklin modifies sessions.")

    return violations

if __name__ == "__main__":
    files = get_changed_files()
    actor = extract_actor_from_branch()

    print(f"Checking ownership for actor: {actor}")
    print(f"Files modified: {len([f for f in files if f])}")

    violations = check_ownership(files, actor)

    if violations:
        print("\nOWNERSHIP VIOLATIONS DETECTED:")
        for v in violations:
            print(f"- {v}")
        sys.exit(1)
    else:
        print("\nAll files follow ownership rules.")
        sys.exit(0)
