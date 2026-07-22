from pathlib import Path

from nhan_thuat.catalog import KnowledgeCatalog
from nhan_thuat.identifiers import generate_identifier, next_identifier, parse_identifier
from nhan_thuat.naming import (
    is_kebab_slug,
    validate_filename_contains_id,
    validate_unit_identifier_matches_type,
)
from nhan_thuat.ontology import known_relation_types
from nhan_thuat.registry import build_registry, load_registry

ROOT = Path(__file__).resolve().parents[1]


def test_registry_loads_domains_units_and_relations() -> None:
    registry = load_registry(ROOT)

    assert set(registry.domains) == {"tu-than", "tri-nhan", "dung-nhan", "hop-chung", "thanh-su"}
    assert "NT-LAW-0001" in registry.units
    assert registry.get_unit("NT-LAW-0001").primary_domain == "tri-nhan"
    assert registry.taxonomy.has_domain("tri-nhan")


def test_legacy_build_registry_shape_is_preserved() -> None:
    legacy = build_registry(ROOT)

    assert "NT-LAW-0001" in legacy
    assert legacy["NT-LAW-0001"]["id"] == "NT-LAW-0001"
    assert "source_path" not in legacy["NT-LAW-0001"]


def test_catalog_contains_deterministic_indexes() -> None:
    catalog = load_registry(ROOT).catalog()
    data = catalog.to_mapping()

    assert isinstance(catalog, KnowledgeCatalog)
    assert "NT-LAW-0001" in data["indexes"]["by_type"]["law"]
    assert "NT-LAW-0001" in data["indexes"]["by_primary_domain"]["tri-nhan"]
    assert "NT-LAW-0001" in data["indexes"]["by_evidence_level"]["provisional"]
    assert isinstance(data["indexes"]["by_evidence_reference"], dict)
    assert "NT-LAW-0001" in data["indexes"]["by_tag"]["motivation"]


def test_identifier_generation_and_parsing() -> None:
    identifier = parse_identifier("NT-LAW-0001")
    domain_identifier = parse_identifier("NT-D01")

    assert identifier.prefix == "LAW"
    assert identifier.number == 1
    assert domain_identifier.prefix == "D"
    assert domain_identifier.number == 1
    assert generate_identifier("LAW", 2) == "NT-LAW-0002"
    assert next_identifier(["NT-LAW-0001", "NT-TOOL-0001"], "LAW") == "NT-LAW-0002"


def test_naming_conventions() -> None:
    assert is_kebab_slug("decision-making")
    assert not is_kebab_slug("Decision Making")
    assert validate_unit_identifier_matches_type("NT-LAW-0001", "law") is None
    assert "does not match" in validate_unit_identifier_matches_type("NT-TOOL-0001", "law")
    assert validate_filename_contains_id(Path("NT-LAW-0001.yaml"), "NT-LAW-0001") is None


def test_ontology_relation_vocabulary_is_backwards_compatible() -> None:
    assert known_relation_types() == ("supports", "conflicts_with", "depends_on", "applies_to")
