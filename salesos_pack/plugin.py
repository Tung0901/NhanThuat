"""
SalesOS Industry Solution Pack Entrypoint Plugin.
Exposes SalesOSPlugin for registration through ExtensionRegistry.
"""

import json
from pathlib import Path
from typing import Any, Dict
from salesos_pack.capabilities.lead_intake_capability import LeadIntakeCapability
from salesos_pack.personas.sales_ops_coordinator import SalesOpsCoordinatorPersona
from salesos_pack.schemas.domain_contracts import WorkflowResult


class SalesOSPlugin:
    """SalesOS Industry Solution Pack Plugin Entrypoint."""

    plugin_id: str = "com.nhanthuat.salesos"
    plugin_name: str = "SalesOS Industry Solution Pack"
    version: str = "1.0.0"

    def __init__(self) -> None:
        self.manifest_path = Path(__file__).resolve().parent / "plugin.json"
        self.manifest_data = self._load_manifest()
        self.capability = LeadIntakeCapability()
        self.persona = SalesOpsCoordinatorPersona()

    def _load_manifest(self) -> Dict[str, Any]:
        if self.manifest_path.exists():
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"error": "Manifest plugin.json not found"}

    def health_check(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "version": self.version,
            "status": "HEALTHY",
            "capability_id": self.capability.capability_id,
            "persona_id": self.persona.persona_id,
            "active_leads_count": len(self.capability.lead_repository),
            "manifest_verified": "plugin_id" in self.manifest_data,
        }

    def process_lead(
        self,
        payload: Dict[str, Any],
        simulate_unverified_fallback: bool = False
    ) -> WorkflowResult:
        """Execute lead intake and assignment workflow."""
        return self.capability.process_lead_intake(payload, simulate_unverified_fallback)
