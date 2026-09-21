"""
Nhân Thuật Behavioral Service.
Ingests human input (messages, daily reports, task notes).
Queries Jev AI Decision Adapter for 3 core metrics:
- burnout_risk (Noul / Boolean)
- stress_score (Score / Scale 1 to 5)
- behavior_style (Choice / DISC: "D" | "I" | "S" | "C")
Emits structured behavioral evaluation events.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from modules.decider.adapter import DecisionResult, DecisionSchema, JevDecisionAdapter


@dataclass(frozen=True)
class HumanInputRecord:
    """Human input record representing messages, daily reports, or task notes."""
    content: str
    author_id: str = "EMP-DEFAULT"
    input_id: str = field(default_factory=lambda: f"INP-{uuid.uuid4().hex[:8].upper()}")
    source_type: str = "message"  # "message" | "daily_report" | "task_note"
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BehavioralEvaluationEvent:
    """Structured event emitted upon analyzing human behavioral input."""
    event_id: str
    input_id: str
    author_id: str
    burnout_risk: bool
    burnout_risk_confidence: float
    stress_score: int
    stress_score_confidence: float
    behavior_style: str  # "D" | "I" | "S" | "C"
    behavior_style_confidence: float
    timestamp: float
    raw_decisions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "input_id": self.input_id,
            "author_id": self.author_id,
            "burnout_risk": self.burnout_risk,
            "burnout_risk_confidence": round(self.burnout_risk_confidence, 4),
            "stress_score": self.stress_score,
            "stress_score_confidence": round(self.stress_score_confidence, 4),
            "behavior_style": self.behavior_style,
            "behavior_style_confidence": round(self.behavior_style_confidence, 4),
            "timestamp": self.timestamp,
        }


class NhanThuatBehavioralService:
    """
    Ingests unstructured employee communication and extracts psychological/behavioral signals
    using the Jev System-1 Decision Adapter.
    """

    def __init__(self, decider: JevDecisionAdapter | None = None) -> None:
        self.decider = decider or JevDecisionAdapter()

    def evaluate(
        self,
        human_input: HumanInputRecord | str,
        author_id: str = "EMP-DEFAULT",
        source_type: str = "message",
    ) -> BehavioralEvaluationEvent:
        """
        Evaluate human input and emit a structured BehavioralEvaluationEvent.
        """
        if isinstance(human_input, str):
            record = HumanInputRecord(
                content=human_input,
                author_id=author_id,
                source_type=source_type,
            )
        else:
            record = human_input

        # 1. Query burnout_risk (Noul / Boolean)
        burnout_res: DecisionResult = self.decider.decide(
            text_state=record.content,
            schema=DecisionSchema(type="noul", threshold=0.5),
        )

        # 2. Query stress_score (Score / Scale 1 to 5)
        stress_res: DecisionResult = self.decider.decide(
            text_state=record.content,
            schema=DecisionSchema(type="score", scale_min=1.0, scale_max=5.0),
        )

        # 3. Query behavior_style (Choice / DISC: "D" | "I" | "S" | "C")
        style_res: DecisionResult = self.decider.decide(
            text_state=record.content,
            schema=DecisionSchema(type="choice", options=["D", "I", "S", "C"]),
        )

        event = BehavioralEvaluationEvent(
            event_id=f"EVT-NT-{uuid.uuid4().hex[:10].upper()}",
            input_id=record.input_id,
            author_id=record.author_id,
            burnout_risk=bool(burnout_res.decision),
            burnout_risk_confidence=float(burnout_res.confidence),
            stress_score=int(stress_res.decision),
            stress_score_confidence=float(stress_res.confidence),
            behavior_style=str(style_res.decision),
            behavior_style_confidence=float(style_res.confidence),
            timestamp=time.time(),
            raw_decisions={
                "burnout_risk": burnout_res.to_dict(),
                "stress_score": stress_res.to_dict(),
                "behavior_style": style_res.to_dict(),
            },
        )

        return event
