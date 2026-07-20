---
title: 4-Week Course — Overview
type: course
created: 2026-07-06
status: active
tags: [course, ai-workflow, knowledge-management]
related: ["[[week-1]]", "[[next-gen-warfare]]", "[[warhouse-vault]]"]
source: conversation (2026-07-06)
---

# 🎓 4-Week Course — Overview

**What:** a 4-week hands-on course; the work products live in the `BASH 1` workspace (terminal, git/GitHub, and AI-assisted knowledge building).

## Timeline

| Week | Dates | Analysis | Status |
|---|---|---|---|
| **Week 1** | Mon Jun 29 – Sun Jul 5 | [[week-1]] | ✅ done |
| **Week 2** | Mon Jul 6 – Sun Jul 12 | week-2 (due Mon Jul 13) | ▶️ in progress |
| **Week 3** | Mon Jul 13 – Sun Jul 19 | week-3 (due Mon Jul 20) | ▶️ in progress |
| **Week 4** | Mon Jul 20 – **Thu Jul 23 (final day)** | week-4 | ▶️ in progress |

## Week 2 progress (in flight)

- **Day 5 (Jul 6)** — built the `my-vault` skill (three verbs: capture · record-a-decision · recall) and learned [[the-house-rule]]: reads run free, writes wait for review. Recorded [[the-house-rule]] + ADR-001 (a `decisions/` folder). Visual explainer: `course/day5-explainer.html`.
- **Day 6 (Jul 7)** — turned the promise into a law with a `PreToolUse` guard hook → [[the-guard-hook]]. Proved it live (blocked a real AI commit).
- **Day 7 (Jul 8)** — built **the doctor** (`doctor.sh`), a read-only rule-checker that turns CLAUDE.md prose into pass/fail checks → [[the-doctor]]. Completes the Week-2 arc: promise → law → inspector.
- **End-of-week project (Jul 8)** — **Task Manager v1**: a working single-screen app + a set of 5 ADRs → [[task-manager]]. Decisions-first, doctor-clean.
- **Jul 8** — consolidated the vault into one folder, backfilled Day 5/6 records, added a finish-sound.

## Week 3 progress (in flight)

- **Day 9 (Jul 13)** — built **the doorway**: a `vault` CLI that checks every write *at the entry* (before it lands), complementing the doctor (which checks after). Rewired the AI's skill to use it → [[the-doorway-cli]].
- **Day 10 (Jul 14)** — **bricked up the wall**: gave the guard a **second law** so direct writes into the vault's note zones are blocked (notes must use the doorway), while tools stay editable and reads run free → [[the-second-law]].
- **Day 11 (Jul 15)** — **the doctor at the counter**: `vault capture` now validates the form *before* filing (required title · type repair · zone default · non-sensitive only), landing every note as `status: proposed` → [[the-doctor-at-the-counter]].
- **Day 12 (Jul 16)** — **the door reads both ways** + **the three-channel loop**: the CLI gains its read side (search/recent/tree) and end-of-week project **The Pulse** ships (live X data + a free AI summary via headless Claude Code) → [[the-pulse]].

## Week 4 progress (in flight)

- **Day 13 (Jul 20)** — **the face**: gave the vault a *frontend* — channel ③ ("perceive") in visual form. Chose **SvelteKit** against a scorecard (readable output = stays mine; same as the real product), learned the words of design (UX/UI, hierarchy, affordance, state…), and sketched the "recent notes" view as a boxes-only **wireframe** → [[the-face-frontend]]. Day 14 designs it, Day 15 builds it.

## Deliverables

- **Weekly analysis** — at the end of each course week, a `course/week-N.md` note analyzing what was done, worked on, and learned (built from that week's daily notes, project logs, and git history).
- **Final summary — Thursday, July 23, 2026:** a complete course summary in two versions:
  1. **Personal** — everything the owner did, worked on, and learned across the 4 weeks
  2. **Team-facing** — a shareable presentation-style summary for the team

## How this stays current
Daily work feeds the vault (standing rule in the workspace CLAUDE.md); weekly analyses are compiled every Monday for the week before; scheduled reminders back this up. Everything traces back to daily notes and git commits — no reconstruction from memory.
