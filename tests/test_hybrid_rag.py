"""
Test Suite for Phase 2: Hybrid RAG Engine (BM25 + Dense Vector Search + RRF Fusion).
Tests lexical search, semantic embeddings, rank fusion, multi-tier relationship expansion, and latency.
"""

import time
from pathlib import Path

import pytest

from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.models import KnowledgeUnit
from nhan_thuat.rag.bm25_search import BM25Engine
from nhan_thuat.rag.hybrid_retriever import HybridRetriever
from nhan_thuat.rag.normalizer import extract_unit_text_corpus, strip_accents, tokenize
from nhan_thuat.rag.vector_search import LocalDenseEmbedder, VectorSearchEngine
from nhan_thuat.runtime.resolver import KnowledgeResolver


@pytest.fixture(scope="module")
def sample_units() -> list[KnowledgeUnit]:
    engine = KnowledgeEngine()
    return [
        KnowledgeUnit.from_mapping(iu.raw_data, source_path=None)
        for iu in engine.units_by_id.values()
    ]


def test_normalizer_accent_stripping() -> None:
    text = "Hợp đồng cung cấp vật tư chậm tiến độ tại công trình"
    normalized = strip_accents(text)
    assert "Hop dong cung cap vat tu cham tien do tai cong trinh" in normalized or "hop dong" in normalized.lower()
    
    tokens = tokenize("Khách hàng chê báo giá đắt hơn đối thủ!")
    assert "khach" in tokens or "khách" in tokens
    assert "gia" in tokens or "giá" in tokens
    assert "dat" in tokens or "đắt" in tokens


def test_normalizer_extract_unit_text_corpus() -> None:
    sample_data = {
        "id": "NT-LAW-TEST",
        "title": "Quy luật đòn bẩy",
        "summary": "Tác động nhỏ tạo thay đổi lớn.",
        "definition": "Định nghĩa đòn bẩy trong quản trị.",
        "tags": ["leverage", "strategy"],
        "primary_domain": "thanh-su",
    }
    corpus = extract_unit_text_corpus(sample_data)
    assert "NT-LAW-TEST" in corpus
    assert "Quy luật đòn bẩy" in corpus
    assert "leverage" in corpus


def test_bm25_engine_search_accuracy(sample_units: list[KnowledgeUnit]) -> None:
    bm25 = BM25Engine(units=sample_units)
    assert len(bm25.units) >= 370
    assert len(bm25.vocab) > 100

    # Search for specific law keyword
    results = bm25.search("quy luật lợi ích chi phối hành vi", top_k=3)
    assert len(results) >= 1
    top_hit = results[0]
    assert "NT-LAW-0001" in top_hit.unit_id or "lợi ích" in str(getattr(top_hit.unit, "title", "")).lower()
    assert top_hit.score > 0.0
    assert 0.0 <= top_hit.normalized_score <= 1.0
    assert len(top_hit.match_details.matched_terms) >= 1


def test_dense_vector_embedder_and_search(sample_units: list[KnowledgeUnit], tmp_path: Path) -> None:
    embedder = LocalDenseEmbedder(dim=128)
    vec1 = embedder.embed_text("xung đột nội bộ tranh chấp quyền lợi")
    vec2 = embedder.embed_text("mâu thuẫn tổ đội bất đồng lương thưởng")
    vec3 = embedder.embed_text("công thức toán học giải tích vi phân")

    assert vec1.shape == (128,)
    # Semantic cosine similarity should be higher between related management topics than unrelated topics
    sim_related = float(vec1 @ vec2)
    sim_unrelated = float(vec1 @ vec3)
    assert sim_related > sim_unrelated

    # Test VectorSearchEngine with cache
    cache_file = tmp_path / ".vector_cache.json"
    v_engine = VectorSearchEngine(units=sample_units[:20], cache_path=cache_file, dim=128)
    v_results = v_engine.search("quy luật lợi ích và động lực", top_k=3)
    assert len(v_results) == 3
    assert v_results[0].score >= v_results[1].score
    assert cache_file.exists()


def test_hybrid_retriever_rrf_and_latency(sample_units: list[KnowledgeUnit], tmp_path: Path) -> None:
    cache_file = tmp_path / ".vector_cache.json"
    vector_engine = VectorSearchEngine(units=sample_units, cache_path=cache_file, dim=128)
    bm25_engine = BM25Engine(units=sample_units)
    hybrid = HybridRetriever(units=sample_units, bm25_engine=bm25_engine, vector_engine=vector_engine)

    query = "đối tác nợ quá hạn không chịu thanh toán tiền hàng"
    t_start = time.perf_counter()
    result = hybrid.retrieve(query, top_k=5, expand_relations=True)
    latency_ms = (time.perf_counter() - t_start) * 1000

    assert len(result.primary_units) == 5
    assert len(result.fusion_items) == 5
    assert result.total_latency_ms < 500.0  # Fast retrieval under 500ms
    assert "bm25_latency_ms" in result.latency_breakdown
    assert "vector_latency_ms" in result.latency_breakdown

    # Verify RRF score ordering
    scores = list(result.scores.values())
    assert scores == sorted(scores, reverse=True)


def test_hybrid_retriever_multi_tier_expansion(sample_units: list[KnowledgeUnit]) -> None:
    hybrid = HybridRetriever(units=sample_units)
    query = "công trình chậm tiến độ do vật tư"
    result = hybrid.retrieve(query, top_k=3, expand_relations=True)

    assert len(result.primary_units) >= 1
    # Check that related units map is populated
    top_id = result.fusion_items[0].unit_id
    assert top_id in result.related_units_map
    related_links = result.related_units_map[top_id]
    assert isinstance(related_links, list)
    if related_links:
        first_link = related_links[0]
        assert hasattr(first_link, "relation_type")
        assert hasattr(first_link, "unit_id")
        assert hasattr(first_link, "title")


def test_knowledge_resolver_hybrid_integration(sample_units: list[KnowledgeUnit]) -> None:
    resolver = KnowledgeResolver(sample_units)
    hybrid_res = resolver.resolve_hybrid("đàm phán giá cao xử lý từ chối", limit=4)

    assert len(hybrid_res.primary_units) == 4
    assert hybrid_res.total_latency_ms >= 0.0

    # Ensure classic resolve still works as expected
    classic_res = resolver.resolve("khủng hoảng truyền thông", limit=3)
    assert len(classic_res) <= 3
