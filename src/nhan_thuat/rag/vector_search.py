"""
Dense Vector Semantic Search Engine for NhanThuat Knowledge Units.
Implements local semantic embedding generation, cosine similarity search,
and persistent vector cache management (knowledge/.vector_cache.json).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from nhan_thuat.rag.normalizer import extract_unit_text_corpus, tokenize


@dataclass
class VectorResult:
    unit_id: str
    score: float  # Cosine similarity (0.0 to 1.0)
    unit: Any


SEMANTIC_ANCHORS: dict[str, list[str]] = {
    "conflict_dispute": ["xung dot", "tranh chap", "mau thuan", "bat dong", "cai va", "dinh cong", "tranh gianh", "doi quyen loi", "bat hoa", "strike"],
    "negotiation_agreement": ["dam phan", "thuong luong", "thoa thuan", "hop dong", "gia ca", "chiet khau", "thoa hiep", "doi tac", "ky ket", "pricing"],
    "leadership_governance": ["lanh dao", "quan tri", "dieu hanh", "chu tich", "giam doc", "ky luat", "quy che", "sop", "phan quyen", "hinh danh", "nhi binh"],
    "personnel_training": ["nhan su", "dao tao", "huan luyen", "khuyen hoc", "tuyen dung", "onboarding", "mentorship", "nang luc", "danh gia", "uon nan"],
    "operations_project": ["cong trinh", "thi cong", "vat tu", "tien do", "hien truong", "cham tre", "che tai", "nha cung cap", "giao hang", "san xuat"],
    "finance_debt": ["tai chinh", "dong tien", "cong no", "doi no", "qua han", "thanh toan", "tien hang", "thu hoi", "chi phi", "loi nhuan", "ngan sach"],
    "rhetoric_persuasion": ["hung bien", "thuyet phuc", "be luan diem", "tu choi", "giai thich", "khach hang", "reframing", "lap luan", "phan bien"],
    "psychology_behavior": ["tam ly", "hanh vi", "nhan thuc", "thao tung", "cam xuc", "dong luc", "thoi quen", "nhan cach", "tinh cach", "dinh kien"],
    "strategy_tactics": ["chien luoc", "binh phap", "the tran", "don bay", "bat doi xung", "co hoi", "canh tranh", "doi thu", "muc tieu", "ke hoach"],
    "resilience_mindset": ["khac ky", "tam tri", "nghich canh", "ap luc", "binh tam", "kiem soat", "vo vi", "tam trai", "thich ung", "kien tri"],
}


class LocalDenseEmbedder:
    """
    High-performance, lightweight, deterministic dense embedder.
    Generates dense semantic embeddings using subword n-gram hashing,
    semantic anchor projections, and L2 normalization, 100% offline.
    """

    def __init__(self, dim: int = 384, seed: int = 42) -> None:
        self.dim = dim
        self.seed = seed
        rng = np.random.RandomState(seed)
        # Random projection basis for projecting terms into dense vector space
        self.projection_matrix = rng.randn(10007, dim).astype(np.float32)
        # Anchor bases for semantic topic alignment
        self.anchor_bases = {
            anchor_name: rng.randn(dim).astype(np.float32)
            for anchor_name in SEMANTIC_ANCHORS
        }
        for name in self.anchor_bases:
            norm = np.linalg.norm(self.anchor_bases[name])
            if norm > 1e-6:
                self.anchor_bases[name] /= norm

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text string into a normalized dense vector."""
        if not text:
            return np.zeros(self.dim, dtype=np.float32)

        tokens = tokenize(text)
        if not tokens:
            return np.zeros(self.dim, dtype=np.float32)

        vec = np.zeros(self.dim, dtype=np.float32)
        text_lower = text.lower()

        # 1. Word tokens & subwords projection
        for i, token in enumerate(tokens):
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % 10007
            weight = 1.0 / (1.0 + 0.01 * min(i, 50))
            vec += self.projection_matrix[h] * weight

            # Character 3-grams for morphology overlap
            if len(token) >= 3:
                for ci in range(len(token) - 2):
                    c3 = token[ci : ci + 3]
                    ch = int(hashlib.md5(c3.encode("utf-8")).hexdigest(), 16) % 10007
                    vec += self.projection_matrix[ch] * (weight * 0.3)

            # Bi-grams for local phrase context
            if i > 0:
                bigram = f"{tokens[i-1]}_{token}"
                bh = int(hashlib.md5(bigram.encode("utf-8")).hexdigest(), 16) % 10007
                vec += self.projection_matrix[bh] * (weight * 1.5)

        # 2. Semantic anchor projections
        for anchor_name, anchor_phrases in SEMANTIC_ANCHORS.items():
            for phrase in anchor_phrases:
                if phrase in text_lower or any(p in tokens for p in phrase.split()):
                    vec += self.anchor_bases[anchor_name] * 3.5

        # L2 normalize
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec /= norm

        return vec

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """Embed a batch of text strings into an (N x dim) matrix."""
        matrix = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            matrix[i] = self.embed_text(t)
        return matrix


class VectorSearchEngine:
    """
    Dense Vector Search Engine with persistent cache for NhanThuat Knowledge Units.
    """

    def __init__(
        self,
        units: list[Any] | None = None,
        cache_path: str | Path | None = None,
        dim: int = 384,
    ) -> None:
        self.dim = dim
        self.embedder = LocalDenseEmbedder(dim=dim)
        self.units: list[Any] = []
        self.unit_ids: list[str] = []
        self.unit_map: dict[str, Any] = {}
        self.embeddings: np.ndarray = np.zeros((0, dim), dtype=np.float32)

        if cache_path is None:
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
            cache_path = repo_root / "knowledge" / ".vector_cache.json"
        self.cache_path = Path(cache_path)

        if units:
            self.index_units(units)

    def _compute_corpus_checksum(self, units: list[Any]) -> str:
        """Compute checksum of the units list to invalidate stale cache."""
        hasher = hashlib.sha256()
        for u in units:
            uid = str(getattr(u, "id", getattr(u, "unit_id", "")))
            ver = str(getattr(u, "version", ""))
            checksum = str(getattr(u, "checksum", ""))
            hasher.update(f"{uid}:{ver}:{checksum}".encode("utf-8"))
        return hasher.hexdigest()

    def index_units(self, units: list[Any], use_cache: bool = True) -> None:
        """Index all units into dense vector matrix with disk cache support."""
        self.units = list(units)
        self.unit_ids = [getattr(u, "id", getattr(u, "unit_id", "")) for u in self.units]
        self.unit_map = {uid: u for uid, u in zip(self.unit_ids, self.units)}

        if not self.units:
            self.embeddings = np.zeros((0, self.dim), dtype=np.float32)
            return

        corpus_hash = self._compute_corpus_checksum(self.units)

        # Try loading from cache
        if use_cache and self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                if cache_data.get("corpus_hash") == corpus_hash and "embeddings" in cache_data:
                    cached_ids = cache_data.get("unit_ids", [])
                    if cached_ids == self.unit_ids:
                        self.embeddings = np.array(cache_data["embeddings"], dtype=np.float32)
                        return
            except Exception:
                pass  # Recompute if cache read fails

        # Compute fresh embeddings
        texts = []
        for unit in self.units:
            raw = unit.raw if hasattr(unit, "raw") and unit.raw else getattr(unit, "raw_data", {})
            corpus = extract_unit_text_corpus(raw if raw else unit.__dict__)
            texts.append(corpus)

        self.embeddings = self.embedder.embed_batch(texts)

        # Save to disk cache
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_payload = {
                "corpus_hash": corpus_hash,
                "num_units": len(self.units),
                "dimension": self.dim,
                "unit_ids": self.unit_ids,
                "embeddings": self.embeddings.tolist(),
            }
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_payload, f)
        except Exception:
            pass  # Non-blocking if write fails

    def search(
        self,
        query: str,
        top_k: int = 5,
        domain_filter: str | None = None,
        min_similarity: float = 0.0,
    ) -> list[VectorResult]:
        """
        Search indexed units by semantic vector cosine similarity.
        Returns top_k VectorResult objects sorted by similarity descending.
        """
        if not query or len(self.units) == 0 or len(self.embeddings) == 0:
            return []

        q_vec = self.embedder.embed_text(query)
        if np.linalg.norm(q_vec) < 1e-6:
            return []

        # Vectorized cosine similarity: dot product of normalized vectors
        sims = np.dot(self.embeddings, q_vec)

        results: list[VectorResult] = []
        # Filter and rank
        scored_indices = []
        for idx, sim in enumerate(sims):
            unit = self.units[idx]
            raw = unit.raw if hasattr(unit, "raw") and unit.raw else getattr(unit, "raw_data", {})
            unit_domain = str(getattr(unit, "primary_domain", getattr(unit, "domain", raw.get("primary_domain", ""))))
            if domain_filter and unit_domain != domain_filter:
                continue

            score = float(sim)
            if score > min_similarity:
                scored_indices.append((score, idx))

        scored_indices.sort(key=lambda x: x[0], reverse=True)

        for score, idx in scored_indices[:top_k]:
            unit = self.units[idx]
            uid = self.unit_ids[idx]
            results.append(
                VectorResult(
                    unit_id=uid,
                    score=round(max(0.0, score), 4),
                    unit=unit,
                )
            )

        return results
