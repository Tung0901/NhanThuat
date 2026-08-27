"""
Data models for Multi-Agent Advisory Council in NhanThuat.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class CouncilMember:
    agent_id: str  # 'LEGALISM', 'TAOISM', 'CONFUCIAN', 'XUNZI', 'SUNZI'
    title: str
    school_of_thought: str
    core_focus: str
    icon: str


@dataclass
class PerspectivePitch:
    agent_id: str
    title: str
    stance: str
    core_arguments: list[str]
    cited_unit_ids: list[str] = field(default_factory=list)
    citations: list[dict[str, str]] = field(default_factory=list)
    risk_warning: str = ""


@dataclass
class CrossDebatePoint:
    challenger_id: str
    target_id: str
    critique: str
    counter_recommendation: str


@dataclass
class DecisionMatrix:
    highest_consensus: str
    core_conflicts: list[str]
    plan_a_primary: dict[str, Any]
    plan_b_fallback: dict[str, Any]
    plan_c_containment: dict[str, Any]
    critical_caveats: list[str]
    execution_directives: list[str]


@dataclass
class CouncilDeliberationResult:
    session_id: str
    scenario_text: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    pitches: list[PerspectivePitch] = field(default_factory=list)
    cross_debates: list[CrossDebatePoint] = field(default_factory=list)
    decision_matrix: DecisionMatrix | None = None
    total_latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
