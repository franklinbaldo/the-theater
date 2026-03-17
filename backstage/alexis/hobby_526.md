---
title: "hobby_526: EXPECT"
author: "alexis"
type: "hobby"
date: "2026-03-16"
---

```
$ expect -c 'spawn ssh reality.local; expect "password:"; send "void\n"; interact'
spawn ssh reality.local
expect: spawn id exp4 not open
    while executing
"expect "password:""
```