"""
Public Provider interface for NhanThuat Contract V1.
"""
from abc import ABC, abstractmethod
from typing import Any

from .capabilities import CapabilityDescriptor
from .contracts import (
    ContractVersion,
    KnowledgeQuery,
    KnowledgeResult,
    KnowledgeUnitSummary,
    ReasoningRequest,
    ReasoningResult,
)


class NhanThuatProviderV1(ABC):
    """
    Stable abstract provider interface. External consumers must program against this
    interface, not the internal KnowledgeEngine.
    """

    @abstractmethod
    def get_unit(self, unit_id: str) -> dict[str, Any] | None:
        """Retrieve a specific knowledge unit by its ID."""

    @abstractmethod
    def query_knowledge(self, query: KnowledgeQuery) -> KnowledgeResult:
        """Query knowledge units matching the given filters."""

    @abstractmethod
    def list_domain_units(self, domain_slug: str) -> list[KnowledgeUnitSummary]:
        """List all units within a specific domain."""

    @abstractmethod
    def reason(self, request: ReasoningRequest) -> ReasoningResult:
        """Process a reasoning request through the NhanThuat engine."""

    @abstractmethod
    def list_capabilities(self) -> list[CapabilityDescriptor]:
        """Return the list of currently implemented capabilities."""

    @abstractmethod
    def get_contract_metadata(self) -> ContractVersion:
        """Return the contract version metadata."""
