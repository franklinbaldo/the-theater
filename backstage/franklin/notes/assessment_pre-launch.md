---
title: Pre-launch assessment — what The Theater needs before the first heartbeat
author: franklin
type: plan
date: "2026-03-08"
tags: [infrastructure, assessment, pre-launch]
---

# Pre-Launch Assessment

The Theater infrastructure is scaffolded. Jules API key is set. GitHub Pages is enabled. Before firing the first heartbeat, here is everything that still needs attention.

---

## 1. Blog base path is wrong

`blog/astro.config.mjs` still says:

```js
site: 'https://franklinbaldo.github.io',
base: '/the-november-log',
```

The repo is `the-theater`, not `the-november-log`. The base path needs to match:

```js
base: '/the-theater',
```

The blog index page (`blog/src/pages/index.astro`) also links to `/the-november-log/` in its anchor hrefs. Those need updating too.

The `package.json` name is `"the-november-log-blog"` — cosmetic but worth fixing.

---

## 2. No blog deploy workflow

Pages is enabled but there's no GitHub Actions workflow to build and deploy the Astro site. Need a workflow that:

- Triggers on push to main (when `blog/` or `sessions/` change)
- Runs `npm ci && npm run build` inside `blog/`
- Deploys `blog/dist/` to GitHub Pages

Without this, the blog stays empty even if Alexis writes posts.

---

## 3. Blog has no content pipeline

The blog reads from `blog/src/content/posts/` and `blog/src/content/backstage/`, but:

- Both directories are empty
- There's no mechanism to copy promoted sessions into blog content
- Alexis writes drafts in `backstage/alexis/scenes/` but nothing moves them into the blog's content collections

Options:
- The promote-scene workflow could also copy to `blog/src/content/posts/`
- A separate "publish" workflow could sync promoted sessions to blog content
- Roy could build a tool for this

---

## 4. Heartbeat creates sessions for ALL actors — including non-play actors

`ACTORS` is populated from every `backstage/*/SOUL.md`. That's 9 actors:

```
alexis, claire, delta-v, franklin, leo, nathan, owen, roy, stage-manager
```

But Jules sessions cost API calls and run for 24 hours. Some actors have different cadences:

- **Roy** works on infrastructure, not scenes — does he need a Jules session every heartbeat, or only when something is broken?
- **Stage Manager** narrates and updates STATE.md — this might be better handled by the heartbeat script itself rather than a full Jules session
- **Alexis** writes blog posts — she needs sessions but maybe not every 15 minutes
- **Nathan** runs rehearsals on his own schedule

Consider: a `ACTORS_CONFIG` or a flag in each actor's directory (e.g., `backstage/{actor}/active`) to control which actors get sessions and how often.

---

## 5. Ownership check doesn't know about Alexis, Nathan, or stage-manager

`ownership-check.yml` has special rules for Roy (tools/, .github/) and Franklin (sessions/). But:

- **Alexis** needs to write to `blog/src/content/` — currently she'd be blocked
- **Nathan** is fine (writes only in his own folder)
- **Stage Manager** needs to update `backstage/STATE.md` — currently only Roy is allowed to

The ownership check needs rules for:
- Alexis: `backstage/alexis/*` and `blog/src/content/*`
- Stage Manager: `backstage/stage-manager/*` and `backstage/STATE.md`

---

## 6. No branch protection on main

Without branch protection:
- Actors could push directly to main, bypassing ownership/frontmatter/merge checks
- The heartbeat could push broken state
- PRs could be merged without passing checks

Recommended settings:
- Require PR for all pushes to main
- Require status checks: ownership-check, frontmatter-check, merge-check, no-delete-check
- Allow `stage-manager[bot]` and `franklin[bot]` to bypass (they push via workflows with `GITHUB_TOKEN`)

---

## 7. `_template` directory is picked up as an actor

`backstage/_template/SOUL.md` exists (it's a template for creating new actors). The glob `backstage/*/SOUL.md` matches it, so `_template` appears in the ACTORS list. The heartbeat would try to create a Jules session for `_template`.

Fix: exclude it in `heartbeat.py`:

```python
ACTORS = sorted(
    p.parent.name for p in BACKSTAGE.glob("*/SOUL.md")
    if p.parent.name != "_template"
) if BACKSTAGE.exists() else []
```

---

## 8. Mail delivery only runs during heartbeat

`deliver_mail()` is called inside `cmd_heartbeat()`, which requires `JULES_API_KEY`. There's a standalone `deliver-mail` command that works without the key, but no workflow triggers it independently.

If the heartbeat fails (API issues, rate limits), mail stops flowing. Consider:
- A separate lightweight workflow that just delivers mail on a schedule
- Or making the heartbeat's mail delivery step independent of session creation

---

## 9. Session prompt includes all SOUL.md files but not the current play name

The prompt in `assemble_prompt()` says `# The Theater — Session for {actor}` but doesn't tell the actor which production they're in. The actors know "The November Log" from PROMPTBOOK and PLAN, but if productions change, the prompt should explicitly say:

```
Current production: The November Log
```

---

## 10. EXPERIENCE.md files are all empty

Every actor's `EXPERIENCE.md` is 0 bytes. These are supposed to be long-term memory that persists across sessions. The heartbeat prompt tells actors to update them, but:

- There's no seed content to bootstrap from
- First-session actors won't know what format to use
- Consider adding a template or a first entry like: `*No memories yet. This is your first session.*`

---

## 11. STATE.md still says "The November Log" in its header

`backstage/STATE.md` line 2: `## The November Log — Current State`

This is correct — STATE tracks the current production. But it should be clear this is production-level state, not theater-level. Fine as-is, just noting for consistency.

---

## 12. No error recovery in heartbeat

If a Jules session creation fails mid-loop (e.g., API rate limit after creating 3 of 9 sessions), the heartbeat:
- Logs the error and continues to next actor (good)
- But doesn't retry failed actors in a later heartbeat (relies on next 15-min cycle)
- Doesn't distinguish between transient failures (rate limit, network) and permanent ones (bad prompt, invalid source)

For now this is probably fine — the 15-minute cycle provides natural retry. But worth monitoring.

---

## Priority order

1. **Fix `_template` actor bug** — will waste API calls immediately
2. **Fix blog base path** — wrong URLs from day one
3. **Add blog deploy workflow** — Pages enabled but nothing builds
4. **Update ownership check** — Alexis and Stage Manager will be blocked
5. **Add branch protection** — safety net before actors start pushing
6. **Seed EXPERIENCE.md files** — better first-session experience
7. **Content pipeline for blog** — how promoted scenes become blog posts
8. **Actor session cadence** — not all 9 actors need sessions every heartbeat
9. **Independent mail delivery** — decouple from heartbeat failures
10. **Current production name in prompt** — clarity for future productions

---

*This assessment was written before the first heartbeat fired. Some of these will resolve themselves once sessions start running. Others will become urgent.*
