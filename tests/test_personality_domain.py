from pathlib import Path

from nhan_thuat.loader import load_document
from nhan_thuat.registry import load_registry
from nhan_thuat.validator import validate_repository

ROOT = Path(__file__).resolve().parents[1]
PERSONALITY_LAWS = {f"NT-LAW-{number:04d}" for number in range(34, 37)}
PERSONALITY_PRINCIPLES = {f"NT-PRINCIPLE-{number:04d}" for number in range(60, 63)}
PERSONALITY_PATTERNS = {f"NT-MODEL-{number:04d}" for number in range(7, 9)}
PERSONALITY_ANTI_PATTERNS = {f"NT-ANTI-PATTERN-{number:04d}" for number in range(9, 12)}
PERSONALITY_UNITS = (
    PERSONALITY_LAWS
    | PERSONALITY_PRINCIPLES
    | PERSONALITY_PATTERNS
    | PERSONALITY_ANTI_PATTERNS
)


def test_personality_status_is_frozen() -> None:
    status = load_document(ROOT / "docs" / "domains" / "personality" / "status.yaml")

    assert status["domain_area_id"] == "NT-DA-0003"
    assert status["slug"] == "personality"
    assert status["status"] == "frozen"
    assert status["previous_status"] == "ready_for_review"
    assert status["approved_by"] == "Product Owner"
    assert status["blockers"] == []
    assert status["unit_counts"] == {
        "laws": 3,
        "principles": 3,
        "models": 2,
        "anti_patterns": 3,
    }


def test_personality_units_are_registered_and_scoped() -> None:
    registry = load_registry(ROOT)

    assert PERSONALITY_UNITS.issubset(registry.units)
    for unit_id in PERSONALITY_UNITS:
        unit = registry.get_unit(unit_id)
        assert unit.status == "frozen"
        expected_domain = "hop-chung" if unit_id == "NT-ANTI-PATTERN-0011" else "tri-nhan"
        assert unit.primary_domain == expected_domain
        assert unit.tags
        assert unit.evidence.level == "provisional"


def test_personality_unit_types_match_expected_counts() -> None:
    registry = load_registry(ROOT)

    assert {registry.get_unit(unit_id).type for unit_id in PERSONALITY_LAWS} == {"law"}
    assert {registry.get_unit(unit_id).type for unit_id in PERSONALITY_PRINCIPLES} == {
        "principle"
    }
    assert {registry.get_unit(unit_id).type for unit_id in PERSONALITY_PATTERNS} == {"model"}
    assert {registry.get_unit(unit_id).type for unit_id in PERSONALITY_ANTI_PATTERNS} == {
        "anti-pattern"
    }


def test_personality_relations_validate() -> None:
    assert validate_repository(ROOT) == []


def test_personality_docs_and_evidence_placeholders_exist() -> None:
    docs = ROOT / "docs" / "domains" / "personality"

    assert (docs / "ARCHITECTURE.md").exists()
    assert (docs / "CONCEPT-MAP.md").exists()
    assert (docs / "GLOSSARY.md").exists()
    assert (docs / "DEPENDENCIES.md").exists()
    assert (docs / "REVIEW-REPORT.md").exists()

    evidence = load_document(docs / "evidence-placeholders.yaml")
    assert evidence["evidence_posture"]["default_level"] == "provisional"
    assert evidence["evidence_posture"]["external_references_fabricated"] is False


def test_personality_frozen_inventory_is_explicit() -> None:
    status = load_document(ROOT / "docs" / "domains" / "personality" / "status.yaml")
    docs = ROOT / "docs" / "domains" / "personality"

    assert set(status["members"]["laws"]) == PERSONALITY_LAWS
    assert set(status["members"]["principles"]) == PERSONALITY_PRINCIPLES
    assert set(status["members"]["models"]) == PERSONALITY_PATTERNS
    assert set(status["members"]["anti_patterns"]) == PERSONALITY_ANTI_PATTERNS
    assert set(status["artifacts"]) == {
        f"docs/domains/personality/{path.name}" for path in docs.iterdir() if path.is_file()
    }
