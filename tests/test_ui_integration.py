import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.services.engine_adapter import EngineAdapter

def test_ui_engine_adapter_integration():
    """Verify EngineAdapter correctly integrates with the actual KnowledgeEngine."""
    adapter = EngineAdapter()
    
    # Verify core engine is loaded and contains expected data volume
    total_units = adapter.get_total_units()
    assert total_units >= 294, f"Expected at least 294 units, got {total_units}"
    
    # Verify types
    type_counts = adapter.get_type_counts()
    
    assert "phenomenon" in type_counts, "Phenomenon must be supported"
    assert type_counts["phenomenon"] > 0, "Phenomenon count must be > 0"
    assert "law" in type_counts
    assert "principle" in type_counts
    assert "model" in type_counts
    assert "anti-pattern" in type_counts
    
    # Verify domains
    domains = adapter.get_all_domains()
    assert len(domains) > 0, "Expected at least 1 domain"
    
    # Test query resolution
    results = adapter.resolve_query("test query", limit=3)
    assert len(results) > 0, "Resolve query should return results"
    
    # Ensure phenomenon is searchable
    phenomena_results = adapter.query_filters(domain="All", unit_type="phenomenon")
    assert len(phenomena_results) > 0, "Should return phenomena units"
    assert phenomena_results[0].type == "phenomenon"
