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
    BASENAME=$(basename "$FILE")
    if [[ "$BASENAME" == "README.md" || "$BASENAME" == "PROMPTBOOK.md" || "$BASENAME" == "JULES.md" || "$BASENAME" == "SOUL.md" || "$BASENAME" == "EXPERIENCE.md" || "$BASENAME" == "PLAN.md" || "$BASENAME" == "STATE.md" || "$FILE" == *"heartbeat_"* ]]; then
        continue
    fi

    # Check the file for the `---` boundaries at the start.

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
