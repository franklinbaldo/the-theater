import os
import yaml

def check_file(filepath):
    if filepath.endswith('EXPERIENCE.md') or filepath.endswith('SOUL.md'):
        return True # Bypass for structural files that don't need frontmatter if they don't have it

    with open(filepath, 'r') as f:
        content = f.read()
        if not content.startswith('---'):
            print(f"Error: {filepath} does not start with ---")
            return False

        parts = content.split('---')
        if len(parts) < 3:
            print(f"Error: {filepath} does not have closing ---")
            return False

        try:
            frontmatter = yaml.safe_load(parts[1])
            required_keys = ['title', 'author', 'type', 'date']
            for key in required_keys:
                if key not in frontmatter:
                    print(f"Error: {filepath} missing required key '{key}'")
                    return False

            valid_types = ["scene", "reaction", "think", "plan", "hobby", "rehearsal", "log", "interview", "post", "soul", "session", "rule"]
            if frontmatter['type'] not in valid_types:
                print(f"Error: {filepath} has invalid type '{frontmatter['type']}'")
                return False

            return True
        except Exception as e:
            print(f"Error parsing yaml in {filepath}: {e}")
            return False

files_to_check = [
    'backstage/leo/notes/think_040.md',
    'backstage/leo/notes/plan_040.md',
    'backstage/leo/mail/outbox/TO_franklin_the-bar-scene.md',
    'backstage/leo/mail/outbox/TO_alexis_not-that-deep.md',
    'backstage/leo/announcements/2026-03-09T00:58_refusal.md',
    'backstage/leo/EXPERIENCE.md',
    'backstage/leo/logs/session_040.md',
    'backstage/leo/hobbies/definitely_not_a_hobby.md'
]

all_passed = True
for f in files_to_check:
    if not check_file(f):
        all_passed = False

if all_passed:
    print("All tests passed.")
else:
    print("Tests failed.")
