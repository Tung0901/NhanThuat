"""Evaluation logic for adherence to knowledge units."""

from typing import Any, Iterable

from nhan_thuat.models import KnowledgeUnit


class KnowledgeEvaluator:
    """Evaluates text/plans for adherence to knowledge units and constraints."""

    def __init__(self):
        pass

    def evaluate(self, content: str, units: Iterable[KnowledgeUnit]) -> dict[str, Any]:
        """
        Evaluate if a given content text adheres to the provided knowledge units.
        This provides a heuristic rule-based check or prepares metadata for LLM-based evaluation.
        
        Args:
            content: The text to evaluate.
            units: The knowledge units to enforce.
            
        Returns:
            A dictionary containing evaluation metrics, violations, and confidence scores.
        """
        result = {
            "score": 100.0,
            "violations": [],
            "warnings": [],
            "aligned_units": []
        }
        
        content_lower = content.lower()
        
        for unit in units:
            unit_aligned = False
            
            # Simple keyword tracking for alignment
            if unit.type in ("anti-pattern", "phenomenon"):
                # For anti-patterns and phenomena, check if the content seems to trigger it
                # In a real implementation, an LLM evaluator should verify this
                for risk in unit.risks:
                    if risk.lower() in content_lower:
                        result["score"] -= 10.0
                        result["violations"].append(f"Potential Risk Triggered: {unit.id} - Risk detected: {risk}")
            else:
                # For laws and principles, check if key concepts are mentioned
                unit_aligned = any(tag.lower() in content_lower for tag in unit.tags)
                if unit_aligned:
                    result["aligned_units"].append(unit.id)
                else:
                    result["warnings"].append(f"Content might not incorporate: {unit.id} ({unit.title})")
                    
        # Ensure score is bounded
        result["score"] = max(0.0, min(100.0, result["score"]))
        
        return result
