---
name: feed-vault
description: Ingest new information into the personal knowledge vault — capture in the daily note, file into atomic notes, connect with wikilinks, update the index. Use whenever the user says to feed the vault, add info, log something, or save knowledge.
---

# Feed Vault

Run the capture → file → connect → index → review pipeline defined in the vault's `CLAUDE.md`.

## Steps

1. **Daily note:** open `daily/<today YYYY-MM-DD>.md`; if missing, create it from `templates/daily.md`. Append the raw info under "📥 Captured today."
2. **Decide destination(s)** per chunk of info:
   - evergreen concept → `knowledge/` (one idea per file; check for an existing note to extend first)
   - project update → `projects/<project>.md` (update status + append to its Log)
   - link/source → `references/`
3. **Create from templates**, never blank. Fill all frontmatter; convert relative dates to absolute.
4. **Connect:** add `[[wikilinks]]` both ways — new note ↔ existing notes it touches, and list it under "🗂 Filed into" in the daily note.
5. **Index:** add to `INDEX.md` "Recently added" (newest first), bump section counts, extend the tag cloud if a new tag appeared.
6. **Dashboard:** run `python3 .dashboard/generate.py` from the vault root to refresh `dashboard.html`.
7. **Commit:** `git add -A && git commit` with a message like `feed: <topics>`.
8. **The doorway:** report to the user exactly what was captured, which notes were created/updated, and what got linked.
