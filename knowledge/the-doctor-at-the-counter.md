---
title: The Doctor at the Counter (validate before you file)
type: note
created: 2026-07-15
tags: [ai-workflow, knowledge-management, cli]
related: ["[[the-doctor]]", "[[the-doorway-cli]]", "[[the-second-law]]"]
source: conversation (UAEN Week 3 Day 11, 2026-07-15)
---

# The Doctor at the Counter — check the form before filing

Day 7's [[the-doctor]] checked notes *after* they were filed. Day 9's [[the-doorway-cli]]
made the counter the only door. But the counter still filed *whatever it was handed*.
Day 11 posts the doctor **at the counter**: `vault capture` now validates the form
**before** it writes, so every note that lands is already well-formed.

## The four checks (inside the capture verb)
1. **Required title** — an empty title is refused with a fix message.
2. **Valid type, with repair** — must be `note`/`task`/`idea`; a wrong-case near-miss
   (`Task`) is **lowercased**, not rejected.
3. **Allowed zone, with default** — must be `inbox/`/`knowledge/`/`tasks/`; an empty zone
   **defaults to `inbox/`**.
4. **Non-sensitive only** — anything marked `sensitive` is refused. The vault's prime
   rule is now *enforceable*, not just written on a wall.

On any hard fail → **refuse + write nothing**, with a message that says how to fix it.
On pass → file as **`status: proposed`** (ready for the human to sign).

## Repair vs. reject
The doctor **repairs shape, never content**: it will lowercase a type or default a zone,
but it will *never* invent a title you didn't write.

## Enforce in the CLI, describe in the skill
Same split as [[the-second-law]]: the `my-vault` skill *describes* the target shape
(`--type note|task|idea --zone …`) so the AI sends it right; the CLI *enforces* it so it's
true even when the AI gets it wrong. Types grew in lockstep across `bin/vault`,
`doctor.sh`, and `CLAUDE.md` (they move together).

## The governed write path (now complete)
> your sentence → the skill → the counter → **the doctor (checks the form)** → the vault (`proposed`) → your signature

## See also
- [[the-doctor]] (Day 7) · [[the-doorway-cli]] (Day 9) · [[the-second-law]] (Day 10)
