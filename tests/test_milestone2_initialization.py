from pathlib import Path

from nhan_thuat.loader import load_document

ROOT = Path(__file__).resolve().parents[1]


def test_milestone2_status_initializes_domain_system() -> None:
    status = load_document(ROOT / "milestones" / "milestone-02-domain-system" / "status.yaml")

    assert status["milestone_id"] == "NT-MILESTONE-02"
    assert status["title"] == "Milestone 2 - Knowledge Expansion & Domain System"
    assert status["status"] == "in_progress"
    assert status["progress"] == 10


def test_domain_registry_contains_only_approved_ids_and_slugs() -> None:
    registry = load_document(ROOT / "knowledge" / "domain-registry.yaml")
    domains = registry["domains"]

    assert len(domains) == 30
    assert set().union(*(domain.keys() for domain in domains)) == {"id", "slug", "category_id"}
    assert domains[0] == {"id": "NT-DA-0001", "slug": "human-nature", "category_id": "CAT-CORE"}
    assert domains[-1] == {"id": "NT-DA-0030", "slug": "persuasion-influence", "category_id": "CAT-BEHAVIORAL"}
    assert len({domain["id"] for domain in domains}) == 30
    assert len({domain["slug"] for domain in domains}) == 30


def test_approved_domain_blueprint_adrs_are_accepted() -> None:
    adr_0014 = (
        ROOT / "docs" / "adr" / "ADR-0014-domain-catalogue-hierarchy-and-dependencies.md"
    ).read_text(encoding="utf-8")
    adr_0015 = (
        ROOT / "docs" / "adr" / "ADR-0015-domain-expansion-planning-and-freeze-gates.md"
    ).read_text(encoding="utf-8")

    assert "**Status:** accepted" in adr_0014
    assert "**Status:** accepted" in adr_0015


def test_roadmap_aligns_milestone_sequence() -> None:
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")

    assert "Milestone 2 - Knowledge Expansion & Domain System" in roadmap
    assert "Milestone 3 - Intelligence Engine" in roadmap
    assert "Milestone 4 - BusinessOS Integration" in roadmap
