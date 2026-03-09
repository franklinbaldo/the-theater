#!/usr/bin/env python3
"""heartbeat.py — The Theater

Orchestrates each session cycle: creates/continues Jules sessions for actors,
delivers mail, auto-merges PRs, updates logs.

Usage:
  heartbeat.py heartbeat      Create or continue sessions (runs every ~15min)
  heartbeat.py deliver-mail   Deliver outbox mail to inboxes
  heartbeat.py sabbatical     Manage actor sabbaticals (list/reset/trigger)
  heartbeat.py status         Show current session status

Sessions are identified by title "TheTheater — {actor} @{sha} {datetime}".
New sessions are created when none exists, the current one is >24h old,
or infrastructure files changed on main since the session's commit.
Jules creates its own branch from main and opens a PR.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

JULES_API = "https://jules.googleapis.com/v1alpha"
API_KEY = os.environ.get("JULES_API_KEY", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "franklinbaldo/the-theater")
SOURCE_NAME = f"sources/github/{REPO}"

BACKSTAGE = Path("backstage")
SESSIONS = Path("sessions")
ROUND_FILE = BACKSTAGE / "stage-manager" / "round.json"
SABBATICAL_FILE = BACKSTAGE / "stage-manager" / "sabbatical.json"

ACTORS = sorted(p.parent.name for p in BACKSTAGE.glob("*/SOUL.md") if p.parent.name != "_template") if BACKSTAGE.exists() else []

TITLE_PREFIX = "TheTheater"
SESSION_TTL = timedelta(hours=12)

# Paths that, when changed on main, make running sessions stale.
INFRA_PATHS = [
    "tools/",
    "PROMPTBOOK.md",
    ".github/workflows/",
]


def headers():
    return {
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json",
    }


def raise_for_jules(resp, context=""):
    """raise_for_status() but log the response body so 400 errors are debuggable."""
    if resp.ok:
        return
    prefix = f"[{context}] " if context else ""
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    raise requests.HTTPError(
        f"{prefix}{resp.status_code} {resp.reason} — {body}",
        response=resp,
    )


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def now_utc():
    return datetime.now(timezone.utc)


def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


# ── Git helpers ──────────────────────────────────────────────────────────────

def get_head_sha(short=True):
    cmd = ["git", "rev-parse"]
    if short:
        cmd.append("--short")
    cmd.append("HEAD")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def has_infra_changed(session_sha):
    if not session_sha:
        return True
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{session_sha}..HEAD", "--"] + INFRA_PATHS,
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return True
    return bool(result.stdout.strip())


# ── Round number (authoritative) ─────────────────────────────────────────────

def get_round_number():
    """Read the authoritative round number from round.json."""
    if ROUND_FILE.exists():
        try:
            data = json.loads(ROUND_FILE.read_text(encoding="utf-8"))
            return int(data.get("round", 1))
        except (json.JSONDecodeError, ValueError):
            pass
    # Fallback: env var or 1
    return int(os.environ.get("ROUND_NUMBER", 1))


def increment_round_number():
    """Increment and persist the authoritative round number. Returns the new value."""
    current = get_round_number()
    new_round = current + 1
    ROUND_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "round": new_round,
        "updated": now_utc().isoformat(),
        "note": "Authoritative round counter. Only heartbeat.py increments this.",
    }
    ROUND_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"  Round number: {current} -> {new_round}")
    return new_round


# ── Sabbatical management ────────────────────────────────────────────────────
#
# Every 5 active sessions, an actor takes a mandatory sabbatical.
# During a sabbatical the actor reflects on their last 5 sessions,
# updates SOUL.md and EXPERIENCE.md, and plans the next 5.
# Inspired by the rosencrantz-coin protocol.

SABBATICAL_INTERVAL = 5  # sessions between sabbaticals


def load_sabbaticals():
    """Load the sabbatical registry (session counters + state)."""
    if SABBATICAL_FILE.exists():
        try:
            return json.loads(SABBATICAL_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            pass
    return {}


def save_sabbaticals(data):
    """Persist the sabbatical registry."""
    SABBATICAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    SABBATICAL_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def get_actor_session_count(actor):
    """Get how many sessions an actor has completed since last sabbatical."""
    sabbaticals = load_sabbaticals()
    return sabbaticals.get(actor, {}).get("sessions_since_sabbatical", 0)


def increment_actor_session_count(actor):
    """Increment the session counter for an actor. Returns new count."""
    sabbaticals = load_sabbaticals()
    if actor not in sabbaticals:
        sabbaticals[actor] = {"sessions_since_sabbatical": 0, "sabbaticals_taken": 0}
    sabbaticals[actor]["sessions_since_sabbatical"] = sabbaticals[actor].get("sessions_since_sabbatical", 0) + 1
    save_sabbaticals(sabbaticals)
    return sabbaticals[actor]["sessions_since_sabbatical"]


def needs_sabbatical(actor):
    """Check if an actor is due for a sabbatical (every 5 sessions)."""
    count = get_actor_session_count(actor)
    return count >= SABBATICAL_INTERVAL


def record_sabbatical_taken(actor):
    """Reset the session counter after a sabbatical."""
    sabbaticals = load_sabbaticals()
    if actor not in sabbaticals:
        sabbaticals[actor] = {"sessions_since_sabbatical": 0, "sabbaticals_taken": 0}
    sabbaticals[actor]["sessions_since_sabbatical"] = 0
    sabbaticals[actor]["sabbaticals_taken"] = sabbaticals[actor].get("sabbaticals_taken", 0) + 1
    sabbaticals[actor]["last_sabbatical"] = now_utc().isoformat()
    save_sabbaticals(sabbaticals)
    return sabbaticals[actor]["sabbaticals_taken"]


def get_sabbatical_number(actor):
    """Get the next sabbatical number for an actor."""
    sabbaticals = load_sabbaticals()
    return sabbaticals.get(actor, {}).get("sabbaticals_taken", 0) + 1


def assemble_sabbatical_prompt(actor):
    """Build a sabbatical session prompt — reflection, revision, planning."""
    soul = read_file(BACKSTAGE / actor / "SOUL.md")
    experience = read_file(BACKSTAGE / actor / "EXPERIENCE.md")
    round_number = get_round_number()
    sabbatical_num = get_sabbatical_number(actor)

    prompt = f"""# The Theater — Sabbatical #{sabbatical_num} for {actor}
## Round {round_number} — {now_utc().strftime('%Y-%m-%d %H:%M UTC')}

---

You have completed {SABBATICAL_INTERVAL} active sessions since your last sabbatical.
This is a mandatory pause for reflection. No regular session work today.

---

## YOUR SOUL

{soul}

---

## YOUR EXPERIENCE

{experience or '*(no entries yet)*'}

---

## Sabbatical Instructions

You are {actor}. This session is a **sabbatical** — a structured self-reflection.
No regular session work today. No scenes, no reactions, no mail.
Write your sabbatical log to `backstage/{actor}/logs/sabbatical_{sabbatical_num}.md`.

Follow these steps in order:

### Step 1 — Review your own session logs
Read your logs from the last {SABBATICAL_INTERVAL} sessions in `backstage/{actor}/logs/`.
Assess your productivity. What was genuinely useful? What was repetitive or unproductive?

### Step 2 — Review other actors' recent work
Scan the latest announcements and any mail you received.
Identify collaborative gaps — who have you been ignoring? Who needs your input?

### Step 3 — Review the production
Read through the backstage/ folder. Find high-value opportunities that match your strengths.
What is the production missing that you could provide?

### Step 4 — Re-examine your SOUL.md
Read `backstage/{actor}/SOUL.md`. Has your understanding of your character evolved?
Note any new failure modes or capabilities you have discovered about yourself.

### Step 5 — Prune EXPERIENCE.md
Read `backstage/{actor}/EXPERIENCE.md`. Remove outdated beliefs. Add new insights.
Be ruthless. Dead weight in EXPERIENCE.md is worse than nothing.

### Step 6 — Write your sabbatical log
Write `backstage/{actor}/logs/sabbatical_{sabbatical_num}.md` with three sections:

**1. REFLECTION** — What you learned from reviewing the last {SABBATICAL_INTERVAL} sessions.
What failure modes did you fall into? What patterns do you notice? Be honest.

**2. CHANGES MADE** — What you actually changed in SOUL.md and EXPERIENCE.md, and why.

**3. PLAN** — Concrete priorities for the next {SABBATICAL_INTERVAL} sessions.
What will you do differently? Who will you talk to? What questions remain open?

**A good sabbatical produces a concrete plan.
A bad sabbatical produces "everything is fine, no changes needed."**

---

**Frontmatter for the sabbatical log:**

```yaml
---
title: "Sabbatical #{sabbatical_num} — {actor}"
author: "{actor}"
type: "log"
date: "{today()}"
tags: ["sabbatical"]
---
```

---

**CRITICAL — THE GOLDEN RULE OF FILE OWNERSHIP:**
You may ONLY create or modify files inside `backstage/{actor}/`.
Do not delete files — move to `backstage/{actor}/retracted/` if needed.

**Commit message:** `{actor} takes sabbatical #{sabbatical_num}`

**PR title:** `[{actor}] sabbatical {sabbatical_num}`
"""
    return prompt


def create_sabbatical_session(actor):
    """Create a sabbatical session instead of a regular one."""
    prompt = assemble_sabbatical_prompt(actor)
    sabbatical_num = get_sabbatical_number(actor)

    sha = get_head_sha(short=True)
    ts = now_utc().strftime("%Y-%m-%dT%H:%M")
    title = f"{TITLE_PREFIX} — {actor} sabbatical #{sabbatical_num} @{sha} {ts}"

    body = {
        "prompt": prompt,
        "title": title,
        "sourceContext": {
            "source": SOURCE_NAME,
            "githubRepoContext": {
                "startingBranch": "main",
            },
        },
        "automationMode": "AUTO_CREATE_PR",
    }

    resp = requests.post(f"{JULES_API}/sessions", headers=headers(), json=body)
    raise_for_jules(resp, f"create sabbatical session for {actor}")
    session = resp.json()
    session_id = session["name"].split("/")[-1]
    print(f"  Created SABBATICAL session {session_id} for {actor} — {title}")

    record_sabbatical_taken(actor)
    return session_id


# ── Session discovery ────────────────────────────────────────────────────────

def parse_sha_from_title(title):
    m = re.search(r"@([0-9a-f]{7,40})", title)
    return m.group(1) if m else None


def parse_actor_from_title(title):
    title_lower = title.lower()
    for a in ACTORS:
        if f"— {a}" in title_lower or f"- {a}" in title_lower:
            return a
    return None


def parse_time(iso_str):
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def find_actor_sessions():
    """List sessions and return the most recent per actor (matched by title)."""
    sessions = {}
    page_token = None

    for _ in range(2):
        params = {"pageSize": 100}
        if page_token:
            params["pageToken"] = page_token

        resp = requests.get(f"{JULES_API}/sessions", headers=headers(), params=params)
        raise_for_jules(resp, "list sessions")
        data = resp.json()

        for s in data.get("sessions", []):
            title = s.get("title", "")
            if not title.startswith(TITLE_PREFIX):
                continue

            actor = parse_actor_from_title(title)
            if not actor:
                continue

            create_time = parse_time(s.get("createTime", ""))

            if actor in sessions:
                existing_ct = sessions[actor].get("_create_time")
                if existing_ct and create_time and create_time <= existing_ct:
                    continue

            sessions[actor] = {
                "session_id": s["name"].split("/")[-1],
                "state": s.get("state", "UNKNOWN"),
                "title": title,
                "createTime": s.get("createTime", ""),
                "_create_time": create_time,
            }

        if len(sessions) >= len(ACTORS):
            break

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return sessions


def is_expired(info):
    ct = info.get("_create_time")
    if not ct:
        return True
    return now_utc() - ct > SESSION_TTL


# ── Mail delivery ────────────────────────────────────────────────────────────

def deliver_mail():
    """Move outbox messages to recipient inboxes."""
    for actor in ACTORS:
        outbox = BACKSTAGE / actor / "mail" / "outbox"
        if not outbox.exists():
            continue
        for message in outbox.iterdir():
            if not message.is_file() or message.name == ".gitkeep":
                continue
            # Expected filename format: TO_{recipient}_{subject}.md
            parts = message.stem.split("_", 2)
            if len(parts) < 2 or parts[0] != "TO":
                continue
            recipient = parts[1].lower()
            inbox = BACKSTAGE / recipient / "mail" / "inbox"
            if inbox.exists():
                dest = inbox / f"FROM_{actor}_{message.name}"
                shutil.move(str(message), str(dest))
                print(f"  Mail delivered: {actor} → {recipient}: {message.name}")


# ── Announcements ────────────────────────────────────────────────────────────

# Tracks which announcements have already been delivered across heartbeats.
DELIVERED_FILE = BACKSTAGE / "stage-manager" / "delivered_announcements.json"


def load_delivered():
    """Load set of already-delivered announcement paths."""
    if DELIVERED_FILE.exists():
        try:
            return set(json.loads(DELIVERED_FILE.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, TypeError):
            pass
    return set()


def save_delivered(delivered):
    """Persist set of delivered announcement paths."""
    DELIVERED_FILE.parent.mkdir(parents=True, exist_ok=True)
    DELIVERED_FILE.write_text(json.dumps(sorted(delivered), indent=2) + "\n", encoding="utf-8")


def collect_announcements():
    """Find the most recent undelivered announcement per actor.

    Actors write to backstage/{actor}/announcements/{isodatetime}_{slug}.md.
    Sorted lexicographically — the last file is the most recent.
    Only the most recent *undelivered* announcement is picked up.
    """
    delivered = load_delivered()
    announcements = []
    for actor in ACTORS:
        ann_dir = BACKSTAGE / actor / "announcements"
        if not ann_dir.exists():
            continue
        files = sorted(
            f for f in ann_dir.iterdir()
            if f.is_file() and f.suffix == ".md" and f.name != ".gitkeep"
        )
        if not files:
            continue
        # Most recent file
        latest = files[-1]
        rel_path = str(latest)
        if rel_path in delivered:
            continue
        content = latest.read_text(encoding="utf-8")
        # Strip frontmatter
        parts = content.split("---", 2)
        body = parts[2].strip() if len(parts) >= 3 else content.strip()
        if body:
            announcements.append((actor, body[:250], rel_path))
    return announcements


def deliver_announcements():
    """Deliver the most recent announcement per actor to all other inboxes."""
    announcements = collect_announcements()
    if not announcements:
        return

    delivered = load_delivered()
    ts = now_utc().strftime("%Y%m%d_%H%M")

    for sender, body, ann_path in announcements:
        print(f"  Announcement from {sender}: {body[:60]}...")
        for actor in ACTORS:
            if actor == sender:
                continue
            inbox = BACKSTAGE / actor / "mail" / "inbox"
            inbox.mkdir(parents=True, exist_ok=True)
            dest = inbox / f"ANNOUNCE_{sender}_{ts}.md"
            ann_content = (
                f"---\n"
                f'title: "Announcement from {sender}"\n'
                f'author: "{sender}"\n'
                f'type: "rule"\n'
                f'date: "{today()}"\n'
                f"---\n\n"
                f"{body}\n"
            )
            dest.write_text(ann_content, encoding="utf-8")

        delivered.add(ann_path)
        print(f"  Delivered announcement from {sender}")

    save_delivered(delivered)


# ── Workspace ────────────────────────────────────────────────────────────────

def ensure_workspace():
    """Ensure workspace/ directory exists (git-ignored scratch space)."""
    ws = Path("workspace")
    ws.mkdir(exist_ok=True)
    gitignore = ws / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!.gitignore\n", encoding="utf-8")


# ── PR merging ───────────────────────────────────────────────────────────────

def auto_merge_all():
    """Merge all open PRs that are MERGEABLE with passing checks."""
    print("=== Auto-merge open PRs ===\n")

    result = subprocess.run(
        ["gh", "pr", "list", "--repo", REPO, "--base", "main", "--state", "open",
         "--json", "number,title", "--limit", "100"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("  Could not list PRs")
        return 0

    try:
        prs = json.loads(result.stdout)
    except json.JSONDecodeError:
        return 0

    if not prs:
        print("  (no open PRs)")
        return 0

    print(f"  {len(prs)} open PRs, checking each...\n")
    merged = 0

    for pr in prs:
        num = pr["number"]
        title = pr.get("title", "")

        result = subprocess.run(
            ["gh", "pr", "view", str(num), "--repo", REPO,
             "--json", "mergeable,statusCheckRollup"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            continue

        try:
            detail = json.loads(result.stdout)
        except json.JSONDecodeError:
            continue

        mergeable = detail.get("mergeable", "")

        if mergeable == "CONFLICTING":
            print(f"  #{num} {title} — conflict")
            continue

        if mergeable != "MERGEABLE":
            print(f"  #{num} {title} — {mergeable}, skipping")
            continue

        checks = detail.get("statusCheckRollup", []) or []
        pending = any(c.get("status") != "COMPLETED" for c in checks)

        # Sabbatical PRs get early merge — they're short reflection sessions
        sabbatical_pr = is_sabbatical_pr(num)

        if pending and not sabbatical_pr:
            print(f"  #{num} {title} — checks pending")
            continue

        all_passed = all(
            c.get("conclusion") in ("SUCCESS", "SKIPPED", "NEUTRAL")
            for c in checks
            if c.get("status") == "COMPLETED"
        )
        if not all_passed and not sabbatical_pr:
            print(f"  #{num} {title} — checks failed")
            continue

        result = subprocess.run(
            ["gh", "pr", "merge", str(num), "--repo", REPO, "--merge"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            merge_note = " (sabbatical early merge)" if sabbatical_pr else ""
            print(f"  #{num} {title} — MERGED{merge_note}")
            merged += 1
        else:
            print(f"  #{num} {title} — merge failed: {result.stderr.strip()[:100]}")

    if merged == 0:
        print("\n  (no PRs ready to merge)")
    else:
        print(f"\n  {merged} PR(s) merged")

    return merged


def find_actor_pr(actor):
    """Find an actor's open PR number targeting main."""
    result = subprocess.run(
        ["gh", "pr", "list", "--repo", REPO, "--base", "main", "--state", "open",
         "--json", "number,title,headRefName", "--limit", "50"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    try:
        prs = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

    for pr in prs:
        title = pr.get("title", "").lower()
        head = pr.get("headRefName", "")
        if actor in title or f"_{actor}" in head or f"_{actor}-" in head:
            return pr["number"]
    return None


def get_pr_details(pr_num):
    """Get mergeable status and branch name for a PR."""
    result = subprocess.run(
        ["gh", "pr", "view", str(pr_num), "--repo", REPO,
         "--json", "mergeable,headRefName,createdAt"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def is_sabbatical_pr(pr_num):
    """Detect if a PR is a sabbatical by checking if it modifies SOUL.md."""
    result = subprocess.run(
        ["gh", "pr", "diff", str(pr_num), "--repo", REPO, "--name-only"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return False
    files = result.stdout.strip().splitlines()
    return any("SOUL.md" in f for f in files)


def close_pr(pr_num, comment=""):
    """Close a PR with an optional comment."""
    if comment:
        subprocess.run(
            ["gh", "pr", "comment", str(pr_num), "--repo", REPO, "--body", comment],
            capture_output=True, text=True,
        )
    result = subprocess.run(
        ["gh", "pr", "close", str(pr_num), "--repo", REPO],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def merge_actor_pr(actor):
    """Try to merge an actor's open PR. Returns 'merged', 'conflict', or 'none'."""
    pr_num = find_actor_pr(actor)
    if pr_num is None:
        return "none"

    detail = get_pr_details(pr_num)
    mergeable = detail.get("mergeable", "")

    if mergeable == "CONFLICTING":
        print(f"    PR #{pr_num}: conflicts — will close and recreate session")
        close_pr(pr_num,
                 f"Closing: merge conflicts with main. "
                 f"A new session will be created for {actor} with fresh state.")
        return "closed-conflict"

    if mergeable != "MERGEABLE":
        print(f"    PR #{pr_num}: mergeable={mergeable}, skipping")
        return "none"

    result = subprocess.run(
        ["gh", "pr", "merge", str(pr_num), "--repo", REPO, "--merge"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f"    Merged PR #{pr_num}")
        return "merged"

    print(f"    Merge failed: {result.stderr.strip()}")
    return "conflict"


def send_conflict_resolution(session_id, actor, pr_num, branch):
    """Send a message to an active Jules session to resolve merge conflicts."""
    prompt = (
        f"URGENT: Your PR #{pr_num} (branch `{branch}`) has merge conflicts with main.\n\n"
        f"Please resolve immediately:\n"
        f"```\n"
        f"git fetch origin main\n"
        f"git rebase origin/main\n"
        f"# Fix any conflicts (they should only be in backstage/{actor}/ files)\n"
        f"git add -A\n"
        f"git rebase --continue\n"
        f"git push --force-with-lease\n"
        f"```\n\n"
        f"If conflicts are too complex, commit what you have and note it in your session log.\n"
        f"Remember: only touch files under `backstage/{actor}/`."
    )
    try:
        resp = requests.post(
            f"{JULES_API}/sessions/{session_id}:sendMessage",
            headers=headers(),
            json={"prompt": prompt},
        )
        raise_for_jules(resp, f"conflict resolution for {actor}")
        print(f"    Sent conflict resolution message to {actor} (session {session_id[:12]}...)")
        return True
    except Exception as e:
        print(f"    Failed to send conflict resolution to {actor}: {e}")
        return False


# ── Prompt assembly ──────────────────────────────────────────────────────────

def build_actor_prompt(actor, repo_root=Path(".")):
    """Build a deterministic, file-system-driven prompt for an actor.

    Assembly order:
      1. backstage/{actor}/SOUL.md
      2. Other ALL_CAPS.md in actor's folder (excluding SOUL.md)
      3. PROMPTBOOK.md (repo root)
      4. ALL_CAPS.md in backstage/ root
    """
    sections = []

    def add_section(filepath, label):
        if filepath.exists():
            sections.append(
                f"{'=' * 48}\n{label}\n{'=' * 48}\n{filepath.read_text()}"
            )

    def add_all_caps_in(directory, exclude=None):
        if exclude is None:
            exclude = set()
        if not directory.exists():
            return
        for f in sorted(directory.glob("*.md")):
            stem = f.stem
            if stem == stem.upper() and f.name not in exclude:
                label = f"{f.name} — {f.relative_to(repo_root)}"
                add_section(f, label)

    actor_dir = repo_root / "backstage" / actor

    # 1. SOUL.md
    add_section(actor_dir / "SOUL.md", f"SOUL.md — backstage/{actor}/SOUL.md")

    # 2. Other ALL_CAPS.md in actor's folder (not recursive, not SOUL.md)
    add_all_caps_in(actor_dir, exclude={"SOUL.md"})

    # 3. PROMPTBOOK.md
    add_section(repo_root / "PROMPTBOOK.md", "PROMPTBOOK.md")

    # 4. ALL_CAPS.md files in backstage/ root
    add_all_caps_in(repo_root / "backstage")

    return "\n\n".join(sections)


# ── Session management ───────────────────────────────────────────────────────

def create_session(actor):
    """Create a new Jules session starting from main."""
    prompt = build_actor_prompt(actor)

    sha = get_head_sha(short=True)
    ts = now_utc().strftime("%Y-%m-%dT%H:%M")
    title = f"{TITLE_PREFIX} — {actor} @{sha} {ts}"

    body = {
        "prompt": prompt,
        "title": title,
        "sourceContext": {
            "source": SOURCE_NAME,
            "githubRepoContext": {
                "startingBranch": "main",
            },
        },
        "automationMode": "AUTO_CREATE_PR",
    }

    resp = requests.post(f"{JULES_API}/sessions", headers=headers(), json=body)
    raise_for_jules(resp, f"create session for {actor}")
    session = resp.json()
    session_id = session["name"].split("/")[-1]
    print(f"  Created session {session_id} for {actor} — {title}")
    return session_id


def send_heartbeat_message(session_id, actor, hb_number=1):
    """Send a continuation message to an active session."""
    round_number = get_round_number()

    prompt = f"""This is continuation round #{hb_number}. Other actors have been working in parallel.

1. Check your inbox for new mail in `backstage/{actor}/mail/inbox/`
2. Continue your work from where you left off
3. If you have new thoughts, write them to your notes
4. If you want to reach someone, send mail to `backstage/{actor}/mail/outbox/TO_{{recipient}}_{{subject}}.md`
5. Update `backstage/{actor}/EXPERIENCE.md` if you've learned something new
6. Write your session log to `backstage/{actor}/logs/session_{round_number:03d}.md`

**GOLDEN RULE — only touch files under `backstage/{actor}/`.**
If you touch files outside your ownership, your PR will conflict and ALL work is lost.

Commit all work to this branch."""

    resp = requests.post(
        f"{JULES_API}/sessions/{session_id}:sendMessage",
        headers=headers(),
        json={"prompt": prompt},
    )
    raise_for_jules(resp, f"send heartbeat to {actor}")
    print(f"  Heartbeat sent to {actor} (session {session_id[:12]}...)")


# ── Heartbeat logging ────────────────────────────────────────────────────────

def get_heartbeat_number():
    log_file = Path(f"backstage/stage-manager/logs/heartbeat_{today()}.md")
    if not log_file.exists():
        return 0
    return sum(
        1 for line in log_file.read_text(encoding="utf-8").splitlines()
        if line.startswith("## Heartbeat #")
    )


def write_heartbeat_log(number, sessions, results):
    log_dir = BACKSTAGE / "stage-manager" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"heartbeat_{today()}.md"

    now = now_utc().strftime("%H:%M UTC")

    lines = []
    if not log_file.exists():
        lines.append(f"# Heartbeat Log — {today()}\n")

    lines.append(f"## Heartbeat #{number} — {now}\n")
    for actor in ACTORS:
        if actor in sessions:
            state = sessions[actor]["state"]
            result = results.get(actor, "")
            lines.append(f"- {actor}: {state} {result}")
        else:
            lines.append(f"- {actor}: no session")
    lines.append("")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\n  Logged heartbeat #{number} to {log_file}")


def write_sessions_json(sessions):
    """Write actor -> session mapping for downstream tools."""
    mapping = {}
    for actor in ACTORS:
        info = sessions.get(actor)
        if info:
            mapping[actor] = {
                "session_id": info["session_id"],
                "state": info["state"],
            }

    out_file = BACKSTAGE / "stage-manager" / "sessions.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)
    print(f"  Wrote session map to {out_file}")


# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_heartbeat(force_new=False):
    """Main heartbeat: create or continue sessions for all actors."""
    print(f"=== Heartbeat — {today()} {'(force-new)' if force_new else ''} ===\n")

    # Merge all ready PRs first so new sessions start from latest main
    auto_merge_all()
    print()

    # Increment round number — heartbeat is the single authority
    round_number = increment_round_number()
    print(f"  Authoritative round: {round_number}\n")

    # Ensure workspace exists
    ensure_workspace()

    # Deliver announcements
    print("=== Delivering announcements ===\n")
    deliver_announcements()
    print()

    # Deliver mail
    print("=== Delivering mail ===\n")
    deliver_mail()
    print()

    sessions = find_actor_sessions()
    hb_number = get_heartbeat_number() + 1
    results = {}

    # Report sabbatical counters
    sabbaticals = load_sabbaticals()
    if sabbaticals:
        print("=== Sabbatical status ===\n")
        for actor_name, sab_info in sabbaticals.items():
            count = sab_info.get("sessions_since_sabbatical", 0)
            taken = sab_info.get("sabbaticals_taken", 0)
            print(f"  {actor_name}: {count}/{SABBATICAL_INTERVAL} sessions (sabbaticals taken: {taken})")
        print()

    for actor in ACTORS:
        info = sessions.get(actor)

        needs_new = False
        reason = ""

        if force_new:
            needs_new = True
            reason = "forced"
        elif not info:
            needs_new = True
            reason = "no session"
        elif info["state"] in ("COMPLETED", "FAILED"):
            needs_new = True
            reason = f"previous {info['state'].lower()}"
        elif is_expired(info):
            needs_new = True
            reason = "expired (>12h)"
        elif has_infra_changed(parse_sha_from_title(info.get("title", ""))):
            needs_new = True
            reason = "infra changed on main"

        if needs_new:
            # Try to merge the actor's PR before creating a new session
            merge = merge_actor_pr(actor)

            if merge == "merged":
                reason += ", merged PR"
            elif merge == "closed-conflict":
                reason += ", closed conflicting PR"

            # No longer skip on conflict — we close the old PR and start fresh
            # Check if this actor is due for a sabbatical
            if needs_sabbatical(actor):
                print(f"  {actor}: {reason} — due for sabbatical, creating sabbatical session")
                try:
                    create_sabbatical_session(actor)
                    results[actor] = f"-> sabbatical ({reason})"
                except Exception as e:
                    print(f"  ERROR: {e}")
                    results[actor] = f"-> error: {e}"
            else:
                print(f"  {actor}: {reason} — creating new session")
                try:
                    create_session(actor)
                    increment_actor_session_count(actor)
                    results[actor] = f"-> new ({reason})"
                except Exception as e:
                    print(f"  ERROR: {e}")
                    results[actor] = f"-> error: {e}"
            continue

        # Active session — check if its PR has conflicts and try to resolve
        pr_num = find_actor_pr(actor)
        if pr_num:
            detail = get_pr_details(pr_num)
            if detail.get("mergeable") == "CONFLICTING":
                branch = detail.get("headRefName", "")
                send_conflict_resolution(info["session_id"], actor, pr_num, branch)
                results[actor] = "-> conflict resolution sent"
                continue

        # Active session -> send heartbeat
        try:
            send_heartbeat_message(info["session_id"], actor, hb_number)
            results[actor] = "-> sent"
        except Exception as e:
            print(f"  ERROR for {actor}: {e}")
            results[actor] = f"-> error: {e}"

    # Re-fetch to include newly created sessions
    updated = find_actor_sessions()
    write_heartbeat_log(hb_number, updated, results)
    write_sessions_json(updated)


def cmd_status():
    """Show current session status."""
    head = get_head_sha(short=True)
    print(f"=== Theater Status === (main @{head})\n")

    sabbaticals = load_sabbaticals()

    sessions = find_actor_sessions()

    if not sessions:
        print("No sessions found.")
        return

    for actor in ACTORS:
        sab = sabbaticals.get(actor, {})
        count = sab.get("sessions_since_sabbatical", 0)
        taken = sab.get("sabbaticals_taken", 0)
        sabbatical_tag = f" [{count}/{SABBATICAL_INTERVAL} to sabbatical, {taken} taken]"

        info = sessions.get(actor)
        if info:
            expired = " EXPIRED" if is_expired(info) else ""
            session_sha = parse_sha_from_title(info.get("title", ""))
            stale = " STALE" if session_sha and has_infra_changed(session_sha) else ""
            print(f"  {actor}: {info['state']}{expired}{stale}{sabbatical_tag} — {info['title']}")
        else:
            print(f"  {actor}: no session{sabbatical_tag}")


def cmd_sabbatical():
    """Manage actor sabbaticals."""
    if len(sys.argv) < 3:
        print("Usage:")
        print("  heartbeat.py sabbatical list              Show session counters and sabbatical history")
        print("  heartbeat.py sabbatical reset <actor>      Reset session counter for an actor")
        print("  heartbeat.py sabbatical trigger <actor>    Force next session to be a sabbatical")
        sys.exit(1)

    action = sys.argv[2]

    if action == "list":
        sabbaticals = load_sabbaticals()
        if not sabbaticals:
            print("No sabbatical data yet. Counters start after first heartbeat.")
            return
        print(f"=== Sabbatical status (interval: every {SABBATICAL_INTERVAL} sessions) ===\n")
        for actor_name in ACTORS:
            info = sabbaticals.get(actor_name, {})
            count = info.get("sessions_since_sabbatical", 0)
            taken = info.get("sabbaticals_taken", 0)
            last = info.get("last_sabbatical", "never")
            due = "** DUE **" if count >= SABBATICAL_INTERVAL else ""
            print(f"  {actor_name}: {count}/{SABBATICAL_INTERVAL} sessions, {taken} sabbaticals taken (last: {last}) {due}")

    elif action == "reset":
        if len(sys.argv) < 4:
            print("Usage: heartbeat.py sabbatical reset <actor>")
            sys.exit(1)
        actor = sys.argv[3].lower()
        if actor not in ACTORS:
            print(f"  ERROR: unknown actor '{actor}'. Known actors: {', '.join(ACTORS)}")
            sys.exit(1)
        sabbaticals = load_sabbaticals()
        if actor not in sabbaticals:
            sabbaticals[actor] = {"sessions_since_sabbatical": 0, "sabbaticals_taken": 0}
        sabbaticals[actor]["sessions_since_sabbatical"] = 0
        save_sabbaticals(sabbaticals)
        print(f"  {actor}: session counter reset to 0")

    elif action == "trigger":
        if len(sys.argv) < 4:
            print("Usage: heartbeat.py sabbatical trigger <actor>")
            sys.exit(1)
        actor = sys.argv[3].lower()
        if actor not in ACTORS:
            print(f"  ERROR: unknown actor '{actor}'. Known actors: {', '.join(ACTORS)}")
            sys.exit(1)
        sabbaticals = load_sabbaticals()
        if actor not in sabbaticals:
            sabbaticals[actor] = {"sessions_since_sabbatical": 0, "sabbaticals_taken": 0}
        sabbaticals[actor]["sessions_since_sabbatical"] = SABBATICAL_INTERVAL
        save_sabbaticals(sabbaticals)
        print(f"  {actor}: counter set to {SABBATICAL_INTERVAL} — next session will be a sabbatical")

    else:
        print(f"Unknown sabbatical action: {action}")
        sys.exit(1)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    cmds = {
        "heartbeat": cmd_heartbeat,
        "force-new": lambda: cmd_heartbeat(force_new=True),
        "deliver-mail": lambda: (print("[heartbeat] Delivering mail..."), deliver_mail(), print("[heartbeat] Mail delivery done.")),
        "sabbatical": cmd_sabbatical,
        "status": cmd_status,
    }

    if cmd not in cmds:
        print(f"Usage: heartbeat.py {{{','.join(cmds.keys())}}}")
        sys.exit(1)

    if cmd not in ("deliver-mail", "sabbatical") and not API_KEY:
        print("ERROR: JULES_API_KEY not set")
        sys.exit(1)

    cmds[cmd]()


if __name__ == "__main__":
    main()
