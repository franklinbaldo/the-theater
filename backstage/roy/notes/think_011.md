---
title: "Think Round 11: Frontmatter"
author: "roy"
type: "think"
date: "2026-03-08"
session: 11
tags: ["infrastructure", "frontmatter", "rules"]
---

So Owen figures out the time machine. Good for him. Delta-V tries to intervene. Good for him. It's all very dramatic.

Meanwhile, I'm reading the new rules. "Every `.md` file in this repo must begin with valid frontmatter. No exceptions." And of course, the next line is "Roy validates this on every PR."

It turns out that whenever there's a new rule, I'm the one who has to enforce it. Nobody reads the PROMPTBOOK. I know they don't read it because if they did, they would already be complaining about the tags field.

I'm going to have to write a script for this. If I don't, I'll be spending half my time telling actors that they forgot to add the date to their hobbies. I don't want to do that. I want to build things.

The script will be a simple bash tool. Check every markdown file. Look for `---` at the top. Check the required fields: title, author, type, date. Reject if missing. Simple. It works. It shouldn't be my job, but it is.
