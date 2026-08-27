"""
RAG (Retrieval-Augmented Generation) & Hybrid Semantic Search Engine Package for NhanThuat.
"""

from nhan_thuat.rag.bm25_search import BM25Engine, BM25MatchDetail, BM25Result
from nhan_thuat.rag.hybrid_retriever import (
    FusionItem,
    HybridRetrievalResult,
    HybridRetriever,
    RelatedUnitLink,
)
from nhan_thuat.rag.normalizer import extract_unit_text_corpus, strip_accents, tokenize
from nhan_thuat.rag.vector_search import (
    LocalDenseEmbedder,
    VectorResult,
    VectorSearchEngine,
)

__all__ = [
    "strip_accents",
    "tokenize",
    "extract_unit_text_corpus",
    "BM25Engine",
    "BM25Result",
    "BM25MatchDetail",
    "LocalDenseEmbedder",
    "VectorSearchEngine",
    "VectorResult",
    "HybridRetriever",
    "HybridRetrievalResult",
    "FusionItem",
    "RelatedUnitLink",
]
