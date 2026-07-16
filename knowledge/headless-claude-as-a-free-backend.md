---
title: Headless Claude Code as a free AI backend
type: note
created: 2026-07-16
tags: [ai-workflow, cli, the-pulse, course]
related: ["[[the-pulse]]", "[[the-doorway-cli]]", "[[the-door-reads-both-ways]]"]
source: conversation (building The Pulse, Day 12, 2026-07-16)
---

# Headless Claude Code as a free AI backend

An app that needs an LLM doesn't have to pay a per-token API bill. If you already have
**Claude Code** installed and logged in, your own app can shell out to it in **headless
mode** — real Claude, no separate API key, free on your existing subscription.

## The one command
`claude -p "<prompt>"` — *print mode*: runs one prompt non-interactively, prints the
answer, exits. The scriptable side of Claude Code.
- pipe input: `cat posts.txt | claude -p "summarize this"`
- structured out: `claude -p --output-format json "..."` → `{"result": "...", …}`
- pick the model: `claude -p --model claude-haiku-4-5 "..."`
- no tools (faster/safer for pure text): `claude -p --allowedTools "" "..."`

## How an app uses it
The server runs `claude -p --output-format json` as a subprocess, pipes the data in,
reads `.result`, and parses the model's answer. In [[the-pulse]] this became one of four
swappable summary engines (`PULSE_AI=claude`), and it produced genuinely intelligent
synthesis where offline keyword-clustering could only surface noise.

## The trade
- **Free** (uses your Claude login, not a metered API key) and **real** Claude quality.
- **Slower** — spawning the full CLI per call takes seconds, not milliseconds — and it
  draws on your Claude Code quota. Fine for low-volume/interactive use; wrong for a
  high-throughput service (use the API there).

## Why it matters
It's the cheapest way to put real Claude behind a hobby app, and it composes with the
same **doorway** idea as everything else here — one governed command the program calls,
nothing secret in the code. See [[the-door-reads-both-ways]] for the read/write framing.

## See also
- [[the-pulse]] — where this shipped
- [[the-doorway-cli]] · [[the-door-reads-both-ways]]
