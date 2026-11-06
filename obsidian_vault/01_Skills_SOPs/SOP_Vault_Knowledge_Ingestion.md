---
title: SOP - Obsidian Knowledge Ingestion & WikiLinking
date: 2026-10-31
tags: [sop, obsidian, memory, ingestion, rag]
related: ["[[Obsidian_Memory_Architecture]]", "[[Jessica_Identity]]"]
---

# SOP - Obsidian Knowledge Ingestion & WikiLinking

### Purpose
Standardizes how Jessica structures, indexes, and cross-references new knowledge ingested into `obsidian_vault/`.

### Formatting Rules
1. **Frontmatter Requirement**:
   - Every file must begin with valid YAML containing `title`, `date`, `tags`, and `related`.
2. **WikiLinking Syntax**:
   - All interconnected concepts must use `[[Target_Note_Title]]` format.
   - For example, link to [[Windows_Administration]] or [[RTX_4060_Telemetry_Rules]].
3. **Directory Placement**:
   - `00_Identity/`: Core identity and directives.
   - `01_Skills_SOPs/`: Operational rules, action plans, triage workflows.
   - `02_Knowledge_Base/`: Technical references, hardware specs, network architectures.
   - `03_Daily_Logs/`: Automated command executions and session histories.
4. **Vector Index Invalidation**:
   - When a note is written or edited, `vault_indexer.py` automatically updates TF-IDF vectors and dense embeddings.

Refer to [[Obsidian_Memory_Architecture]] for details on hybrid search math.
