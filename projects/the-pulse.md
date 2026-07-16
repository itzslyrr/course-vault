---
title: The Pulse
type: project
created: 2026-07-16
status: active
tags: [the-pulse, course, day-12, ai-workflow, cli]
related: ["[[the-three-channel-loop]]", "[[the-door-reads-both-ways]]", "[[the-doorway-cli]]"]
source: conversation (UAEN Week 3 Day 12 — "Ship Something Real")
---

# The Pulse

**One-liner:** the Day 12 "Ship Something Real" build — give it a topic and it shows, in
one clean view, what people are saying about it right now, then an **AI-synthesized**
summary on top. My topic: **AI agents**. First platform: **X (Twitter)**.

## Current status
As of 2026-07-16: **shipped and running.** Live X data flows via `apidirect.io`; the
"Pulse" summary is synthesized by **headless Claude Code** (`claude -p`) — real Claude, no
API key, free on my existing login — with local-Ollama and offline-heuristic fallbacks so
it never comes back empty. Professional space-themed UI with a pulsing summary card.

## Key facts
- **Code lives outside the vault:** `~/Desktop/BASH1/the-pulse/` (own git repo). Python
  stdlib server (`server.py`) + one HTML page (`index.html`) — no dependencies, no install.
- **Keys stay server-side, never in code:** `APIDIRECT_KEY` (data) and any summary key live
  in a gitignored `.env`; the browser never sees them.
- **Summary engine is swappable** via `PULSE_AI`: `claude` (headless Claude Code) ·
  `ollama` (local model) · `heuristic` (offline) · `auto` (default). Card is labelled
  honestly by source — real models glow "AI summary", the offline path reads "auto-summary".
- **The decision trail lives in `~/vault/projects/the-pulse/`**: ADR-001 (fetch + shape),
  ADR-002 (the real apidirect X contract), ADR-003 (free AI summary), a plan, two scopes,
  and 7 work items — all done.
- Milestones met: vault trail · runs + sad path handled · **real data flows** · live demo +
  walkable trail.

## Next steps
- [ ] Optional: install Ollama for a fully-offline real-AI path (no login needed).
- [ ] Optional: "summarizing…" shimmer during the ~6 s headless-Claude wait.
- [ ] Sign (git commit) the app repo and the `~/vault` trail.

## Log
- 2026-07-16 — Built end-to-end on Day 12. Vault trail laid through the `vault` CLI
  (ADR → plan → scope → tasks). App: apidirect proxy, live X data (fixed endpoint to
  `/v1/twitter/posts`), sad-path handling, space UI. Upgrade: AI summary — journeyed from
  paid Anthropic API → local Ollama → **free headless Claude Code**, with an offline
  fallback. Recorded as ADR-002 + ADR-003 in `~/vault`.
