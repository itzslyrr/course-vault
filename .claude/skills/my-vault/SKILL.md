---
name: my-vault
description: The vault tool. Use when the user says "save this", "record this decision",
  "we decided", or asks "what do I know about...". Reads run free. Every write stops for review.
---

# My Vault

Three verbs. Pick by what the user asked. Follow this vault's conventions in `CLAUDE.md`
(frontmatter: title, type, created, tags, related, source · kebab-case files · dates YYYY-MM-DD).

## CAPTURE (write) · "save this..."
1. Create `knowledge/<kebab-title>.md` from `templates/note.md`. Frontmatter: `title`, `type` (`note` for a learning, `reference` for a link/source — pick what fits), `created`, `tags`, `related`, `source`.
2. Connect it: add `[[wikilinks]]` both ways between the new note and any existing note it touches.
3. Add it to `INDEX.md` "Recently added" (newest first) and bump the section count.
4. Show what you made, then **STOP**. The user reviews the `git diff` and commits. You never commit.

## RECORD A DECISION (write) · "record this decision", "we decided..."
1. Create `decisions/adr-NNN-<slug>.md` with the next free number. Frontmatter: `title`, `type: adr`, `status: proposed`, `created`, `tags`, `related`, `source`. Body: **Context · Decision · Consequences**.
2. Link it from `INDEX.md`, and from the related project note's `related:` + Log if it belongs to one.
3. Show what you made, then **STOP**. The user reviews the `git diff` and commits. You never commit.

## RECALL (read) · "what do I know about..."
1. Read `INDEX.md` and follow its links — into `knowledge/`, `projects/`, `references/`, and `decisions/`.
2. Answer and **cite** the notes you used. Read only. **No writes.**

---

*Sibling of `feed-vault`: `feed-vault` runs the full daily capture→file→connect→index→commit pipeline; `my-vault` is the quick verb-triggered tool for a single save, decision, or lookup. Both obey the house rule — writes stop for review.*
