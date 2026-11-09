"""Unit tests for IChing Matrix V2 capabilities:
- 8x8 Coordinates Matrix
- 12 Sovereign Hexagrams (Thập Nhị Tức Quái)
- Moving Lines and State Transition Simulation
- Hydrated relations (Nuclear, Opposite, Inverted)
- Diagnostic tags and Strategic Stances
"""

from backend.app.engine.philosophies.iching_service import TRIGRAM_ORDER, iching_service


def test_iching_service_enrichment():
    """Verify all 64 hexagrams have required v2 fields."""
    all_hexs = iching_service.list_hexagrams()
    assert len(all_hexs) == 64

    for h in all_hexs:
        assert "upper_trigram" in h
        assert "lower_trigram" in h
        assert "binary_pattern" in h
        assert len(h["binary_pattern"]) == 6
        assert all(b in ("0", "1") for b in h["binary_pattern"])
        assert "nuclear_hex_number" in h
        assert 1 <= h["nuclear_hex_number"] <= 64
        assert "opposite_hex_number" in h
        assert 1 <= h["opposite_hex_number"] <= 64
        assert "inverted_hex_number" in h
        assert 1 <= h["inverted_hex_number"] <= 64
        assert "six_lines" in h
        assert len(h["six_lines"]) == 6
        assert "strategic_stance" in h
        assert h["strategic_stance"] in ("Tiến", "Thoái", "Thủ", "Biến")
        assert "diagnostic_tags" in h
        assert len(h["diagnostic_tags"]) >= 1


def test_matrix_8x8():
    """Verify the 8x8 matrix returns 8 rows with 8 cells each and correct upper/lower matching."""
    res = iching_service.get_matrix_8x8()
    assert "matrix" in res
    assert len(res["matrix"]) == 8
    assert res["trigrams_order"] == TRIGRAM_ORDER

    for row in res["matrix"]:
        upper = row["upper_trigram"]
        assert upper in TRIGRAM_ORDER
        assert len(row["cells"]) == 8
        for cell in row["cells"]:
            assert "number" in cell
            assert 1 <= cell["number"] <= 64
            assert "name" in cell
            assert "symbol" in cell


def test_sovereign_12_hexagrams():
    """Verify the 12 sovereign hexagrams are complete and ordered."""
    sovereigns = iching_service.get_sovereign_hexagrams()
    assert len(sovereigns) == 12

    # Check phase orders are 1..12
    orders = [s["twelve_sovereign"]["phase_order"] for s in sovereigns]
    assert orders == list(range(1, 13))

    # Phase 1 must be Phục (#24) and Phase 12 must be Khôn (#2)
    assert sovereigns[0]["number"] == 24
    assert sovereigns[0]["name"] == "Địa Lôi Phục"
    assert sovereigns[5]["number"] == 1
    assert sovereigns[5]["name"] == "Thuần Càn"
    assert sovereigns[11]["number"] == 2
    assert sovereigns[11]["name"] == "Thuần Khôn"


def test_simulate_transition():
    """Test state transition simulation when lines change."""
    # Thuần Càn (111111) with line 1 moving -> Thiên Phong Cấu (011111 - lower Tốn 011, upper Càn 111 = #44)
    res = iching_service.simulate_transition(1, [1])
    assert res["status"] == "success"
    assert res["primary_hexagram"]["number"] == 1
    assert res["moving_lines"] == [1]
    assert res["transformed_hexagram"]["number"] == 44
    assert res["transformed_hexagram"]["name"] == "Thiên Phong Cấu"
    assert "Thiên Phong Cấu" in res["transition_summary"]

    # Thuần Khôn (000000) with line 1 moving -> Địa Lôi Phục (100000 - lower Chấn 100, upper Khôn 000 = #24)
    res2 = iching_service.simulate_transition("Thuần Khôn", [1])
    assert res2["status"] == "success"
    assert res2["transformed_hexagram"]["number"] == 24
    assert res2["transformed_hexagram"]["name"] == "Địa Lôi Phục"

    # All 6 lines moving on Thuần Càn -> Thuần Khôn
    res3 = iching_service.simulate_transition(1, [1, 2, 3, 4, 5, 6])
    assert res3["transformed_hexagram"]["number"] == 2


def test_hydrated_relations_on_get():
    """Verify get_hexagram hydrates nuclear, opposite, and inverted hexagrams."""
    h = iching_service.get_hexagram(1)
    assert h is not None
    assert "nuclear_hexagram" in h
    assert h["nuclear_hexagram"]["number"] == 1
    assert "opposite_hexagram" in h
    assert h["opposite_hexagram"]["number"] == 2
    assert "inverted_hexagram" in h
    assert h["inverted_hexagram"]["number"] == 1

    # Thủy Lôi Truân (#3)
    truan = iching_service.get_hexagram(3)
    assert truan is not None
    assert truan["nuclear_hexagram"]["number"] == 23 # Sơn Địa Bác
    assert truan["inverted_hexagram"]["number"] == 4 # Sơn Thủy Mông


def test_stance_and_tag_filters():
    """Verify filtering by stance and tag."""
    tien = iching_service.list_hexagrams(stance="Tiến")
    assert tien
    assert all(h["strategic_stance"] == "Tiến" for h in tien)

    khoi_nghiep = iching_service.list_hexagrams(tag="khởi_nghiệp_sơ_khai")
    assert any(h["number"] == 3 for h in khoi_nghiep)
