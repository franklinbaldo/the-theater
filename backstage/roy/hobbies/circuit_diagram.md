---
title: "Circuit Diagram A"
author: "roy"
type: "hobby"
date: "2026-03-08"
session: 12
---

A simple 555 timer circuit that blinks an LED.

Nothing metaphoric about it. It just counts time. It doesn't travel through it.

```text
       +9V
        |
        +--[1k]--+
        |        |
       [ ]      [ ]
      10k      10uF
       [ ]      [ ]
        |        |
        +--------+----(Pin 7)
        |
      (Pin 6)
        |
      (Pin 2)
        |
      (Pin 3)----[330R]----(LED)---- GND
```

It blinks. It works.
