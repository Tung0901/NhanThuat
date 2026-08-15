"""Tests for Streamlit WebApp Engine Adapter."""

import pytest

from app.services.engine_adapter import EngineAdapter
from nhan_thuat.models import KnowledgeUnit


@pytest.fixture(scope="module")
def adapter():
    return EngineAdapter()

def test_app_imports_and_engine_integration(adapter: EngineAdapter):
    """Verify that the engine loads all units (at least 370)."""
    assert adapter.engine is not None
    assert len(adapter.engine.units_by_id) >= 370
    
def test_query_flow_multiple_results(adapter: EngineAdapter):
    """Test a broad query that should return multiple units."""
    results = adapter.resolve_query("xã hội", limit=5)
    assert len(results) > 1
    assert isinstance(results[0], KnowledgeUnit)
    
def test_query_flow_one_result(adapter: EngineAdapter):
    """Test a very specific query that should return the exact model."""
    results = adapter.resolve_query("Mô hình Khả năng Xử lý Kỹ lưỡng", limit=1)
    assert len(results) == 1
    assert results[0].id == "NT-MODEL-3401"
    
def test_query_flow_empty_query(adapter: EngineAdapter):
    """Empty query should return empty or gracefully handle it."""
    results = adapter.resolve_query("", limit=5)
    assert len(results) == 0
    
def test_query_flow_no_result(adapter: EngineAdapter):
    """Gibberish query should return empty."""
    results = adapter.resolve_query("asdfghjklqwerty", limit=5)
    assert len(results) == 0

def test_domain_filter(adapter: EngineAdapter):
    """Test domain filtering functionality."""
    results = adapter.query_filters(domain="tri-nhan")
    assert len(results) > 0
    for r in results:
        assert r.primary_domain == "tri-nhan"
        
def test_phenomenon_retrieval(adapter: EngineAdapter):
    """Test unit type filtering."""
    results = adapter.query_filters(unit_type="phenomenon")
    assert len(results) > 0
    for r in results:
        assert r.type == "phenomenon"

def test_evaluator_output(adapter: EngineAdapter):
    """Test evaluator processing."""
    # Force retrieve groupthink phenomenon
    units = [adapter.resolver.resolve_by_id("NT-PHENOMENON-3304")]
    # It has a risk: "Tiếp tục các chiến dịch ra mắt sản phẩm hoặc khoản đầu tư thảm họa dù nội bộ biết rõ rằng chúng sẽ thất bại."
    query = "Tiếp tục các chiến dịch ra mắt sản phẩm hoặc khoản đầu tư thảm họa dù nội bộ biết rõ rằng chúng sẽ thất bại."
    
    result = adapter.evaluate_content(query, units)
    assert "score" in result
    assert result["score"] < 100.0  # Risk triggered penalty
    assert len(result["violations"]) > 0

def test_dependencies_and_evidence(adapter: EngineAdapter):
    """Test transitive dependency resolution."""
    # Groupthink depends on Social Proof (NT-PHENOMENON-3301)
    deps = adapter.resolve_dependencies("NT-PHENOMENON-3304")
    dep_ids = [d.id for d in deps]
    assert "NT-PHENOMENON-3301" in dep_ids
