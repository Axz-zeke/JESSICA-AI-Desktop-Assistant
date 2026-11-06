---
title: Obsidian Memory Architecture & RAG Retrieval
date: 2026-10-31
tags: [memory, rag, embeddings, tfidf, obsidian]
related: ["[[SOP_Vault_Knowledge_Ingestion]]", "[[RTX_4060_Telemetry_Rules]]"]
---

# Obsidian Memory Architecture & RAG Retrieval

Jessica treats the local Obsidian Vault as her permanent external episodic memory and knowledge base. 

### Hybrid Vector & Keyword Retrieval
1. **Dense Vector Embeddings**:
   - Extracted using a lightweight PyTorch neural embedding model trained from scratch.
   - Embeddings map semantic intent vectors into cosine similarity space.
2. **Sparse TF-IDF Keyword Scoring**:
   - Ensures precise exact-match scoring for technical terms (e.g., `RTX 4060`, `1.1.1.1`, `TJunction`, `psutil`).
3. **Hybrid RAG Score**:
   $$\text{Score} = 0.55 \cdot \text{DenseCosineSim} + 0.45 \cdot \text{NormalizedTFIDF}$$

### Note Hierarchy
- `00_Identity/`: Persona specifications, core directives, hardware bounds.
- `01_Skills_SOPs/`: Executable Standard Operating Procedures.
- `02_Knowledge_Base/`: Foundational reference documentation.
- `03_Daily_Logs/`: Automated timestamped command traces and audit reports.

See [[SOP_Vault_Knowledge_Ingestion]] for the markdown formatting guidelines.

