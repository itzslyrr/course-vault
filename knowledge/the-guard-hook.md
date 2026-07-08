---
title: The Guard Hook (promise → law)
type: note
created: 2026-07-08
tags: [ai-workflow, knowledge-management, hooks]
related: ["[[the-house-rule]]", "[[the-eight-kb-moves]]"]
source: conversation (UAEN Week 2 Day 6, 2026-07-08)
---

# The Guard Hook — turning a promise into a law

Day 5's [[the-house-rule]] made the AI *promise* to stop before a write. A **hook** makes that stop a **law** — enforced from outside the AI, every time, whether or not the AI remembers.

## What a hook is
A script the system runs **before** every action the AI takes (`PreToolUse`). It reads what the AI is about to do and returns a verdict as an **exit code**:
- **`exit 2`** → 🚫 blocked (the command never runs; a reason is shown)
- **`exit 0`** → ✅ allowed (runs normally)

## The guard we built (`vault-write-guard.sh`)
Two laws, matched against the command text:
1. **`git commit` / `git push`** → blocked. *Committing is the human's signature.*
2. **`rm …vault`** → blocked. *Deleting in the vault needs your hands.*
Everything else falls through to `exit 0` and runs free — so reads and lookups are untouched.

## Registration
A hook only fires once it's registered in `~/.claude/settings.json` under `PreToolUse` with `"matcher": "Bash"`. Written-but-unregistered = a scarecrow.

## Why it matters (promise vs. law)
| | promise (skill) | law (hook) |
|---|---|---|
| lives | inside the AI (a STOP line) | outside the AI (a script) |
| if the line is deleted | nothing stops it | the guard still blocks |

**Key insight:** a skill is a promise the AI *makes*; a hook is a wall the system *builds*. The guard only checks what the AI **does**, never what a note **says** — so a wrong `type` or a missing link walks right past it (that gap is the next lesson).

## Fail-closed
When a guard is unsure, it blocks by default. The bridge stays up unless you lower it. Proven live: the guard blocked a real AI `git commit` attempt with the exact human-authored reason.

## See also
- [[the-house-rule]] — the promise this hook enforces
- [[the-eight-kb-moves]] — "the doorway" is this rule as one of the eight moves
