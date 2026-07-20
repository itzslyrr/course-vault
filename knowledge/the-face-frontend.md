---
title: The Face (a frontend for the vault)
type: note
created: 2026-07-20
tags: [ai-workflow, frontend, design]
related: ["[[the-doorway-cli]]", "[[the-eight-kb-moves]]"]
source: conversation (UAEN Week 4 Day 13, 2026-07-20)
---

# The Face — giving the vault a frontend

Weeks 1–3 built the vault's **brain** (notes, the `vault` CLI, the doctor, the guard) — but
it's only met as a list of files in the terminal. **Week 4 gives it a face**: a visual
frontend so notes can be *seen* (grouped, dated, clickable), not just dug for.

## The surface, in three forms
The **surface** is anything the human and the AI can both read and write — it's what keeps
the human in charge. Each week gave it a new form:
- **Weeks 1–2 → the vault** (its memory form)
- **Week 3 → the CLI** (its safe doorway)
- **Week 4 → the page** (its visual form)

A face isn't decoration — it's channel ③ of the loop ("perceive") made real: *command → the
AI acts → you perceive → you command again.*

## Choosing the tool (reasoned, not handed down)
Brainstorm (Plain HTML · React/Next · Astro · SvelteKit) → score against four needs
(easy floor · readable output · reads my files · deploys later) → **choose SvelteKit**.
Two deciding reasons: (1) *you can only trust what you can read* — SvelteKit's output is
among the most readable, so the human stays in control; (2) it's *the real tool* the grown-up
product is built with. Recorded as an ADR (what / why / instead-of). *(Same stack as the
Task Manager v2/v3 — a tool already known.)*

## The words of design
- **UX** = how it *feels* · **UI** = how it *looks* (Day 13 is UX; the look is Day 14)
- **Information architecture** (a place for everything) · **navigation** (always know where
  you are) · **hierarchy** (the most important thing catches the eye first)
- **Affordance** (looks pressable) · **feedback** (reacts so you know it worked) ·
  **state** (design the empty / loading / error screens too — often forgotten)
- **Layout** (where things sit) · **view** (one screen for one job) · **component** (a
  reusable brick, like a note card) · **wireframe** (a boxes-only sketch)

## Wireframe first
A **wireframe** is a rough sketch of a screen — grey boxes and labels only, no colours, no
code. It answers *"what goes where?"* before anyone worries about how it looks, and it
throws away cleanly. Day 13's deliverable: sketch **one view** ("recent notes") in a single
plain-HTML file, designed for the user's *journey* (open → see what's new → click → read),
not for a blank page.

## See also
- [[the-doorway-cli]] · [[the-eight-kb-moves]] · Day 14 designs it · Day 15 builds it in SvelteKit
