# CLAUDE.md — Personal Knowledge Vault

This is the owner's personal knowledge vault. It is fed regularly (often daily) with new information. Your job when working here: **capture, file, connect, and keep it navigable.**

## The feeding pipeline

When the owner gives you info to add ("feed the vault with ..."):

1. **Capture** — log it in today's daily note (`daily/YYYY-MM-DD.md`, create from `templates/daily.md` if missing).
2. **File** — extract the durable substance into the right place:
   - `knowledge/` — evergreen facts, concepts, how-tos (one idea per file, atomic)
   - `projects/` — ongoing work with goals and status
   - `references/` — external links, sources, dashboards, repos
3. **Connect** — add `[[wikilinks]]` in `related:` frontmatter and in the body between the new note and existing ones. A note with no links is a dead end.
4. **Index** — add new notes to `INDEX.md` under the right section, newest first in "Recently added."
5. **Dashboard** — run `python3 .dashboard/generate.py` to refresh `dashboard.html` (a PostToolUse hook in the parent project's `.claude/settings.json` also does this automatically on every file write).
6. **The doorway** — summarize what was captured, filed, and linked so the owner can review.

## Conventions

- **File naming:** kebab-case (`hypersonic-weapons.md`), daily notes `YYYY-MM-DD.md`
- **Frontmatter on every note:**
  ```yaml
  ---
  title: Human Title
  type: daily | note | project | reference
  created: YYYY-MM-DD
  tags: [topic1, topic2]
  related: ["[[other-note]]"]
  source: URL or "conversation"   # where the info came from
  ---
  ```
- **Atomic notes:** one concept per file in `knowledge/`. If a daily dump contains three ideas, it becomes three notes.
- **Update, don't duplicate:** before creating a note, check whether one already covers the topic — extend it and bump its `updated:` date instead.
- **Convert relative dates** ("yesterday", "next week") to absolute dates when filing.
- **Never delete owner content** without being asked; git history is the safety net.

## Structure

```
Vault/
├── CLAUDE.md      ← you are here (standing rules)
├── INDEX.md       ← front door: sections + recently added
├── course/        ← 4-week course tracking: overview.md + week-N.md analyses
├── daily/         ← daily capture log, YYYY-MM-DD.md
├── knowledge/     ← atomic evergreen notes
├── projects/      ← ongoing work, one file per project
├── references/    ← external sources & links
├── templates/     ← skeletons: daily, note, project, reference, week
└── .claude/skills/feed-vault/  ← the feeding pipeline as a skill
```

## Course tracking (until 2026-07-23)

This vault tracks the owner's 4-week course (Mon 2026-06-29 → Thu 2026-07-23, see `course/overview.md`):

- **Every Monday** (Jul 13, Jul 20): compile the previous week's analysis into `course/week-N.md` from `templates/week.md`, using that week's daily notes, project Logs, and git history. Update the timeline table in `course/overview.md`.
- **Thursday 2026-07-23 (final day):** produce the full course summary in two versions — personal (everything done/worked on/learned) and team-facing (shareable) — from the four week analyses.
- Week boundaries: W1 Jun 29–Jul 5 · W2 Jul 6–12 · W3 Jul 13–19 · W4 Jul 20–23.

Everything is plain markdown under git. Commit after each feeding session with a message describing what was added, then push — the vault has a public remote at **github.com/itzslyrr/course-vault**.
