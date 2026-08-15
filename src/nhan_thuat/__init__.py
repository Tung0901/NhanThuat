"""Core package for the Nhân Thuật knowledge system."""

from nhan_thuat.knowledge_engine import (
    FALLBACK_INSUFFICIENT_KNOWLEDGE,
    IndexedUnit,
    KnowledgeEngine,
)

__version__ = "1.0.0"
__all__ = ["FALLBACK_INSUFFICIENT_KNOWLEDGE", "IndexedUnit", "KnowledgeEngine"]
