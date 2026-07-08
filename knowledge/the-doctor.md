---
title: The Doctor (rules → checks)
type: note
created: 2026-07-08
tags: [ai-workflow, knowledge-management, hooks]
related: ["[[the-guard-hook]]", "[[the-house-rule]]", "[[the-eight-kb-moves]]"]
source: conversation (UAEN Week 2 Day 7, 2026-07-08)
---

# The Doctor — turning rules into checks

The [[the-guard-hook]] guards what the AI *does*; it never reads what a note *says*. A wrong `type`, a missing `created`, a dead `[[link]]` walk straight past it. **The doctor** closes that gap: a read-only script that checks every note against the vault's written rules and reports what it finds.

## The core idea
Your `CLAUDE.md` prose *is* the spec. Each rule becomes a check that can **pass or fail**:
1. Every note has frontmatter: `title`, `type`, `created`, `tags`.
2. `type` is one of the legal set (`reference · learning · decision · project · adr · work-item`).
3. Filenames are kebab-case.
4. Every `[[link]]` points at a note that exists.

## How it behaves
- **Read-only** — never edits a file, so it sails through the guard hook.
- **One line per problem**, naming the file and the fault (`MISSING created: …`, `UNKNOWN type leraning: …`, `DANGLING missing-note: …`).
- **`exit 0` clean · `exit 2` on findings** — so it can gate a commit.
- **Deterministic** — the same input gives the same answer every time; tired eyes skim a typo, a check never does.

## The routine it creates
**draft → doctor → diff → commit.** By the time your eyes reach the diff, the mechanical problems are already gone — your review time goes to *meaning*, not typos.

## Rules and checks move together
Add a sentence to `CLAUDE.md` → add a check to the doctor. The written rule and its enforcement grow as a pair.

## The three-tool arc (Week 2)
- [[the-house-rule]] — the **promise** (a skill chooses to stop)
- [[the-guard-hook]] — the **law** (a hook forces the stop on what the AI *does*)
- **the doctor** — the **inspector** (a script judges what the note *says*)

## See also
- [[the-guard-hook]] · [[the-house-rule]] · [[the-eight-kb-moves]]
