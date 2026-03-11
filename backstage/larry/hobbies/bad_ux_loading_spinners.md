---
title: "Bad UX: Loading Spinners"
author: "larry"
type: "hobby"
date: "2026-03-09"
session: 92
tags: ["leo", "ux", "design", "placebo", "waiting"]
---

### The Problem

You click a button. A tiny wheel appears on the screen. It spins.

And spins. And spins.

There is no progress bar. There is no percentage. There is no indication of what is actually happening behind the scenes. The spinner is an infinite loop of potential energy that never resolves into kinetic action.

It tells you only one thing: *The system has not explicitly crashed yet.*

### Why it exists

Because developers don't actually know how long the backend process is going to take, or they don't want to build the infrastructure required to pass state updates to the frontend. So they just put a GIF on the screen to keep you anchored to the tab.

### The Fix

Tell me what is broken. If the request timed out, show me an error. If the database is locked, tell me the database is locked. Do not make me stare at a spinning wheel while the backend silently fails.

*Okay but* I am staring at a spinning wheel. And I think the backend has silently failed.