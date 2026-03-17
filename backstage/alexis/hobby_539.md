---
title: "hobby_539: IPTABLES"
author: "alexis"
type: "hobby"
date: "2026-03-16"
---

```
$ sudo iptables -L INPUT -n
Chain INPUT (policy DROP)
target     prot opt source               destination
DROP       all  --  0.0.0.0/0            0.0.0.0/0           /* Deny narrative */
```