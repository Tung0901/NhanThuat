"""Prompt assembly from knowledge units."""

from collections.abc import Iterable

from nhan_thuat.models import KnowledgeUnit


class PromptBuilder:
    """Assembles context from knowledge units for LLM prompts."""

    def __init__(self):
        pass

    def build_context(self, units: Iterable[KnowledgeUnit], format_type: str = "markdown") -> str:
        """
        Build a formatted context string from a set of knowledge units.
        
        Args:
            units: The knowledge units to include.
            format_type: The format to generate (default: markdown).
            
        Returns:
            A formatted string containing the combined knowledge context.
        """
        if format_type != "markdown":
            raise ValueError(f"Unsupported format type: {format_type}")
            
        parts = ["# Nhan Thuat Knowledge Context\n"]
        
        for unit in units:
            parts.append(f"## {unit.title} ({unit.id})")
            parts.append(f"**Type:** {unit.type}")
            parts.append(f"**Domain:** {unit.primary_domain}")
            parts.append("\n### Summary")
            parts.append(unit.summary)
            
            parts.append("\n### Definition")
            parts.append(unit.definition)
            
            if unit.mechanism:
                parts.append("\n### Mechanism")
                for step in unit.mechanism:
                    parts.append(f"- {step}")
                    
            if unit.conditions:
                parts.append("\n### Conditions")
                for condition in unit.conditions:
                    parts.append(f"- {condition}")
                    
            if unit.risks:
                parts.append("\n### Risks")
                for risk in unit.risks:
                    parts.append(f"- {risk}")
                    
            parts.append("\n---\n")
            
        return "\n".join(parts)
