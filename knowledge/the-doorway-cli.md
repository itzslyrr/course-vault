---
title: The Doorway (a CLI that checks before the write)
type: note
created: 2026-07-13
tags: [ai-workflow, knowledge-management, cli]
related: ["[[the-doctor]]", "[[the-guard-hook]]", "[[the-house-rule]]"]
source: conversation (UAEN Week 3 Day 9, 2026-07-13)
---

# The Doorway — one entrance, checked before anything lands

Day 7's [[the-doctor]] checks the notes **after** they're written. The **doorway** (a `vault` CLI) checks the same rules **before** anything lands — a single, guarded entrance that both the human and the AI use.

## What it is
`~/vault/bin/vault` — one bash script with four **write verbs**, each fail-closed:
- **capture** `"words" [--type learning|reference]` — new knowledge note
- **adr** `<project> "decision"` — next-numbered ADR, status proposed
- **task** `<project> "name"` — a `wi-` work item, status planned
- **done** `<project> <wi-slug>` — flip a work item to done
Plus **help**, and it refuses unknown verbs.

## The rule it embodies
Every write is **checked at the door**:
- refuse → one clear reason to **stderr**, **exit 2**
- accept → a **receipt** to stdout, **exit 0**, note written *with* full frontmatter and an index link

Proven with "three bad parcels": empty words · unknown type · duplicate → three refusals, exit 2 each.

## Before vs after
| | checks… | when |
|---|---|---|
| [[the-doctor]] | the files | **after** they're written |
| **the doorway** | the write itself | **before** it lands |

## Why it matters
Same rules, enforced at the entrance, for **both** hands — the AI's skill was rewired to run `vault capture`/`vault adr` instead of hand-writing files, so the human and the AI stand in the same line. It extends the week's through-line: enforcement belongs where it can't be skipped. The wall still has a hole (you can still write files directly, bypassing the door) — Day 10 bricks it up.

## See also
- [[the-doctor]] · [[the-guard-hook]] · [[the-house-rule]]
