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
