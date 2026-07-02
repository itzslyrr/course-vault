---
title: Warhouse Vault
type: project
created: 2026-07-02
status: active
tags: [warehouse, inventory, knowledge-management, github]
related: ["[[next-gen-warfare]]", "[[the-eight-kb-moves]]"]
source: https://github.com/itzslyrr/warhouse-vault
---

# Warhouse Vault

**One-liner:** a warehouse parts-inventory knowledge base — markdown notes tracking industrial parts (part number, NATO supply class, warehouse location, supplier, assembly) across two warehouses, with strict never-guess rules.

## Current status
As of 2026-07-02: 12 parts filed across warehouses A and B, organized under 2 assemblies. **4 migrated parts are flagged** with unverified supplier/assembly data, and the PX-9 pump assembly is incomplete (missing pump body, mechanical seal, o-ring set).

## Key facts
- Located at `~/Desktop/BASH 1/warhouse-vault/`, own git repo, pushed to **github.com/itzslyrr/warhouse-vault** (public)
- Structure: `inventory/` (parts + assemblies + index), `warehouses/` (A, B), `templates/part.md`, `CLAUDE.md`
- Rules: non-sensitive content only; every part links to its assembly and warehouse; frontmatter carries `type/part_no/name/nato_class/warehouse`; **flag uncertainty, never guess**
- Assemblies: GX-200 gearbox (6 parts, complete), PX-9 pump (1 part, incomplete)
- Uses the same method as everything else here → [[the-eight-kb-moves]]

## Next steps
- [ ] Verify supplier & assembly for the 4 flagged parts: EM-610-02, HH-472-05, SG-302-03, SK-330-01
- [ ] Complete the PX-9 pump assembly (pump body, mechanical seal, o-ring set)

## Log
- 2026-07-02 — Filed into the personal vault. State: 12 parts, 2 assemblies, 4 verification flags outstanding.
