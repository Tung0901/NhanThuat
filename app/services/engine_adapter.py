"""Service adapter for the Nhan Thuat Knowledge Engine."""

import streamlit as st
from typing import List, Dict, Any, Tuple
from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.runtime.resolver import KnowledgeResolver
from nhan_thuat.runtime.prompt_builder import PromptBuilder
from nhan_thuat.runtime.evaluator import KnowledgeEvaluator
from nhan_thuat.runtime.synthesizer import KnowledgeSynthesizer
from nhan_thuat.models import KnowledgeUnit

@st.cache_resource(show_spinner="Booting Nhan Thuat Knowledge Engine...")
def get_engine() -> KnowledgeEngine:
    """Singleton instance of the KnowledgeEngine initialized with root registry."""
    return KnowledgeEngine()

class EngineAdapter:
    """Provides a clean UI-facing interface for the Nhan Thuat engine without exposing complexity."""
    
    def __init__(self):
        self.engine = get_engine()
        # Convert IndexedUnits to KnowledgeUnits for the resolver
        knowledge_units = []
        for iu in self.engine.units_by_id.values():
            try:
                knowledge_units.append(KnowledgeUnit.from_mapping(iu.raw_data, source_path=None))
            except Exception:
                pass
        self.resolver = KnowledgeResolver(knowledge_units)
        self.prompt_builder = PromptBuilder()
        self.evaluator = KnowledgeEvaluator()
        self.synthesizer = KnowledgeSynthesizer()
        
    def resolve_query(self, query: str, limit: int = 5) -> List[KnowledgeUnit]:
        """Resolve a text query to the top N knowledge units."""
        return self.resolver.resolve(query, limit=limit)

    def resolve_scored(self, query: str, limit: int = 5) -> List[Tuple[int, KnowledgeUnit]]:
        """Resolve a query to (score, unit) pairs with real resolver scores."""
        return self.resolver.resolve_scored(query, limit=limit)
        
    def synthesize(self, query: str, units: List[KnowledgeUnit]) -> Dict[str, Any]:
        """Produce a synthesis (LLM if configured, deterministic fallback)."""
        return self.synthesizer.synthesize(query, units)
        
    def resolve_dependencies(self, unit_id: str) -> List[KnowledgeUnit]:
        """Get transitive dependencies for a unit.

        Direct graph dependencies come from the engine index. The 'relations'
        block is semantic (supports/conflicts_with/applies_to) and bidirectional
        by design, so it is appended for context but excluded from graph traversal.
        """
        dep_ids = set(self.engine.get_transitive_dependencies(unit_id))

        unit = self.engine.get_unit(unit_id)
        if unit:
            raw_rels = unit.raw_data.get("relations", {})
            for rel_list in raw_rels.values():
                for did in rel_list:
                    dep_ids.add(did)
                    
        deps = []
        for did in dep_ids:
            u = self.engine.get_unit(did)
            if u:
                deps.append(KnowledgeUnit.from_mapping(u.raw_data, source_path=None))
        return deps
        
    def build_context(self, units: List[KnowledgeUnit]) -> str:
        """Build the markdown context string from units."""
        return self.prompt_builder.build_context(units, format_type="markdown")
        
    def evaluate_content(self, query_or_content: str, units: List[KnowledgeUnit]) -> Dict[str, Any]:
        """Evaluate content against the retrieved units."""
        return self.evaluator.evaluate(query_or_content, units)
        
    def query_filters(self, domain: str = None, unit_type: str = None) -> List[KnowledgeUnit]:
        """Filter the knowledge base."""
        results = []
        for unit in self.engine.units_by_id.values():
            if domain and domain != "All" and unit.domain != domain:
                continue
            if unit_type and unit_type != "All" and unit.unit_type != unit_type:
                continue
            results.append(KnowledgeUnit.from_mapping(unit.raw_data, source_path=None))
            
        return results

    def get_all_domains(self) -> List[str]:
        return sorted(list(self.engine.units_by_domain.keys()))
        
    def get_all_types(self) -> List[str]:
        return sorted(list(self.engine.units_by_type.keys()))
        
    def get_total_units(self) -> int:
        return len(self.engine.units_by_id)
        
    def get_type_counts(self) -> Dict[str, int]:
        counts = {}
        for unit_type, units in self.engine.units_by_type.items():
            counts[unit_type] = len(units)
        return counts
        
    def get_domain_counts(self) -> Dict[str, int]:
        return {domain: len(units) for domain, units in self.engine.units_by_domain.items()}
