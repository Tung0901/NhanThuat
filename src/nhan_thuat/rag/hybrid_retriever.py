"""
Hybrid Fusion Retriever & Multi-tier Knowledge Linker for NhanThuat RAG Engine.
Combines Lexical (BM25) and Semantic (Dense Vector) search via Reciprocal Rank Fusion (RRF)
and performs multi-tier relationship expansion (Laws <-> Principles <-> Anti-patterns <-> Models).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from nhan_thuat.models import KnowledgeUnit
from nhan_thuat.rag.bm25_search import BM25Engine, BM25Result
from nhan_thuat.rag.vector_search import VectorResult, VectorSearchEngine


@dataclass
class FusionItem:
    unit_id: str
    unit: Any
    final_score: float
    bm25_rank: int | None = None
    bm25_score: float | None = None
    vector_rank: int | None = None
    vector_score: float | None = None
    rrf_score: float = 0.0


@dataclass
class RelatedUnitLink:
    relation_type: str  # e.g., 'supports', 'depends_on', 'anti_pattern', 'associated_principle'
    unit_id: str
    title: str
    unit_type: str
    summary: str


@dataclass
class HybridRetrievalResult:
    query: str
    primary_units: list[Any] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    fusion_items: list[FusionItem] = field(default_factory=list)
    related_units_map: dict[str, list[RelatedUnitLink]] = field(default_factory=dict)
    latency_breakdown: dict[str, float] = field(default_factory=dict)
    total_latency_ms: float = 0.0


class HybridRetriever:
    """
    Hybrid Retrieval Engine with Reciprocal Rank Fusion (RRF) and Multi-tier Relation Expansion.
    """

    def __init__(
        self,
        units: list[Any] | None = None,
        bm25_engine: BM25Engine | None = None,
        vector_engine: VectorSearchEngine | None = None,
        rrf_k: int = 60,
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5,
    ) -> None:
        self.rrf_k = rrf_k
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight

        self.units = list(units) if units else []
        self.unit_map: dict[str, Any] = {
            getattr(u, "id", getattr(u, "unit_id", "")): u for u in self.units
        }

        self.bm25_engine = bm25_engine or BM25Engine(units=self.units)
        self.vector_engine = vector_engine or VectorSearchEngine(units=self.units)

        if units and not bm25_engine:
            self.bm25_engine.index_units(self.units)
        if units and not vector_engine:
            self.vector_engine.index_units(self.units)

    def index_units(self, units: list[Any]) -> None:
        """Index or update knowledge units in both engines."""
        self.units = list(units)
        self.unit_map = {
            getattr(u, "id", getattr(u, "unit_id", "")): u for u in self.units
        }
        self.bm25_engine.index_units(self.units)
        self.vector_engine.index_units(self.units)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        domain_filter: str | None = None,
        expand_relations: bool = True,
        mode: str = "rrf",  # 'rrf' or 'weighted'
    ) -> HybridRetrievalResult:
        """
        Execute Hybrid Search (BM25 + Vector) and merge results.
        Modes:
        - 'rrf': Reciprocal Rank Fusion: Score = sum(weight / (k + rank))
        - 'weighted': Weighted linear combination: Score = w1*BM25_norm + w2*Vector_sim
        """
        t_start = time.perf_counter()

        # 1. Lexical Search (BM25)
        t_bm25_start = time.perf_counter()
        bm25_results = self.bm25_engine.search(
            query=query,
            top_k=top_k * 3,
            domain_filter=domain_filter,
        )
        bm25_latency_ms = round((time.perf_counter() - t_bm25_start) * 1000, 2)

        # 2. Semantic Search (Dense Vector)
        t_vec_start = time.perf_counter()
        vector_results = self.vector_engine.search(
            query=query,
            top_k=top_k * 3,
            domain_filter=domain_filter,
        )
        vector_latency_ms = round((time.perf_counter() - t_vec_start) * 1000, 2)

        # 3. Fusion (RRF or Weighted)
        t_fusion_start = time.perf_counter()
        fusion_map: dict[str, FusionItem] = {}

        # Process BM25 ranks
        for rank, b_res in enumerate(bm25_results, 1):
            uid = b_res.unit_id
            unit = b_res.unit or self.unit_map.get(uid)
            rrf_contrib = self.bm25_weight / (self.rrf_k + rank)

            fusion_map[uid] = FusionItem(
                unit_id=uid,
                unit=unit,
                final_score=0.0,
                bm25_rank=rank,
                bm25_score=b_res.score,
                rrf_score=rrf_contrib,
            )

        # Process Vector ranks
        for rank, v_res in enumerate(vector_results, 1):
            uid = v_res.unit_id
            unit = v_res.unit or self.unit_map.get(uid)
            rrf_contrib = self.vector_weight / (self.rrf_k + rank)

            if uid in fusion_map:
                fusion_map[uid].vector_rank = rank
                fusion_map[uid].vector_score = v_res.score
                fusion_map[uid].rrf_score += rrf_contrib
            else:
                fusion_map[uid] = FusionItem(
                    unit_id=uid,
                    unit=unit,
                    final_score=0.0,
                    vector_rank=rank,
                    vector_score=v_res.score,
                    rrf_score=rrf_contrib,
                )

        # Calculate final scores
        for uid, item in fusion_map.items():
            if mode == "weighted":
                b_score = (item.bm25_score or 0.0)
                v_score = (item.vector_score or 0.0)
                item.final_score = round(self.bm25_weight * b_score + self.vector_weight * v_score, 4)
            else:  # RRF default
                item.final_score = round(item.rrf_score * 100, 4)

        # Sort merged candidates
        ranked_items = sorted(fusion_map.values(), key=lambda x: x.final_score, reverse=True)
        top_items = ranked_items[:top_k]
        fusion_latency_ms = round((time.perf_counter() - t_fusion_start) * 1000, 2)

        # 4. Multi-tier Relationship Expansion
        related_units_map: dict[str, list[RelatedUnitLink]] = {}
        if expand_relations:
            for item in top_items:
                uid = item.unit_id
                unit = item.unit or self.unit_map.get(uid)
                if not unit:
                    continue
                
                links: list[RelatedUnitLink] = []
                raw = unit.raw if hasattr(unit, "raw") and unit.raw else getattr(unit, "raw_data", {})
                relations = raw.get("relations", {}) if raw else getattr(unit, "relations", {})
                
                # Check explicit relations (supports, depends_on, conflicts_with, applies_to)
                if isinstance(relations, dict):
                    for rel_type, target_ids in relations.items():
                        for tid in target_ids:
                            target_unit = self.unit_map.get(str(tid))
                            if target_unit:
                                t_raw = target_unit.raw if hasattr(target_unit, "raw") and target_unit.raw else getattr(target_unit, "raw_data", {})
                                links.append(
                                    RelatedUnitLink(
                                        relation_type=rel_type,
                                        unit_id=str(tid),
                                        title=str(getattr(target_unit, "title", t_raw.get("title", tid))),
                                        unit_type=str(getattr(target_unit, "type", getattr(target_unit, "unit_type", t_raw.get("type", "")))),
                                        summary=str(getattr(target_unit, "summary", t_raw.get("summary", ""))),
                                    )
                                )

                # Domain & Category Co-occurrence expansion (e.g. Law -> related Principles / Anti-patterns)
                primary_domain = str(getattr(unit, "primary_domain", getattr(unit, "domain", raw.get("primary_domain", ""))))
                unit_type = str(getattr(unit, "type", getattr(unit, "unit_type", raw.get("type", ""))))

                if len(links) < 3 and primary_domain:
                    # Find complementary unit in same domain
                    for other_id, other_u in self.unit_map.items():
                        if other_id == uid or any(l.unit_id == other_id for l in links):
                            continue
                        o_raw = other_u.raw if hasattr(other_u, "raw") and other_u.raw else getattr(other_u, "raw_data", {})
                        o_domain = str(getattr(other_u, "primary_domain", getattr(other_u, "domain", o_raw.get("primary_domain", ""))))
                        o_type = str(getattr(other_u, "type", getattr(other_u, "unit_type", o_raw.get("type", ""))))
                        
                        if o_domain == primary_domain:
                            # If primary is Law, link Anti-patterns / Principles in same domain
                            if unit_type == "law" and o_type in ("anti-pattern", "principle"):
                                links.append(
                                    RelatedUnitLink(
                                        relation_type=f"domain_{o_type}",
                                        unit_id=other_id,
                                        title=str(getattr(other_u, "title", o_raw.get("title", other_id))),
                                        unit_type=o_type,
                                        summary=str(getattr(other_u, "summary", o_raw.get("summary", ""))),
                                    )
                                )
                            elif unit_type == "anti-pattern" and o_type in ("principle", "law"):
                                links.append(
                                    RelatedUnitLink(
                                        relation_type=f"counter_{o_type}",
                                        unit_id=other_id,
                                        title=str(getattr(other_u, "title", o_raw.get("title", other_id))),
                                        unit_type=o_type,
                                        summary=str(getattr(other_u, "summary", o_raw.get("summary", ""))),
                                    )
                                )
                        if len(links) >= 3:
                            break

                related_units_map[uid] = links

        total_latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

        return HybridRetrievalResult(
            query=query,
            primary_units=[item.unit for item in top_items if item.unit is not None],
            scores={item.unit_id: item.final_score for item in top_items},
            fusion_items=top_items,
            related_units_map=related_units_map,
            latency_breakdown={
                "bm25_latency_ms": bm25_latency_ms,
                "vector_latency_ms": vector_latency_ms,
                "fusion_latency_ms": fusion_latency_ms,
            },
            total_latency_ms=total_latency_ms,
        )
