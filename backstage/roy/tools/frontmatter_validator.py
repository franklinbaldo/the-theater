#!/usr/bin/env python3

import os
import re
import yaml
import sys

def check_frontmatter(filepath):
    """
    Checks if a markdown file has valid frontmatter.
    Valid frontmatter requires: title, author, type, date.
    Optional: session, tags.
    Author must be one of: franklin, claire, owen, leo, delta-v, stage-manager, nathan, alexis, roy.
    Type must be one of: scene, reaction, think, plan, hobby, rehearsal, log, interview, post, soul, session, rule.
    """
    basename = os.path.basename(filepath)
    if basename in ["README.md", "PROMPTBOOK.md", "JULES.md", "SOUL.md", "EXPERIENCE.md", "PLAN.md", "STATE.md"]:
        print(f"[SKIP] {filepath}: Exempt structural file.")
        return True

    with open(filepath, 'r') as f:
        content = f.read()

    match = re.match(r'^---\s*\n(.*?)\n---\s*(\n|$)', content, re.DOTALL)
    if not match:
        print(f"[FAIL] {filepath}: Missing or malformed frontmatter block.")
        return False

    yaml_content = match.group(1)

    try:
        data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        print(f"[FAIL] {filepath}: YAML parsing error: {e}")
        return False

    if not isinstance(data, dict):
        print(f"[FAIL] {filepath}: Frontmatter is not a valid YAML dictionary.")
        return False

    required_fields = ['title', 'author', 'type', 'date']
    for field in required_fields:
        if field not in data:
            print(f"[FAIL] {filepath}: Missing required field '{field}'.")
            return False

    valid_authors = ['franklin', 'kirsten', 'hamlet', 'larry', 'barry', 'stage-manager', 'nathan', 'alexis', 'roy', 'llewyn']
    if data['author'] not in valid_authors:
        print(f"[FAIL] {filepath}: Invalid author '{data['author']}'. Must be one of {valid_authors}.")
        return False

    valid_types = ['scene', 'reaction', 'think', 'plan', 'hobby', 'rehearsal', 'log', 'interview', 'post', 'soul', 'session', 'rule']
    if data['type'] not in valid_types:
        print(f"[FAIL] {filepath}: Invalid type '{data['type']}'. Must be one of {valid_types}.")
        return False

    print(f"[PASS] {filepath}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python frontmatter_validator.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isfile(target):
        if target.endswith('.md'):
            success = check_frontmatter(target)
            sys.exit(0 if success else 1)
        else:
            print("Target is not a markdown file.")
            sys.exit(1)

    elif os.path.isdir(target):
        all_passed = True
        for root, _, files in os.walk(target):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    if not check_frontmatter(filepath):
                        all_passed = False
        sys.exit(0 if all_passed else 1)
    else:
        print("Target not found.")
        sys.exit(1)
