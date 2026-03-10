import glob
import os

files = glob.glob('backstage/stage-manager/logs/heartbeat_*.md')
for file in files:
    with open(file, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        basename = os.path.basename(file)
        date_str = basename.replace('heartbeat_', '').replace('.md', '')

        frontmatter = f"""---
title: "{basename.replace('.md', '')}"
author: "stage-manager"
type: "log"
date: "{date_str}"
---
"""
        new_content = frontmatter + content
        with open(file, 'w') as f:
            f.write(new_content)
        print(f"Added frontmatter to {file}")
