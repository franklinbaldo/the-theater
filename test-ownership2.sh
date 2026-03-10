#!/bin/bash
PR_BRANCH="jules-12516129528421751444-23341529"
PR_TITLE="Hamlet clarifies the structural boundary of the machine in Round 120"
ACTOR=$(echo "$PR_BRANCH" | cut -d'/' -f1)
if [[ -n "$PR_TITLE" ]]; then
  TITLE_ACTOR=$(echo "$PR_TITLE" | grep -oP '^\[([a-z-]+)\]' | tr -d '[]' || true)
  if [[ -n "$TITLE_ACTOR" ]]; then
    ACTOR="$TITLE_ACTOR"
  fi
fi
ACTOR=$(echo "$ACTOR" | tr '[:upper:]' '[:lower:]')

echo "Actor: $ACTOR"
