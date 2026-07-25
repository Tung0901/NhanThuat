from pathlib import Path

from nhan_thuat.loader import load_document
from nhan_thuat.registry import load_registry
from nhan_thuat.validator import validate_repository

ROOT = Path(__file__).resolve().parents[1]
BATCH_LAW_IDS = {f"NT-LAW-{number:04d}" for number in range(4, 24)}
BATCH_PRINCIPLE_IDS = {f"NT-PRINCIPLE-{number:04d}" for number in range(4, 44)}


def test_batch1_status_is_frozen() -> None:
    status = load_document(ROOT / "knowledge" / "foundation" / "batch-01" / "status.yaml")

    assert status["batch_id"] == "NT-BATCH-001"
    assert status["status"] == "frozen"
    assert status["progress"] == 100
    assert status["unit_counts"] == {"laws": 20, "principles": 40}
    assert status["approved_by"] == "Product Owner"


def test_batch1_units_are_registered_with_expected_types() -> None:
    registry = load_registry(ROOT)

    assert BATCH_LAW_IDS.issubset(registry.units)
    assert BATCH_PRINCIPLE_IDS.issubset(registry.units)
    assert {registry.get_unit(unit_id).type for unit_id in BATCH_LAW_IDS} == {"law"}
    assert {registry.get_unit(unit_id).type for unit_id in BATCH_PRINCIPLE_IDS} == {
        "principle"
    }


def test_batch1_units_have_metadata_and_taxonomy_classification() -> None:
    registry = load_registry(ROOT)
    valid_domains = set(registry.taxonomy.domains)

    for unit_id in BATCH_LAW_IDS | BATCH_PRINCIPLE_IDS:
        unit = registry.get_unit(unit_id)
        assert unit.status in ("review", "frozen")
        assert unit.version == "0.1.0"
        assert unit.primary_domain in valid_domains
        assert set(unit.secondary_domains).issubset(valid_domains)
        assert unit.primary_domain not in unit.secondary_domains
        assert unit.evidence.level == "provisional"
        assert isinstance(unit.evidence.references, tuple)
        assert unit.definition
        assert unit.mechanism
        assert unit.conditions
        assert unit.exceptions
        assert unit.applications
        assert unit.risks
        assert unit.tags


def test_batch1_relations_are_validated_and_cross_linked() -> None:
    registry = load_registry(ROOT)

    assert validate_repository(ROOT) == []
    relation_pairs = {
        (relation.source, relation.type, relation.target)
        for relation in registry.relations
        if relation.source in BATCH_LAW_IDS | BATCH_PRINCIPLE_IDS
    }

    for principle_id in BATCH_PRINCIPLE_IDS:
        depends_on_law = any(
            source == principle_id
            and relation_type == "depends_on"
            and target.startswith("NT-LAW-")
            for source, relation_type, target in relation_pairs
        )
        assert depends_on_law, principle_id

    for law_id in BATCH_LAW_IDS:
        supports_principle = any(
            source == law_id
            and relation_type == "supports"
            and target.startswith("NT-PRINCIPLE-")
            for source, relation_type, target in relation_pairs
        )
        assert supports_principle, law_id


def test_batch1_catalog_indexes_units() -> None:
    catalog = load_registry(ROOT).catalog().to_mapping()

    assert BATCH_LAW_IDS.issubset(catalog["indexes"]["by_type"]["law"])
    assert BATCH_PRINCIPLE_IDS.issubset(catalog["indexes"]["by_type"]["principle"])
    assert BATCH_LAW_IDS | BATCH_PRINCIPLE_IDS <= set(
        catalog["indexes"]["by_evidence_level"]["provisional"]
    )
    assert "systems" in catalog["indexes"]["by_tag"]


def test_batch1_manifest_and_review_report_are_frozen() -> None:
    manifest = load_document(ROOT / "knowledge" / "foundation" / "batch-01" / "manifest.yaml")
    report = load_document(ROOT / "knowledge" / "foundation" / "batch-01" / "review-report.yaml")

    assert manifest["status"] == "frozen"
    assert manifest["freeze"]["eligible"] is True
    assert report["freeze_eligibility"]["eligible"] is True
    assert report["duplicate_candidates"] == []
    assert report["conflict_candidates"] == []
