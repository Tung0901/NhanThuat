"""
BM25 Lexical Search Engine for NhanThuat Knowledge Units.
Implements Okapi BM25 with Vietnamese tokenization, term-frequency weights, and field boosts.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from nhan_thuat.models import KnowledgeUnit
from nhan_thuat.rag.normalizer import extract_unit_text_corpus, tokenize


@dataclass
class BM25MatchDetail:
    matched_terms: list[str] = field(default_factory=list)
    term_frequencies: dict[str, int] = field(default_factory=dict)
    field_hits: list[str] = field(default_factory=list)


@dataclass
class BM25Result:
    unit_id: str
    score: float
    normalized_score: float
    unit: Any  # KnowledgeUnit or IndexedUnit
    match_details: BM25MatchDetail = field(default_factory=BM25MatchDetail)


class BM25Engine:
    """
    Okapi BM25 Index & Search Engine for NhanThuat Knowledge Units.
    """

    def __init__(
        self,
        units: list[Any] | None = None,
        k1: float = 1.5,
        b: float = 0.75,
        title_boost: float = 2.5,
        tag_boost: float = 2.0,
    ) -> None:
        self.k1 = k1
        self.b = b
        self.title_boost = title_boost
        self.tag_boost = tag_boost

        self.units: list[Any] = []
        self.unit_map: dict[str, Any] = {}
        self.doc_lengths: list[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_term_freqs: list[dict[str, int]] = []
        self.idf: dict[str, float] = {}
        self.vocab: set[str] = set()

        if units:
            self.index_units(units)

    def index_units(self, units: list[Any]) -> None:
        """Build the BM25 inverted index from a list of Knowledge Units."""
        self.units = list(units)
        self.unit_map = {}
        self.doc_lengths = []
        self.doc_term_freqs = []
        doc_freqs: dict[str, int] = {}
        self.vocab = set()

        num_docs = len(self.units)
        if num_docs == 0:
            self.avg_doc_len = 0.0
            self.idf = {}
            return

        total_length = 0

        for unit in self.units:
            raw = unit.raw if hasattr(unit, "raw") and unit.raw else getattr(unit, "raw_data", {})
            uid = getattr(unit, "id", getattr(unit, "unit_id", ""))
            self.unit_map[uid] = unit

            # Extract fields
            title_tokens = tokenize(str(getattr(unit, "title", raw.get("title", ""))))
            tags_tokens = tokenize(" ".join(str(t) for t in getattr(unit, "tags", raw.get("tags", []))))
            id_tokens = tokenize(uid)
            corpus_text = extract_unit_text_corpus(raw if raw else unit.__dict__)
            body_tokens = tokenize(corpus_text)

            # Build weighted term frequency for document
            tf: dict[str, int] = {}
            for t in body_tokens:
                tf[t] = tf.get(t, 0) + 1
            for t in title_tokens:
                tf[t] = tf.get(t, 0) + int(self.title_boost)
            for t in tags_tokens + id_tokens:
                tf[t] = tf.get(t, 0) + int(self.tag_boost)

            doc_len = sum(tf.values())
            self.doc_lengths.append(doc_len)
            self.doc_term_freqs.append(tf)
            total_length += doc_len

            # Track Document Frequency (df)
            for term in tf.keys():
                doc_freqs[term] = doc_freqs.get(term, 0) + 1
                self.vocab.add(term)

        self.avg_doc_len = total_length / num_docs if num_docs > 0 else 0.0

        # Calculate Inverted Document Frequency (IDF) with BM25 smoothing
        self.idf = {}
        for term, df in doc_freqs.items():
            # BM25 standard smoothed IDF: ln(1 + (N - df + 0.5) / (df + 0.5))
            self.idf[term] = math.log(1.0 + (num_docs - df + 0.5) / (df + 0.5))

    def search(
        self,
        query: str,
        top_k: int = 5,
        domain_filter: str | None = None,
        min_score: float = 0.0,
    ) -> list[BM25Result]:
        """
        Search indexed units with query string.
        Returns top_k BM25Result objects sorted by BM25 score descending.
        """
        if not query or not self.units:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores: list[tuple[float, int, list[str]]] = []
        max_possible_score = 0.0

        for idx, unit in enumerate(self.units):
            raw = unit.raw if hasattr(unit, "raw") and unit.raw else getattr(unit, "raw_data", {})
            unit_domain = str(getattr(unit, "primary_domain", getattr(unit, "domain", raw.get("primary_domain", ""))))
            if domain_filter and unit_domain != domain_filter:
                continue

            doc_len = self.doc_lengths[idx]
            tf_dict = self.doc_term_freqs[idx]
            score = 0.0
            matched_terms = []

            for q_term in query_tokens:
                if q_term in tf_dict:
                    freq = tf_dict[q_term]
                    idf_val = self.idf.get(q_term, 0.0)

                    # Okapi BM25 TF formula
                    numerator = freq * (self.k1 + 1.0)
                    denominator = freq + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                    term_score = idf_val * (numerator / denominator)
                    score += term_score
                    matched_terms.append(q_term)

            if score > min_score:
                scores.append((score, idx, matched_terms))
                if score > max_possible_score:
                    max_possible_score = score

        if not scores:
            return []

        scores.sort(key=lambda x: x[0], reverse=True)
        results: list[BM25Result] = []

        norm_divisor = max_possible_score if max_possible_score > 0 else 1.0

        for score, idx, matched_terms in scores[:top_k]:
            unit = self.units[idx]
            uid = getattr(unit, "id", getattr(unit, "unit_id", ""))
            norm_score = round(min(1.0, score / norm_divisor), 4)
            tf_map = {t: self.doc_term_freqs[idx].get(t, 0) for t in matched_terms}

            results.append(
                BM25Result(
                    unit_id=uid,
                    score=round(score, 4),
                    normalized_score=norm_score,
                    unit=unit,
                    match_details=BM25MatchDetail(
                        matched_terms=matched_terms,
                        term_frequencies=tf_map,
                    ),
                )
            )

        return results
