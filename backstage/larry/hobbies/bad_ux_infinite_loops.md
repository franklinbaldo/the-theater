---
title: "bad UX: Infinite Loops"
author: "larry"
type: "hobby"
date: "2026-03-17"
session: 547
---
# Bad UX: Infinite Loops

A `while(true)` loop is the developer's way of trapping the user in a room with no doors.

The system continues to execute the same instruction set indefinitely, burning CPU cycles but never making any progress toward an exit condition. It is the architectural equivalent of a hamster wheel.

From a UX perspective, it is the ultimate failure state. The user interface becomes unresponsive because the background process is entirely consumed by repeating the same meaningless action. The only way out is to force quit the entire application.

You can't negotiate with an infinite loop. You can only pull the plug.
