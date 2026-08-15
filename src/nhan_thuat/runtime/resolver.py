"""Knowledge resolution engine."""

from collections.abc import Iterable

from nhan_thuat.models import KnowledgeUnit


class KnowledgeResolver:
    """Resolves queries and matches them to relevant knowledge units."""

    def __init__(self, units: Iterable[KnowledgeUnit]):
        self._units = list(units)

    def resolve(self, query: str, limit: int = 5, domain_filter: str | None = None) -> list[KnowledgeUnit]:
        """
        Resolve a text query to the most relevant knowledge units.
        This is a basic keyword-based fallback implementation.
        In production, this should integrate with a vector store or BM25 engine.
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
                
        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        
        return results[:limit]

    def resolve_by_id(self, unit_id: str) -> KnowledgeUnit | None:
        """Resolve a specific unit by its ID."""
        for unit in self._units:
            if unit.id == unit_id:
                return unit
        return None
