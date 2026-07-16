---
title: The door reads both ways
type: note
created: 2026-07-16
tags: [ai-workflow, knowledge-management, cli, retrieval, course]
related: ["[[the-doorway-cli]]", "[[the-three-channel-loop]]", "[[the-doctor-at-the-counter]]"]
source: conversation (UAEN Week 3 Day 12, 2026-07-16)
---

# The door reads both ways — retrieval is the other half of the doorway

The [[the-doorway-cli|doorway]] began as a **write-only** door: `capture`, `adr`, `plan`, `task`, `done` — every one a checked write. Its help text admitted the gap: *"reads arrive on Day 11."* A door you can only put things *into* is a drawer, not a doorway. Day 12 added the read side.

## The read verbs (channel ③ · perception)
Reads run **free** — no gate, no receipt, nothing written. They only look, so they belong on the perception channel, not the action channel.

| verb | what it answers |
|---|---|
| `vault search <term>` | full-text, ranked **title > tag > body** |
| `vault recent [n]` | what was I just working on |
| `vault tree` | the whole vault as a table of contents |
| `vault open <slug>` | show me this one note |
| `vault backlinks <slug>` | what points *at* this note |
| `vault related <slug>` | notes sharing a tag, most-shared first |
| `vault tags [tag]` | the tag cloud, or every note under one tag |

## The asymmetry that matters
Writes are **fail-closed**: refuse with a reason, exit 2, change nothing. Reads are **fail-open**: they never write, so they need no gate — the worst a bad read does is show you nothing. Enforcement lives on the write path *because that's the only path that can do harm.* Putting a gate on reads would only slow perception, the one channel you want to strengthen.

## Why it matters
Retrieval is what makes a growing vault usable instead of a write-only pit. It also completes [[the-three-channel-loop]]: the door now serves both action (②, the checked writes) and perception (③, the free reads), so the loop can actually close — you run `search`/`recent`, see the state, and issue the next command.

## See also
- [[the-doorway-cli]] — the write side of the same door
- [[the-three-channel-loop]] — where reads sit in the loop
- [[the-doctor-at-the-counter]] — what still guards the writes
