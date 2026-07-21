from pathlib import Path

from nhan_thuat.loader import load_document
from nhan_thuat.registry import load_registry
from nhan_thuat.validator import validate_repository

ROOT = Path(__file__).resolve().parents[1]
HUMAN_NATURE_LAWS = {f"NT-LAW-{number:04d}" for number in range(24, 29)}
HUMAN_NATURE_PRINCIPLES = {f"NT-PRINCIPLE-{number:04d}" for number in range(44, 52)}
HUMAN_NATURE_PATTERNS = {f"NT-MODEL-{number:04d}" for number in range(1, 4)}
HUMAN_NATURE_ANTI_PATTERNS = {f"NT-ANTI-PATTERN-{number:04d}" for number in range(1, 5)}
HUMAN_NATURE_UNITS = (
    HUMAN_NATURE_LAWS
    | HUMAN_NATURE_PRINCIPLES
    | HUMAN_NATURE_PATTERNS
    | HUMAN_NATURE_ANTI_PATTERNS
)


def test_human_nature_status_is_frozen() -> None:
    status = load_document(ROOT / "docs" / "domains" / "human-nature" / "status.yaml")

    assert status["domain_area_id"] == "NT-DA-0001"
    assert status["slug"] == "human-nature"
    assert status["status"] == "frozen"
    assert status["previous_status"] == "ready_for_review"
    assert status["approved_by"] == "Product Owner"
    assert status["blockers"] == []
    assert status["unit_counts"] == {
        "laws": 5,
        "principles": 8,
        "models": 3,
        "anti_patterns": 4,
    }


def test_human_nature_units_are_registered_and_scoped() -> None:
    registry = load_registry(ROOT)

    assert HUMAN_NATURE_UNITS.issubset(registry.units)
    for unit_id in HUMAN_NATURE_UNITS:
        unit = registry.get_unit(unit_id)
        assert unit.status == "frozen"
        assert unit.primary_domain == "tri-nhan"
        assert unit.tags
        assert unit.evidence.level == "provisional"
        assert unit.evidence.references == ()


def test_human_nature_unit_types_match_expected_counts() -> None:
    registry = load_registry(ROOT)

    assert {registry.get_unit(unit_id).type for unit_id in HUMAN_NATURE_LAWS} == {"law"}
    assert {registry.get_unit(unit_id).type for unit_id in HUMAN_NATURE_PRINCIPLES} == {
        "principle"
    }
    assert {registry.get_unit(unit_id).type for unit_id in HUMAN_NATURE_PATTERNS} == {"model"}
    assert {registry.get_unit(unit_id).type for unit_id in HUMAN_NATURE_ANTI_PATTERNS} == {
        "anti-pattern"
    }


def test_human_nature_relations_validate() -> None:
    assert validate_repository(ROOT) == []


def test_human_nature_docs_and_evidence_placeholders_exist() -> None:
    docs = ROOT / "docs" / "domains" / "human-nature"

    assert (docs / "ARCHITECTURE.md").exists()
    assert (docs / "CONCEPT-MAP.md").exists()
    assert (docs / "GLOSSARY.md").exists()
    assert (docs / "DEPENDENCIES.md").exists()
    assert (docs / "REVIEW-REPORT.md").exists()

    evidence = load_document(docs / "evidence-placeholders.yaml")
    assert evidence["evidence_posture"]["default_level"] == "provisional"
    assert evidence["evidence_posture"]["external_references_fabricated"] is False


def test_human_nature_frozen_inventory_is_explicit() -> None:
    status = load_document(ROOT / "docs" / "domains" / "human-nature" / "status.yaml")
    docs = ROOT / "docs" / "domains" / "human-nature"

    assert set(status["members"]["laws"]) == HUMAN_NATURE_LAWS
    assert set(status["members"]["principles"]) == HUMAN_NATURE_PRINCIPLES
    assert set(status["members"]["models"]) == HUMAN_NATURE_PATTERNS
    assert set(status["members"]["anti_patterns"]) == HUMAN_NATURE_ANTI_PATTERNS
    assert set(status["artifacts"]) == {
        f"docs/domains/human-nature/{path.name}" for path in docs.iterdir() if path.is_file()
    }
