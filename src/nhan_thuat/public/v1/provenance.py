"""
Provenance contracts for NhanThuat Contract V1.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProvenanceRecord:
    correlation_id: str
    session_id: str
    timestamp_utc: str
    accessed_units: list[str] = field(default_factory=list)
    decision_trace: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
