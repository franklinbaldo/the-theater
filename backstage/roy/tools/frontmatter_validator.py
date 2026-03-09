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
    with open(filepath, 'r') as f:
        content = f.read()

    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
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

    valid_authors = ['franklin', 'claire', 'owen', 'leo', 'delta-v', 'stage-manager', 'nathan', 'alexis', 'roy']
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
import os
import sys
import yaml

VALID_TYPES = {"scene", "reaction", "think", "plan", "hobby", "rehearsal", "log", "interview", "post", "soul", "session", "rule"}
VALID_AUTHORS = {"franklin", "claire", "owen", "leo", "delta-v", "stage-manager", "nathan", "alexis", "roy"}

def validate_frontmatter(filepath):
    """
    Validates that a markdown file begins with correctly structured YAML frontmatter.
    It returns True if valid, or prints an error and returns False if invalid.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    if not lines:
        print(f"File {filepath} is empty.")
        return False

    if lines[0].strip() != "---":
        print(f"File {filepath} does not start with a YAML separator '---'.")
        return False

    yaml_lines = []
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
        yaml_lines.append(lines[i])

    if end_idx == -1:
        print(f"File {filepath} has an unclosed YAML block.")
        return False

    yaml_content = "".join(yaml_lines)
    try:
        data = yaml.safe_load(yaml_content)
    except Exception as e:
        print(f"File {filepath} has invalid YAML syntax: {e}")
        return False

    if not isinstance(data, dict):
        print(f"File {filepath} frontmatter must be a key-value dictionary.")
        return False

    errors = []

    # Check title
    if "title" not in data:
        errors.append("Missing required field 'title'.")

    # Check author
    if "author" not in data:
        errors.append("Missing required field 'author'.")
    elif data["author"] not in VALID_AUTHORS:
        errors.append(f"Invalid 'author'. Expected one of {VALID_AUTHORS}, got {data['author']}.")

    # Check type
    if "type" not in data:
        errors.append("Missing required field 'type'.")
    elif data["type"] not in VALID_TYPES:
        errors.append(f"Invalid 'type'. Expected one of {VALID_TYPES}, got {data['type']}.")

    # Check date
    if "date" not in data:
        errors.append("Missing required field 'date'.")

    # Warn on unknown fields if necessary, though optional fields exist.

    if errors:
        print(f"File {filepath} frontmatter validation failed:")
        for err in errors:
            print(f"  - {err}")
        return False

    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python frontmatter_validator.py <file1.md> [file2.md ...]")
        sys.exit(1)

    all_valid = True
    for file in sys.argv[1:]:
        if not file.endswith('.md'):
            print(f"Skipping non-markdown file: {file}")
            continue
        if not validate_frontmatter(file):
            all_valid = False

    if not all_valid:
        sys.exit(1)

    print("All checked files have valid frontmatter.")
    sys.exit(0)
