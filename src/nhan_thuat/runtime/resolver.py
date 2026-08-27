"""Knowledge resolution engine with hybrid lexical and semantic search."""

from collections.abc import Iterable
from typing import Any

from nhan_thuat.models import KnowledgeUnit
from nhan_thuat.rag.hybrid_retriever import HybridRetrievalResult, HybridRetriever


class KnowledgeResolver:
    """Resolves queries and matches them to relevant knowledge units using keyword and hybrid search."""

    def __init__(self, units: Iterable[KnowledgeUnit]):
        self._units = list(units)
        self._hybrid_retriever: HybridRetriever | None = None

    @property
    def hybrid_retriever(self) -> HybridRetriever:
        if self._hybrid_retriever is None:
            self._hybrid_retriever = HybridRetriever(units=self._units)
        return self._hybrid_retriever

    def resolve_hybrid(
        self,
        query: str,
        limit: int = 5,
        domain_filter: str | None = None,
        expand_relations: bool = True,
    ) -> HybridRetrievalResult:
        """Resolve query using Hybrid RAG Engine (BM25 + Dense Vector + RRF Fusion)."""
        return self.hybrid_retriever.retrieve(
            query=query,
            top_k=limit,
            domain_filter=domain_filter,
            expand_relations=expand_relations,
        )

    def resolve(self, query: str, limit: int = 5, domain_filter: str | None = None) -> list[KnowledgeUnit]:
        """
        Resolve a text query to the most relevant knowledge units.
        Returns top units matching query keywords.
        """
        return [unit for _, unit in self.resolve_scored(query, limit=limit, domain_filter=domain_filter)]

    def resolve_scored(
        self, query: str, limit: int = 5, domain_filter: str | None = None
    ) -> list[tuple[int, KnowledgeUnit]]:
        """Resolve a query and return (score, unit) pairs sorted by relevance."""
        results = []
        query_terms = set(query.lower().split())
        
        for unit in self._units:
            if domain_filter and unit.primary_domain != domain_filter:
                continue
                
            score = 0
            text_corpus = (
                unit.title.lower() + " " + 
                unit.summary.lower() + " " + 
                unit.definition.lower()
            )
            
            for term in query_terms:
                if term in text_corpus:
                    score += 1
            
            if score > 0:
                results.append((score, unit))
                
        # Sort by score descending, then by ID for deterministic tie-breaking
        results.sort(key=lambda x: (x[0], x[1].id), reverse=True)
        
        return results[:limit]

    def resolve_by_id(self, unit_id: str) -> KnowledgeUnit | None:
        """Resolve a specific unit by its ID."""
        for unit in self._units:
            if unit.id == unit_id:
                return unit
        return None
