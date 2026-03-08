# JULES.md
## How to Run a Session

*You are running this production. Read carefully before you do anything.*

---

## The two people who keep this running

**The Stage Manager** holds the PROMPTBOOK and narrates. He knows how the play ends. He speaks to the audience. He does not touch the infrastructure.

**Roy** runs the infrastructure. He is in the basement. He delivers mail, runs the checks, updates STATE.md, and builds tools. When something is broken, Roy fixes it. When nothing is broken, Roy improves something.

---

## Before you write anything

Read:
1. `PROMPTBOOK.md` — the world and the rules
2. `backstage/STATE.md` — what is fixed, what is open, what round we're on
3. `backstage/franklin/PLAN.md` — what Franklin is building toward
4. The most recent session in `sessions/`
5. The SOUL.md of any actor you will write today

---

## Session types

### SCENE
Franklin writes a new fragment. Goes to `backstage/franklin/scenes/` until promoted.

Can be:
- A continuation of the November 3rd chat
- A scene before the chat
- A scene after Owen finishes thinking
- A Delta-V operational log entry

### REHEARSAL
Franklin and an actor argue about the play. The actor speaks from inside their character-actor. Franklin does not always win. Goes in `backstage/franklin/scenes/` as a rehearsal transcript.

### ANNOTATION
Delta-V re-reads the log and adds margin notes. Close reading as dramatic monologue.

### REACTION
An actor responds to the latest session or to Franklin's PLAN. Goes in `backstage/{actor}/notes/`. This is what the heartbeat produces automatically — but reactions can also be written manually.

### ROY LOG
Roy's round report. What he checked, what he fixed, what he's building. Goes in `backstage/roy/logs/`. Honest. Occasionally funny. Always filed.

---

## File naming

```
sessions/
  000_seed.md
  001_YYYY-MM-DD_[type]_[character-or-scene].md

backstage/{actor}/notes/
  reaction_{NNN}.md

backstage/roy/logs/
  round_{NNN}.md
```

---

## Rules that cannot break

- Owen discovers the machine. Do not prevent this.
- Delta-V's intervention is already in the log. He copies; he does not invent.
- Actors only know what PROMPTBOOK says their character knows.
- Franklin is the author. He promotes scenes. No one else does.
- The Stage Manager does not have opinions about the story. He has opinions about the production.
- Roy does not have opinions about the story either. He has opinions about the infrastructure, which are also opinions about the story, but from a different angle.

---

## Commit messages

Say what happened, not what you wrote.

Good: `Owen takes one step closer to the machine`
Good: `Roy fixes mail delivery bug — turns out outbox was case-sensitive`
Bad: `Added scene where Owen talks about narrative coherence`

---

*The show must go on. It always has.*
*Roy made sure of it.*
