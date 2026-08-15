"""
NhanThuat Public Contract V1.
"""
from .capabilities import CapabilityDescriptor
from .compatibility import CompatibilityMetadata
from .contracts import (
    ContractVersion,
    KnowledgeQuery,
    KnowledgeResult,
    KnowledgeUnitSummary,
    ReasoningRequest,
    ReasoningResult,
)
from .errors import InsufficientVerifiedKnowledgeError, PublicError
from .provenance import ProvenanceRecord
from .provider import NhanThuatProviderV1
from .registry import ContractRegistry, registry
from .serializers import serialize_contract

__all__ = [
    "CapabilityDescriptor",
    "CompatibilityMetadata",
    "ContractRegistry",
    "ContractVersion",
    "InsufficientVerifiedKnowledgeError",
    "KnowledgeQuery",
    "KnowledgeResult",
    "KnowledgeUnitSummary",
    "NhanThuatProviderV1",
    "ProvenanceRecord",
    "PublicError",
    "ReasoningRequest",
    "ReasoningResult",
    "registry",
    "serialize_contract",
]
