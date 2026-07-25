"""
Public Provider interface for NhanThuat Contract V1.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from .contracts import (
    KnowledgeQuery,
    KnowledgeResult,
    KnowledgeUnitSummary,
    ReasoningRequest,
    ReasoningResult,
    ContractVersion,
)
from .capabilities import CapabilityDescriptor


class NhanThuatProviderV1(ABC):
    """
    Stable abstract provider interface. External consumers must program against this
    interface, not the internal KnowledgeEngine.
    """

    @abstractmethod
    def get_unit(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific knowledge unit by its ID."""
        pass

    @abstractmethod
    def query_knowledge(self, query: KnowledgeQuery) -> KnowledgeResult:
        """Query knowledge units matching the given filters."""
        pass

    @abstractmethod
    def list_domain_units(self, domain_slug: str) -> List[KnowledgeUnitSummary]:
        """List all units within a specific domain."""
        pass

    @abstractmethod
    def reason(self, request: ReasoningRequest) -> ReasoningResult:
        """Process a reasoning request through the NhanThuat engine."""
        pass

    @abstractmethod
    def list_capabilities(self) -> List[CapabilityDescriptor]:
        """Return the list of currently implemented capabilities."""
        pass

    @abstractmethod
    def get_contract_metadata(self) -> ContractVersion:
        """Return the contract version metadata."""
        pass
