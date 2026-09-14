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
    "BM25Engine",
    "BM25MatchDetail",
    "BM25Result",
    "FusionItem",
    "HybridRetrievalResult",
    "HybridRetriever",
    "LocalDenseEmbedder",
    "RelatedUnitLink",
    "VectorResult",
    "VectorSearchEngine",
    "extract_unit_text_corpus",
    "strip_accents",
    "tokenize",
]
