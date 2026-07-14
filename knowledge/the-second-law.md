---
title: The Second Law (bricking up the wall)
type: note
created: 2026-07-14
tags: [ai-workflow, knowledge-management, hooks, cli]
related: ["[[the-doorway-cli]]", "[[the-guard-hook]]", "[[the-doctor]]"]
source: conversation (UAEN Week 3 Day 10, 2026-07-14)
---

# The Second Law — the vault gets one door

Day 9's [[the-doorway-cli]] was opt-in: you *could* write notes through the `vault`
counter, but the AI (or an editor, or a script) could still write files directly and
skip every check. Day 10 closes that hole by giving the Day-6 [[the-guard-hook]] a
**second law**.

## The two laws (tool-based)
The `PreToolUse` guard now watches three tools (matcher `Bash|Write|Edit`):
- **Law 1 (Bash):** a command with `git commit`/`git push` → blocked. *Committing is the human's signature.*
- **Law 2 (Write/Edit):** a write into `~/vault/{knowledge,projects,templates,inbox}/` → blocked. *Notes go through the doorway.* **Tool files (`bin/`, `doctor.sh`) are exempt** — the human's review + commit covers those.
- Everything else — reads, non-note writes — runs free.

## Two kinds of things, two kinds of governance
| Thing | Rule |
|---|---|
| **Notes** | must go through the doorway (Law 2 blocks direct writes) |
| **Tools** | drafted by AI, gated by the human's review + commit (Law 1) |
| **Reads** | always free — looking was never the risk |

## The write path (the only road a note can travel)
> your sentence → the skill → the counter (checked) → the vault → your signature

## Proven live
The exact direct write that landed one hour earlier **bounced** (exit 2, "notes go
through the doorway"); the counter still welcomed a `vault capture`; reads answered;
and a `bin/vault` edit passed. The wall is **precise** — it blocks the side door, not
the front door or the reads.

## The remaining hole (homework)
Law 2 watches the **Write/Edit tools**, not Bash file redirection — a raw
`echo … > ~/vault/knowledge/x.md` still slips past. A real hole is a gift for the next lesson.

## See also
- [[the-doorway-cli]] (Day 9) · [[the-guard-hook]] (Day 6) · [[the-doctor]] (Day 7)
