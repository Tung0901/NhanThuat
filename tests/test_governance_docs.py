from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_project_constitution_exists() -> None:
    constitution = ROOT / "PROJECT_CONSTITUTION.md"
    assert constitution.exists()
    text = constitution.read_text(encoding="utf-8")
    assert "NT-GOV-CONSTITUTION-001" in text
    assert "Only the Product Owner may approve" in text


def test_initial_adrs_exist() -> None:
    adr_dir = ROOT / "docs" / "adr"
    expected = {
        "ADR-0001-repository-source-of-truth.md",
        "ADR-0002-separate-content-and-engine.md",
        "ADR-0003-product-owner-approval-and-frozen-control.md",
        "ADR-0004-adr-process-for-durable-decisions.md",
    }
    assert expected.issubset({path.name for path in adr_dir.glob("ADR-*.md")})
