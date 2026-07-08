---
title: ADR-001 — Keep decisions as numbered ADRs in a decisions/ folder
type: adr
status: proposed
created: 2026-07-06
tags: [knowledge-management, ai-workflow]
related: ["[[the-house-rule]]", "[[the-eight-kb-moves]]"]
source: conversation (UAEN Week 2 Day 5, 2026-07-06)
---

# ADR-001 — Keep decisions as numbered ADRs in a decisions/ folder

## Context
The `my-vault` skill has a "record a decision" verb. The vault had no home for decision
records: `knowledge/` holds evergreen facts, `projects/` holds ongoing work, `references/`
holds links. A decision — what we chose and why — is a distinct, immutable artifact.

## Decision
Store each decision as its own file in a flat `decisions/` folder (matching the vault's
existing flat layout), named `adr-NNN-<slug>.md` with the next free number, `type: adr`,
and a `status:` line (`proposed` → `accepted`/`superseded`). One decision per file.
Cross-link each ADR to the project or note it affects.

## Consequences
- Decisions become greppable, numbered, and linkable — the AI can cite them on recall.
- Adds `adr` as a fourth note type alongside `daily | note | project | reference`.
- Project notes keep their **Log** as the timeline; ADRs hold the *why* behind a choice.
