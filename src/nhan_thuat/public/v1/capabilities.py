"""
Capabilities catalog for NhanThuat Contract V1.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class CapabilityDescriptor:
    capability_id: str
    version: str
    name: str
    description: str
    input_contract: str
    output_contract: str
    status: str  # e.g., "IMPLEMENTED", "PLANNED"
    deterministic_behavior: bool
    required_contract_version: str


# The registry of currently implemented capabilities in NhanThuat
NHANTHUAT_CAPABILITIES = [
    CapabilityDescriptor(
        capability_id="NHANTHUAT-CAP-001",
        version="1.0",
        name="Knowledge Query",
        description="Query the verified NhanThuat knowledge base by domain, type, or tag.",
        input_contract="KnowledgeQuery",
        output_contract="KnowledgeResult",
        status="IMPLEMENTED",
        deterministic_behavior=True,
        required_contract_version="v1.0.0"
    ),
    CapabilityDescriptor(
        capability_id="NHANTHUAT-CAP-002",
        version="1.0",
        name="Philosophical Routing and Reasoning",
        description="Reason over an input scenario to determine the best philosophical lens and recommended actions.",
        input_contract="ReasoningRequest",
        output_contract="ReasoningResult",
        status="PLANNED",
        deterministic_behavior=False,  # Can depend on router heuristics
        required_contract_version="v1.0.0"
    ),
]
