"""
SALESOS-PERSONA-001 — Sales Operations Coordinator Persona.
Respects BusinessOS Level 2 Authority limits and strict verified company policy rules.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class TemperamentVector:
    conservative_vs_aggressive: float = 0.60
    analytical_vs_intuitive: float = 0.70
    deliberate_vs_fast: float = 0.60
    independent_vs_collaborative: float = 0.70
    procedural_vs_exploratory: float = 0.30


class SalesOpsCoordinatorPersona:
    """Sales Operations Coordinator Persona (SALESOS-PERSONA-001)."""

    persona_id: str = "SALESOS-PERSONA-001"
    persona_name: str = "Sales Operations Coordinator"
    authority_level: int = 2  # Level 2 Authority — Operate & Recommend within defined rules
    temperament_vector: TemperamentVector = TemperamentVector()
    preferred_lenses: List[str] = ("LENS-RHETORIC", "LENS-CONFUCIAN")

    def get_persona_spec(self) -> Dict[str, Any]:
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "authority_level": self.authority_level,
            "temperament_vector": {
                "conservative_vs_aggressive": self.temperament_vector.conservative_vs_aggressive,
                "analytical_vs_intuitive": self.temperament_vector.analytical_vs_intuitive,
                "deliberate_vs_fast": self.temperament_vector.deliberate_vs_fast,
                "independent_vs_collaborative": self.temperament_vector.independent_vs_collaborative,
                "procedural_vs_exploratory": self.temperament_vector.procedural_vs_exploratory,
            },
            "preferred_lenses": list(self.preferred_lenses),
        }
