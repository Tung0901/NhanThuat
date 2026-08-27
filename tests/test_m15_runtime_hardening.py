"""
Milestone M15 Runtime Hardening Targeted Test Suite.
Tests KnowledgeEngine, CanonicalSourceRegistry, BusinessOSRuntimeOrchestrator, Storage, and API Endpoints.
"""

from pathlib import Path

from backend.app.engine.canonical_registry import CanonicalSourceRegistry
from backend.app.engine.runtime import BusinessOSRuntimeOrchestrator, RuntimeRequestPayload
from backend.app.engine.storage import FileStateStorageAdapter, InMemoryStorageAdapter
from nhan_thuat.knowledge_engine import FALLBACK_INSUFFICIENT_KNOWLEDGE, KnowledgeEngine


def test_knowledge_engine_loading_and_indexing() -> None:
    engine = KnowledgeEngine()
    # All knowledge units loaded
    assert len(engine.units_by_id) == 379

    # Check primary indexes
    assert "NT-LAW-0001" in engine.units_by_id
    unit = engine.get_unit("NT-LAW-0001")
    assert unit is not None
    assert unit.unit_type == "law"
    assert unit.checksum.startswith("sha256:")


def test_knowledge_engine_transitive_dependencies() -> None:
    engine = KnowledgeEngine()
    unit = engine.get_unit("NT-LAW-0001")
    assert unit is not None
    transitive = engine.get_transitive_dependencies("NT-LAW-0001")
    assert isinstance(transitive, list)


def test_knowledge_engine_duplicate_id_rejection(tmp_path: Path) -> None:
    # Read a real valid unit file and create duplicate files
    sample_file = Path(__file__).resolve().parent.parent / "knowledge" / "units" / "laws" / "NT-LAW-0001.yaml"
    valid_content = sample_file.read_text(encoding="utf-8")
    
    # Use valid content for both files
    u1 = tmp_path / "unit1.yaml"
    u2 = tmp_path / "unit2.yaml"
    u1.write_text(valid_content, encoding="utf-8")
    u2.write_text(valid_content, encoding="utf-8")

    try:
        KnowledgeEngine(root_dir=tmp_path)
        assert False, "Should have raised ValueError for duplicate ID"
    except ValueError as exc:
        assert "Duplicate Knowledge Unit ID 'NT-LAW-0001'" in str(exc)


def test_canonical_source_registry() -> None:
    registry = CanonicalSourceRegistry()
    summary = registry.get_registered_sources_summary()

    assert summary["knowledge_units"]["exists"] is True
    assert summary["schemas"]["exists"] is True
    assert summary["docs_knowledge"]["exists"] is True
    assert summary["governance"]["exists"] is True

    # Resolve an existing schema
    resolved = registry.resolve_source("schemas/knowledge-unit.schema.json")
    assert resolved is not None
    assert resolved.approval_status == "APPROVED"
    assert resolved.checksum.startswith("sha256:")


def test_runtime_orchestrator_execution() -> None:
    orchestrator = BusinessOSRuntimeOrchestrator()
    req = RuntimeRequestPayload(
        session_id="SESS-TEST-001",
        correlation_id="CORR-TEST-001",
        intent_action="negotiation_coaching",
        scenario_type="objection",
        context_stack={"keywords": ["price objection"]},
        requested_knowledge_ids=["NT-LAW-0001"],
    )

    response = orchestrator.execute(req)
    assert response.status_code == "SUCCESS"
    assert response.primary_philosophy == "rhetoric"
    assert response.confidence_score > 0.0
    assert response.execution_latency_ms >= 0.0
    assert response.causal_provenance["checksum"].startswith("sha256:")
    assert response.config_snapshot["global_ai_temperature"] == 0.1


def test_runtime_orchestrator_fallback_on_missing_unit() -> None:
    orchestrator = BusinessOSRuntimeOrchestrator()
    req = RuntimeRequestPayload(
        session_id="SESS-TEST-002",
        correlation_id="CORR-TEST-002",
        intent_action="query_unknown",
        scenario_type="general",
        requested_knowledge_ids=["NT-MISSING-UNIT-9999"],
    )

    response = orchestrator.execute(req)
    assert response.status_code == "INSUFFICIENT_VERIFIED_KNOWLEDGE"
    assert response.error_code == FALLBACK_INSUFFICIENT_KNOWLEDGE


def test_storage_adapters() -> None:
    # 1. InMemoryStorageAdapter
    mem = InMemoryStorageAdapter()
    mem.set("leads", "LEAD-001", {"id": "LEAD-001", "name": "Test"})
    assert mem.get("leads", "LEAD-001") == {"id": "LEAD-001", "name": "Test"}
    assert len(mem.list("leads")) == 1
    assert mem.delete("leads", "LEAD-001") is True

    # 2. FileStateStorageAdapter
    fs = FileStateStorageAdapter()
    fs.set("test_col", "key1", {"data": "hello"})
    assert fs.get("test_col", "key1") == {"data": "hello"}
    assert fs.delete("test_col", "key1") is True
