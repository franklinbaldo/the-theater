#!/usr/bin/env python3
"""
heartbeat.py — The November Log
Orchestrates each session cycle: reads actor state, sends to Jules API,
delivers mail, updates logs.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

BACKSTAGE = Path("backstage")
SESSIONS = Path("sessions")
ACTORS = ["claire", "owen", "leo", "delta-v", "stage-manager", "franklin", "roy", "alexis", "nathan"]

JULES_API_URL = os.environ.get("JULES_API_URL", "")
JULES_API_KEY = os.environ.get("JULES_API_KEY", "")


def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def deliver_mail():
    """Move outbox messages to recipient inboxes."""
    for actor in ACTORS:
        outbox = BACKSTAGE / actor / "mail" / "outbox"
        if not outbox.exists():
            continue
        for message in outbox.iterdir():
            if not message.is_file():
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


def build_actor_prompt(actor: str, round_number: int) -> str:
    """Assemble the full context prompt for an actor."""
    soul = read_file(BACKSTAGE / actor / "SOUL.md")
    experience = read_file(BACKSTAGE / actor / "EXPERIENCE.md")
    state = read_file(BACKSTAGE / "STATE.md")
    promptbook = read_file(Path("PROMPTBOOK.md"))
    plan = read_file(BACKSTAGE / "franklin" / "PLAN.md") if actor != "franklin" else ""

    # Read inbox
    inbox_path = BACKSTAGE / actor / "mail" / "inbox"
    inbox_contents = ""
    if inbox_path.exists():
        for msg in sorted(inbox_path.iterdir()):
            if msg.is_file():
                inbox_contents += f"\n---\n**{msg.name}**\n{msg.read_text()}\n"

    # Read latest session
    session_files = sorted(SESSIONS.glob("*.md"))
    latest_session = read_file(session_files[-1]) if session_files else ""

    prompt = f"""# Heartbeat — Round {round_number}
## {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

---

## YOUR SOUL

{soul}

---

## YOUR EXPERIENCE (long-term memory)

{experience or '*(no entries yet)*'}

---

## THE WORLD

### PROMPTBOOK (world rules)
{promptbook}

### STATE (what is fixed, what is open)
{state}

{'### FRANKLIN\'S PLAN' + chr(10) + plan if plan else ''}

---

## LATEST SESSION

{latest_session}

---

## YOUR INBOX

{inbox_contents or '*(no messages)*'}

---

## YOUR SESSION — Round {round_number}

You are {actor}. Follow this sequence exactly, in order.

### STEP 1 — Read inbox
You have already received your inbox above. Read every message.

### STEP 2 — Think
Write `backstage/{actor}/notes/think_{round_number:03d}.md`.
Speak as your character-actor. What does the latest session mean to you?
What do you notice? What do you feel about the direction of the play?
What do you want? Do not perform. Think.

### STEP 3 — Read inbox again
Re-read your messages after thinking. Add any new observations to your think file.

### STEP 4 — Plan
Write `backstage/{actor}/notes/plan_{round_number:03d}.md`.
What will you do this session? Who will you write to and why?
What are you trying to accomplish or influence?

### STEP 5 — Execute
Do what you planned:
- Send mail to `backstage/{actor}/mail/outbox/TO_{{recipient}}_{{subject}}.md`
- Update `backstage/{actor}/EXPERIENCE.md` with anything new you believe
- Write your session log to `backstage/{actor}/logs/session_{round_number:03d}.md`

### STEP 6 — Hobbies
Create or continue something in `backstage/{actor}/hobbies/`.
This has nothing to do with the play. It is yours. Define your hobby whenever you want.
If you have no hobby yet, this is the round you might find one.

---

You may only edit files inside `backstage/{actor}/`.
Do not delete files — move to `backstage/{actor}/retracted/` if needed.
"""
    return prompt


def run_heartbeat():
    round_number = int(os.environ.get("ROUND_NUMBER", 1))
    print(f"[heartbeat] Round {round_number} — {datetime.utcnow().isoformat()}")

    # Step 1: Deliver pending mail
    print("[heartbeat] Delivering mail...")
    deliver_mail()

    # Step 2: Build prompts and call Jules API for each actor
    for actor in ACTORS:
        print(f"[heartbeat] Processing actor: {actor}")
        prompt = build_actor_prompt(actor, round_number)

        # Write prompt to actor's inbox as context (for debugging / audit)
        prompt_log = BACKSTAGE / actor / "logs" / f"prompt_{round_number:03d}.md"
        prompt_log.parent.mkdir(parents=True, exist_ok=True)
        prompt_log.write_text(prompt, encoding="utf-8")

        # TODO: Send to Jules API
        # response = call_jules_api(actor, prompt)
        # process_response(actor, response)

    print("[heartbeat] Done.")


if __name__ == "__main__":
    run_heartbeat()
