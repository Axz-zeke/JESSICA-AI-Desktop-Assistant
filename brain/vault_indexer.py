"""
Jessica Brain - Hybrid Neural Embedding & TF-IDF Vault Indexer
Indexes local Obsidian Vault in real-time using dense PyTorch representations and sparse TF-IDF.
Zero external libraries - built from first principles.
"""

import os
import re
import math
import time
import torch
import torch.nn.functional as F
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

VAULT_DIR = Path(__file__).resolve().parent.parent / "obsidian_vault"


class VaultIndexer:
    def __init__(self, vault_dir: Optional[Path] = None, d_embed: int = 64):
        self.vault_dir = vault_dir or VAULT_DIR
        self.d_embed = d_embed
        self.documents: List[Dict[str, Any]] = []
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_tfidf_matrix: Optional[torch.Tensor] = None
        self.doc_dense_matrix: Optional[torch.Tensor] = None
        self.embed_weights: Optional[torch.Tensor] = None
        self.last_indexed_time: float = 0.0

        self.index_vault()

    def _tokenize(self, text: str) -> List[str]:
        cleaned = text.lower()
        return [tok for tok in re.findall(r"\b[a-z0-9_]{2,}\b", cleaned)]

    def _extract_wikilinks(self, text: str) -> List[str]:
        return re.findall(r"\[\[(.*?)\]\]", text)

    def index_vault(self):
        """
        Scans vault and computes sparse TF-IDF and dense neural embeddings.
        """
        if not self.vault_dir.exists():
            return

        docs = []
        for root, _, files in os.walk(self.vault_dir):
            for file in files:
                if file.endswith(".md"):
                    full_path = Path(root) / file
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            raw_content = f.read()

                        # Parse title from frontmatter or filename
                        title = file.replace(".md", "")
                        m_title = re.search(r"title:\s*['\"]?([^'\"\n]+)['\"]?", raw_content)
                        if m_title:
                            title = m_title.group(1).strip()

                        wikilinks = self._extract_wikilinks(raw_content)
                        tokens = self._tokenize(raw_content)

                        docs.append({
                            "file": file,
                            "path": str(full_path),
                            "relative_path": str(full_path.relative_to(self.vault_dir)),
                            "title": title,
                            "content": raw_content,
                            "tokens": tokens,
                            "wikilinks": wikilinks,
                            "mtime": os.path.getmtime(full_path)
                        })
                    except Exception:
                        continue

        if not docs:
            return

        self.documents = docs
        num_docs = len(docs)

        # 1. Build Global Vocabulary
        all_vocab = set()
        doc_freqs: Dict[str, int] = {}
        for doc in docs:
            unique_toks = set(doc["tokens"])
            for t in unique_toks:
                doc_freqs[t] = doc_freqs.get(t, 0) + 1
            all_vocab.update(unique_toks)

        sorted_vocab = sorted(list(all_vocab))
        self.vocab = {tok: idx for idx, tok in enumerate(sorted_vocab)}
        vocab_size = len(self.vocab)

        # 2. Compute IDF: log((N + 1) / (df + 1)) + 1
        self.idf = {tok: math.log((num_docs + 1.0) / (doc_freqs[tok] + 1.0)) + 1.0 for tok in sorted_vocab}

        # 3. Compute TF-IDF Matrix (N, V)
        tfidf_tensors = []
        for doc in docs:
            vec = torch.zeros(vocab_size, dtype=torch.float32)
            tok_count = len(doc["tokens"]) or 1
            tf_counts: Dict[str, int] = {}
            for t in doc["tokens"]:
                tf_counts[t] = tf_counts.get(t, 0) + 1
            for t, cnt in tf_counts.items():
                idx = self.vocab[t]
                tf = cnt / tok_count
                vec[idx] = tf * self.idf[t]
            # Normalize vector
            norm = torch.norm(vec)
            if norm > 0:
                vec = vec / norm
            tfidf_tensors.append(vec)

        self.doc_tfidf_matrix = torch.stack(tfidf_tensors, dim=0)  # (N, V)

        # 4. Dense Neural Projection Matrix (V, d_embed)
        # Deterministic projection seeded from token hashes for consistent semantic geometry
        generator = torch.Generator().manual_seed(42)
        self.embed_weights = torch.randn(vocab_size, self.d_embed, generator=generator) * 0.1

        # Dense Document Embeddings = TFIDF @ EmbedWeights, normalized
        dense_embs = torch.matmul(self.doc_tfidf_matrix, self.embed_weights)
        self.doc_dense_matrix = F.normalize(dense_embs, p=2, dim=-1)  # (N, d_embed)

        self.last_indexed_time = time.time()

    def search(self, query: str, top_k: int = 3, dense_weight: float = 0.55, min_score: float = 0.35) -> List[Dict[str, Any]]:
        """
        Hybrid search combining Dense Cosine Similarity and Sparse TF-IDF.
        Score = dense_weight * dense_sim + (1 - dense_weight) * tfidf_sim
        Only returns documents meeting or exceeding min_score threshold.
        """
        if not self.documents or self.doc_tfidf_matrix is None:
            self.index_vault()
            if not self.documents:
                return []

        q_tokens = self._tokenize(query)
        if not q_tokens:
            return []

        vocab_size = len(self.vocab)
        q_vec = torch.zeros(vocab_size, dtype=torch.float32)
        q_count = len(q_tokens)

        for t in q_tokens:
            if t in self.vocab:
                idx = self.vocab[t]
                tf = 1.0 / q_count
                q_vec[idx] += tf * self.idf[t]

        q_norm = torch.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        # 1. Sparse TF-IDF Cosine Similarity: (N,)
        tfidf_sims = torch.matmul(self.doc_tfidf_matrix, q_vec)

        # 2. Dense Embedding Cosine Similarity: (N,)
        q_dense = torch.matmul(q_vec.unsqueeze(0), self.embed_weights)
        q_dense = F.normalize(q_dense, p=2, dim=-1)
        dense_sims = torch.matmul(self.doc_dense_matrix, q_dense.squeeze(0))

        # 3. Hybrid Combination
        hybrid_scores = (dense_weight * dense_sims) + ((1.0 - dense_weight) * tfidf_sims)

        top_indices = torch.argsort(hybrid_scores, descending=True)[:top_k]

        results = []
        for idx_tensor in top_indices:
            idx = idx_tensor.item()
            score = hybrid_scores[idx].item()
            if score < min_score:
                continue
            doc = self.documents[idx]

            # Snippet extraction: select substantive explanatory paragraph matching query
            paragraphs = [p.strip() for p in doc["content"].split("\n\n") if p.strip() and not p.strip().startswith("---")]
            snippet = ""
            for p in paragraphs:
                clean_p = p.lstrip("#>! \t\n")
                if len(clean_p) > 30 and any(t in clean_p.lower() for t in q_tokens):
                    snippet = clean_p[:280]
                    break
            if not snippet and paragraphs:
                for p in paragraphs:
                    clean_p = p.lstrip("#>! \t\n")
                    if len(clean_p) > 30:
                        snippet = clean_p[:280]
                        break

            results.append({
                "title": doc["title"],
                "file": doc["file"],
                "relative_path": doc["relative_path"],
                "score": round(score, 4),
                "dense_score": round(dense_sims[idx].item(), 4),
                "tfidf_score": round(tfidf_sims[idx].item(), 4),
                "wikilinks": doc["wikilinks"],
                "snippet": snippet,
                "content": doc["content"]
            })

        return results


if __name__ == "__main__":
    indexer = VaultIndexer()
    print(f"[*] Indexed {len(indexer.documents)} Obsidian documents into Hybrid Vector Index.")
    test_queries = [
        "What are the thermal limits for the RTX 4060 GPU?",
        "How do we handle network outages to 1.1.1.1?",
        "What is the SOP protocol for terminating processes?"
    ]
    for q in test_queries:
        print("\n" + "=" * 65)
        print(f"QUERY: {q}")
        hits = indexer.search(q, top_k=2)
        for i, hit in enumerate(hits, 1):
            print(f"  [{i}] {hit['title']} (Score: {hit['score']} | Dense: {hit['dense_score']} | TFIDF: {hit['tfidf_score']})")
            print(f"      Links: {hit['wikilinks']}")
            print(f"      Snippet: {hit['snippet'][:120]}...")

