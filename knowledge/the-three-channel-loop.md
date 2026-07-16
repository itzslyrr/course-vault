---
title: The three-channel loop
type: note
created: 2026-07-16
tags: [ai-workflow, knowledge-management, cli, course]
related: ["[[the-doorway-cli]]", "[[the-house-rule]]", "[[the-door-reads-both-ways]]", "[[the-eight-kb-moves]]"]
source: conversation (UAEN Week 3 Day 12 handbook, 2026-07-16)
---

# The three-channel loop — one loop every project runs on

Working with an AI on a real build is one loop with three channels:

1. **Command** (you → AI) — you chat, research, decide. Judgment starts here.
2. **Action** (AI → world) — the AI acts **only** through the one governed doorway (the `vault` CLI): records, plans, builds. Nothing bypasses it.
3. **Perception** (you ↔ the surface) — you run what was made and gate it on your surface (the vault, a page, the app), and what you see sets up the next command.

The rule that makes it safe: **autonomy grows by widening ②, and the system stays human by strengthening ③.** Let the AI do more through the door — but only as far as you can still perceive and gate the result. Widen action without deepening perception and you get output nobody can audit (*vibe-slop*); keep them in step and you get a real thing built on a trail you can check.

## The pieces that hold it up
- **The surface** — any dual-legible artifact you *and* the AI both read and write (the vault, a page, a button). The load-bearing idea of the whole program: it's what keeps the system human.
- **The doorway / CLI** — the single auditable path action flows through ([[the-doorway-cli]]). Channel ②.
- **The Hook** — deterministic, fail-closed enforcement; blocks any write that skips the door ([[the-guard-hook]], [[the-second-law]]).
- **The doctor** — the write-*format* check: required fields · known type · real zone, before anything is recorded ([[the-doctor-at-the-counter]]).
- **The Human Gate** — you. The AI proposes; you ratify. The author never signs off its own work ([[the-house-rule]]).

**Trustworthy autonomy = judgment (the Gate) + enforcement (the Hook) + one doorway (the CLI).**

## Why it matters
It names *where* each safeguard lives so you can lean on the AI without losing the thread — and it tells you which channel to invest in next. Day 12's work was strengthening channel ③: giving the door a read side so perception has something to run on. → [[the-door-reads-both-ways]]

## See also
- [[the-door-reads-both-ways]] · [[the-doorway-cli]] · [[the-house-rule]] · [[the-second-law]] · [[the-eight-kb-moves]]
