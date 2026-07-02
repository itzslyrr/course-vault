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
├── daily/         ← daily capture log, YYYY-MM-DD.md
├── knowledge/     ← atomic evergreen notes
├── projects/      ← ongoing work, one file per project
├── references/    ← external sources & links
├── templates/     ← skeletons: daily, note, project, reference
└── .claude/skills/feed-vault/  ← the feeding pipeline as a skill
```

Everything is plain markdown under git. Commit after each feeding session with a message describing what was added.
