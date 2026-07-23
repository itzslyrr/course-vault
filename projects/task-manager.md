---
title: Task Manager v1 (end-of-week project)
type: project
created: 2026-07-08
status: shipped
url: apps/task-manager/index.html
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

## v2 — Kanban board
Instructor's next brief: research Kanban, apply it to v2. Built `app-v2.html` — a three-column board (**To Do / In Progress / Done**), cards move by **drag-and-drop or ◀ ▶ buttons**, with a **WIP limit of 3** on In Progress (the defining Kanban control). New `column` data model migrates v1 tasks; per-column newest-first; seeded with sample cards for instant preview. Documented in **ADR-006 → 010** + `wi-kanban-board` (shipped). Notably, v2 was originally "sync" — the instructor re-prioritized to Kanban, so **sync moved to v3** (recorded in ADR-006).

## v2 on a real stack — SvelteKit + SQLite
Instructor's next brief: put v2 on **SvelteKit + SQLite** (the direction ADR-001 always pointed at). Installed Node 22 (portably), then built a real server-backed app in `~/vault/projects/task-manager/v2-sveltekit/`: SvelteKit UI, **better-sqlite3** database, a **REST API** (GET/POST/PATCH/DELETE), and the **WIP limit enforced on the server** (returns HTTP 409 when In Progress is full). Runs at `localhost:5173` via `npm run dev`; data persists in `tasks.db`. Documented as **ADR-011/012/013**. This server-owns-the-data design is what unlocks v3 (device sync).

## Log
- 2026-07-08 — Built app + 5 ADRs + work item (v1) in `~/vault/projects/task-manager/`; doctor clean; committed.
- 2026-07-08 — Built **v2 Kanban board** (`app-v2.html`) + ADR-006…010 + wi-kanban-board; WIP limit, drag-and-drop, v1 migration; doctor clean; committed.
- 2026-07-08 — Rebuilt **v2 on SvelteKit + SQLite** (`v2-sveltekit/`) + ADR-011…013; REST API, server-side WIP (409), runs at localhost:5180; doctor caught a cross-vault dangling link → fixed → clean.
- 2026-07-08 — Built **v3: multi-user auth** (`v3-sveltekit-auth/`) + ADR-014…017 + wi-multi-user-auth. Username+password, scrypt-hashed, httpOnly session cookies, per-user tasks + per-user WIP. Verified in a real browser (Playwright): register/login/logout, data isolation (bob ≠ alice), persistence, wrong-password rejection. Runs at localhost:5181. Doctor clean.
- 2026-07-14 — Added a **task detail view + image attachments** to v2: click a task → modal with an image upload (data-URL in the DB) and editable notes; migrated the schema (`notes`, `image` columns) and extended the PATCH API. Planned + shipped via a separate `planning` project scope. Runs at localhost:5180.

## v3 — multi-user authentication
Instructor's third brief: **accounts**. Built a real login system on the SvelteKit + SQLite app — register / login / logout, each user gets a private board that persists. Passwords hashed with Node's built-in **scrypt** (no dependency); sessions are **httpOnly cookies** checked on every request in `hooks.server.js`; every task query is scoped by **`user_id`** so users can't see each other's data (proven: "bob" can't see "alice"'s task). Documented as **ADR-014…017**. The through-line holds: the isolation lives in the data-layer queries, so a forgotten filter can't leak data. Screenshots: `course/screenshots/v3-login.png`, `v3-board-alice.png`.
