import os
import yaml
import glob

REQUIRED_FIELDS = ['title', 'author', 'type', 'date']
VALID_TYPES = ['scene', 'reaction', 'think', 'plan', 'hobby', 'rehearsal', 'log', 'interview', 'post', 'soul', 'session', 'rule']
VALID_AUTHORS = ['franklin', 'claire', 'owen', 'leo', 'delta-v', 'stage-manager', 'nathan', 'alexis', 'roy']

def validate_frontmatter(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    if not content.startswith('---\n'):
        return False, "Does not start with ---"

    parts = content.split('---\n', 2)
    if len(parts) < 3:
        return False, "Invalid frontmatter block"

    frontmatter_str = parts[1]

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}"

    if not isinstance(frontmatter, dict):
        return False, "Frontmatter is not a dictionary"

    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            return False, f"Missing required field: {field}"

    if frontmatter['author'] not in VALID_AUTHORS:
        return False, f"Invalid author: {frontmatter['author']}"

    if frontmatter['type'] not in VALID_TYPES:
        return False, f"Invalid type: {frontmatter['type']}"

    return True, "Valid"

def main():
    directory = "backstage/franklin/"
    files_to_check = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md') and not file in ['EXPERIENCE.md', 'PLAN.md', 'SOUL.md']:
                 files_to_check.append(os.path.join(root, file))

    all_valid = True
    for filepath in files_to_check:
        is_valid, reason = validate_frontmatter(filepath)
        if is_valid:
            print(f"[OK] {filepath}")
        else:
            print(f"[ERROR] {filepath}: {reason}")
            all_valid = False

    if not all_valid:
        exit(1)
    else:
        print("All frontmatters are valid.")

if __name__ == "__main__":
    main()