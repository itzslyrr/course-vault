---
title: Task Manager v1 (end-of-week project)
type: project
created: 2026-07-08
status: shipped
tags: [course, task-manager, adr, project]
related: ["[[the-doctor]]", "[[overview]]"]
source: ~/vault/projects/task-manager/
---

# Task Manager v1 — Week 2 end-of-week project

**One-liner:** the instructor's end-of-week build — a working **Version 1 task manager** (a single-screen app) delivered together with a **set of 5 ADRs** that justify every design choice. Decisions-first, exactly as the course teaches.

## What shipped
- **The app** (`~/vault/projects/task-manager/app.html`) — self-contained HTML/JS, runs by double-click, saves to `localStorage`. Does the four things a task list must: **create · list · complete · delete** (+ "clear completed"), newest task on top, one screen.
- **The ADR set** (the graded half):
  1. **v1 stack** — a self-contained web app; defer SvelteKit + SQLite to v2 (when sync forces a server)
  2. **Newest-first** — no manual reorder in v1
  3. **Data model** — `{id, text, done, createdAt}`, one JSON array in one localStorage key
  4. **v1 scope** — CRUD only; no accounts, sync, due dates
  5. **Completed-visible** — done tasks stay struck-through, with "clear completed"
- **wi-task-crud** marked **shipped**; sync deferred to v2.

## Why it's a good submission
Every choice is a written decision, not an accident — and the whole project **passed the [[the-doctor]]** (clean bill of health), proving the notes obey the vault rules. This is the course's thesis in one deliverable: *the AI drafts, the human decides, the decisions are recorded, a check enforces the rules.*

## Log
- 2026-07-08 — Built app + 5 ADRs + work item in `~/vault/projects/task-manager/`; doctor clean; committed to the course vault.
