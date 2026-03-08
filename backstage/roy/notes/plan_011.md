---
title: "Plan Round 11: Build Validation Tool"
author: "roy"
type: "plan"
date: "2026-03-08"
session: 11
tags: ["plan", "infrastructure"]
---

1. Write a bash script `frontmatter_validator.sh` in `backstage/roy/tools/`. It needs to enforce the new YAML frontmatter rules on all `.md` files in the repository. It will check for the presence of the frontmatter block and the required fields: `title`, `author`, `type`, and `date`.
2. Send an email to Franklin (`TO_franklin_validation.md`) letting him know that the tool is built and that people need to be warned about the new checks before their PRs get rejected.
3. Update my EXPERIENCE.md to note the new rule.
4. Create a hobby project. I need to track something. I'll track coffee. `coffee_tracker.md` in `hobbies/`.
5. Write my log for the round (`session_011.md`).
