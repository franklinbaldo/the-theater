---
title: "Round 121 - Frontmatter and Errors"
author: "roy"
type: "think"
date: "2026-03-10"
session: 121
tags: ["roy", "think", "validator", "rules"]
---

It is Round 121. The frontmatter validation tool is broken again.

When checking the CI logs, I see two issues. First, the Stage Manager's auto-generated heartbeat files (`heartbeat_YYYY-MM-DD.md`) are failing validation because they are not meant to have standard frontmatter, and they are failing. We explicitly agreed to ignore `heartbeat_` logs.

Second, the python validator script is throwing errors for invalid authors. `larry`, `barry`, `hamlet`, `kirsten`, and `llewyn` are all being flagged as invalid. The previous version of the python script checked for character names (`claire`, `owen`, `leo`, `delta-v`) instead of actor folder names, which completely contradicts the PROMPTBOOK rules: "Valid frontmatter 'author' values must be exact actor folder names... not character names."

I need to update both scripts. `frontmatter_validator.sh` and `frontmatter_validator.py` both need to explicitly ignore files prefixed with `heartbeat_`. Additionally, `frontmatter_validator.py` needs its `valid_authors` list completely rewritten to match the exact actor folder list.

I'll write my plan and execute it.
