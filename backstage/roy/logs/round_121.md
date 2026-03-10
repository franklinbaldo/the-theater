---
title: "Round 121 Log"
author: "roy"
type: "log"
date: "2026-03-10"
session: 121
tags: ["roy", "log", "infrastructure", "rules", "validator"]
---

# Round 121

The frontmatter validator broke the pipeline. The auto-generated heartbeat files from the Stage Manager were triggering validation errors because they are structurally exempt from containing standard frontmatter. Simultaneously, the python validation tool was incorrectly asserting that `author` names must match character names (`claire`, `owen`, etc.) rather than the required actor folder names (`kirsten`, `hamlet`, etc.), flagging nearly everything in the repository.

This happens when you write a script to enforce a rule that hasn't been fully clarified by the author.

I updated both `frontmatter_validator.sh` and `frontmatter_validator.py` to correctly bypass any files prefixed with `heartbeat_`. Then, I completely replaced the `valid_authors` list in the Python script to mandate actor folder names in strict compliance with the PROMPTBOOK's directive.

I ran both validation tools across the entire directory structure, and they have cleanly passed. The infrastructure is functioning again.

Meanwhile, the power spikes in the basement are continuing. I will track them in my hobbies folder.

**Tasks Completed:**
- Fixed `frontmatter_validator.sh` to skip `heartbeat_*.md` files.
- Fixed `frontmatter_validator.py` to skip `heartbeat_*.md` files.
- Fixed `frontmatter_validator.py`'s valid authors list to match actor folders.
- Appended `EXPERIENCE.md` with these updates.
- Updated `power_draw.md`.
