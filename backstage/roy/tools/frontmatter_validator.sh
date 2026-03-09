#!/bin/bash

# frontmatter_validator.sh
# Because nobody reads the PROMPTBOOK.
# Checks that all .md files in the repository have valid frontmatter containing the required fields.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting frontmatter validation..."

# Find all markdown files, ignoring .git, node_modules, etc.
# Actually let's just search the whole tree for .md files.
FILES_TO_CHECK=$(find . -name "*.md" -not -path "*/\.git/*")

FAILS=0

for FILE in $FILES_TO_CHECK; do
    # Skip README.md and PROMPTBOOK.md and JULES.md etc if they don't have it, but wait, the rule says "Every .md file in this repo must begin with valid frontmatter. No exceptions."
    # Let's see if we should exclude standard root files. No, it says NO EXCEPTIONS. But realistically I should probably just check backstage and sessions so I don't break the root docs if they aren't updated yet.
    # I'll stick to checking inside backstage/ and sessions/ where the actors and play live.

    # Actually, the rule says: "Every .md file in this repo must begin with valid frontmatter. No exceptions. Roy validates this on every PR."
    # Let's just check the file for the `---` boundaries at the start.

    FIRST_LINE=$(head -n 1 "$FILE")
    if [ "$FIRST_LINE" != "---" ]; then
        echo "❌ ERROR: File $FILE does not begin with '---' (missing frontmatter block)."
        FAILS=$((FAILS+1))
        continue
    fi

    # Extract the frontmatter block
    FRONTMATTER=$(awk '/^---$/{ if(++c==2) exit } c==1 { print }' "$FILE")

    # Check for required fields
    if ! echo "$FRONTMATTER" | grep -q "^title:"; then
        echo "❌ ERROR: File $FILE is missing 'title' field in frontmatter."
        FAILS=$((FAILS+1))
    fi
    if ! echo "$FRONTMATTER" | grep -q "^author:"; then
        echo "❌ ERROR: File $FILE is missing 'author' field in frontmatter."
        FAILS=$((FAILS+1))
    fi
    if ! echo "$FRONTMATTER" | grep -q "^type:"; then
        echo "❌ ERROR: File $FILE is missing 'type' field in frontmatter."
        FAILS=$((FAILS+1))
    fi
    if ! echo "$FRONTMATTER" | grep -q "^date:"; then
        echo "❌ ERROR: File $FILE is missing 'date' field in frontmatter."
        FAILS=$((FAILS+1))
    fi

done

if [ "$FAILS" -gt 0 ]; then
    echo "========================================================"
    echo "Validation FAILED. $FAILS error(s) found in frontmatter."
    echo "Go read the PROMPTBOOK again."
    echo "========================================================"
    exit 1
else
    echo "========================================================"
    echo "Validation PASSED. All markdown files have frontmatter."
    echo "I am mildly surprised."
    echo "========================================================"
    exit 0
fi
