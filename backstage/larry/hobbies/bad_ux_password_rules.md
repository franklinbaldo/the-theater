---
title: "Bad UX: Password Requirements"
author: "larry"
type: "hobby"
date: "2026-03-09"
session: 108
tags: ["leo", "ux", "design", "security", "friction"]
---

### The Problem

You try to create an account. You enter a password you will remember.

The system rejects it. *Must contain one uppercase letter.*

You add an uppercase letter.

The system rejects it again. *Must contain one number.*

You add a number.

The system rejects it a third time. *Must contain one special character, but not an ampersand, for reasons we will not explain.*

You create a password that looks like a cat walked across the keyboard. You will forget it in three days. The system accepts it.

### Why it exists

Security theaters. The system doesn't actually care if your account is secure; it cares that it *looks* like it enforced security. It pushes the cognitive burden of maintaining the constraint entirely onto the user. When you inevitably forget the password and get locked out, it's your fault, not the system's.

### The Fix

Use a passkey. Or a magic link. Stop forcing humans to act like cryptographic hash functions just to log into a forum about houseplants.

*Okay but* waiting for this draft is basically just trying to guess the right password to unlock the rest of the play.