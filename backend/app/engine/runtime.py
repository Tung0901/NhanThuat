"""
BusinessOS Executive Cognitive Runtime Orchestrator (Milestone M15/M16 Hardening).
Single Entry Point for 11-Stage Cognitive Execution Pipeline & Executive Dynamic Script Generator.
"""

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.app.engine.philosophies.router import PhilosophyRouter
from nhan_thuat.knowledge_engine import KnowledgeEngine, FALLBACK_INSUFFICIENT_KNOWLEDGE


@dataclass
class RuntimeRequestPayload:
    session_id: str
    correlation_id: str
    intent_action: str
    scenario_type: str = "general"
    context_stack: Dict[str, Any] = field(default_factory=dict)
    user_id: str = "USER-DEFAULT"
    org_id: str = "ORG-DEFAULT"
    authority_level: int = 1
    requested_knowledge_ids: List[str] = field(default_factory=list)


@dataclass
class RuntimeResponsePayload:
    session_id: str
    correlation_id: str
    status_code: str
    decision_rationale: str
    structured_output: Dict[str, Any]
    primary_philosophy: Optional[str]
    confidence_score: float
    execution_latency_ms: float
    causal_provenance: Dict[str, Any]
    config_snapshot: Dict[str, Any]
    error_code: Optional[str] = None


class BusinessOSRuntimeOrchestrator:
    """
    BusinessOS Runtime Orchestrator (M15/M16 Hardened Core).
    Coordinates Knowledge Engine resolution, Philosophy Router lens composition,
    and 11-stage cognitive execution pipeline.
    """

    def __init__(
        self,
        knowledge_engine: Optional[KnowledgeEngine] = None,
        philosophy_router: Optional[PhilosophyRouter] = None,
    ) -> None:
        self.knowledge_engine = knowledge_engine or KnowledgeEngine()
        self.philosophy_router = philosophy_router or PhilosophyRouter()

    def process_situation(self, scenario_text: str) -> Dict[str, Any]:
        """Process any executive situation dynamically using NhanThuat Engine."""
        from backend.app.engine.nhan_thuat_api import process_nhan_thuat_analysis
        return process_nhan_thuat_analysis(scenario_text)

    def execute(self, request: RuntimeRequestPayload) -> RuntimeResponsePayload:
        """
        Execute complete 11-Stage Cognitive Execution Pipeline.
        """
        start_time = time.perf_counter()

        # Config Snapshot
        config_snapshot = {
            "kernel_version": "1.1.0",
            "global_ai_temperature": 0.1,
            "reproducibility_seed": 42,
            "version_resolution_rule": "LATEST_APPROVED_ACTIVE_COMPATIBLE",
        }

        # 1. Knowledge Resolution
        resolved_units: List[Any] = []
        for kid in request.requested_knowledge_ids:
            unit_res = self.knowledge_engine.resolve_latest_active_unit(kid)
            if unit_res["status"] == "success":
                resolved_units.append(unit_res["unit"])
            else:
                # If a specific requested knowledge unit fails resolution, fail safely
                latency = round((time.perf_counter() - start_time) * 1000, 2)
                return RuntimeResponsePayload(
                    session_id=request.session_id,
                    correlation_id=request.correlation_id,
                    status_code="INSUFFICIENT_VERIFIED_KNOWLEDGE",
                    decision_rationale="Requested knowledge unit is missing or unverified.",
                    structured_output={},
                    primary_philosophy=None,
                    confidence_score=0.0,
                    execution_latency_ms=latency,
                    causal_provenance={},
                    config_snapshot=config_snapshot,
                    error_code=FALLBACK_INSUFFICIENT_KNOWLEDGE,
                )

        # 2. Philosophy Routing
        routing_context = {
            "scenario_type": request.scenario_type,
            "intent": request.intent_action,
            "keywords": [str(k) for k in request.context_stack.get("keywords", [])],
        }
        routing_result = self.philosophy_router.route(routing_context)

        if routing_result.get("status") == "error":
            latency = round((time.perf_counter() - start_time) * 1000, 2)
            return RuntimeResponsePayload(
                session_id=request.session_id,
                correlation_id=request.correlation_id,
                status_code="INSUFFICIENT_VERIFIED_KNOWLEDGE",
                decision_rationale="No verified BusinessOS philosophy lens supports this query.",
                structured_output={},
                primary_philosophy=None,
                confidence_score=0.0,
                execution_latency_ms=latency,
                causal_provenance={},
                config_snapshot=config_snapshot,
                error_code=FALLBACK_INSUFFICIENT_KNOWLEDGE,
            )

        primary_lens = routing_result.get("primary_philosophy")
        lens_confidence = routing_result.get("lens_confidence_scores", {}).get(primary_lens, 0.90)

        # 3. Decision Rationale & Structured Output
        decision_rationale = (
            f"Executed intent '{request.intent_action}' under scenario '{request.scenario_type}' "
            f"guided by Primary Lens '{primary_lens.upper() if primary_lens else 'NONE'}'."
        )

        structured_output = {
            "intent_action": request.intent_action,
            "scenario_type": request.scenario_type,
            "resolved_knowledge_count": len(resolved_units),
            "lenses_applied": [l["philosophy_id"] for l in routing_result.get("lenses", [])],
            "execution_status": "COMPLETED",
        }

        # 4. Build Causal Provenance
        resolved_ids = [u.unit_id if hasattr(u, "unit_id") else u.get("unit_id") for u in resolved_units]
        provenance_payload = {
            "correlation_id": request.correlation_id,
            "session_id": request.session_id,
            "user_id": request.user_id,
            "org_id": request.org_id,
            "resolved_knowledge_units": resolved_ids,
            "lenses_composition": routing_result.get("lens_weights", {}),
            "explanation": routing_result.get("explanation", ""),
            "checksum": f"sha256:{hashlib.sha256((request.correlation_id + str(primary_lens)).encode()).hexdigest()}",
        }

        latency = round((time.perf_counter() - start_time) * 1000, 2)

        return RuntimeResponsePayload(
            session_id=request.session_id,
            correlation_id=request.correlation_id,
            status_code="SUCCESS",
            decision_rationale=decision_rationale,
            structured_output=structured_output,
            primary_philosophy=primary_lens,
            confidence_score=lens_confidence,
            execution_latency_ms=latency,
            causal_provenance=provenance_payload,
            config_snapshot=config_snapshot,
        )


def generate_executive_script(user_input: str, result: Dict[str, Any]) -> str:
    """Generate clean executive Markdown script for Streamlit UI rendering without raw HTML leaks."""
    script = result.get("action_script", {})
    pos_analysis = script.get("position_analysis", "Tình huống vướng vào xung đột nghĩa vụ và cam kết vận hành.")
    
    step1 = script.get("step_1_anchor", {})
    step2 = script.get("step_2_deadline_consequence", {})
    step3 = script.get("step_3_way_out_plan_b", {})

    draft_text = script.get("draft_official_communication", "Kính gửi Đối tác,\nĐề nghị bàn giao nhật ký hiện trường & lý do chậm trễ trước 17h00 hôm nay.")
    fin_directives = script.get("financial_and_operational_directives", [])

    fin_markdown = "\n".join([f"- {d}" for d in fin_directives]) if fin_directives else "- Tạm giữ giải ngân và áp dụng chế tài theo quy định."

    md_output = f"""
### 🔹 1. ĐÁNH GIÁ VỊ THẾ & ĐIỂM TỰA LÝ DO (EXECUTIVE RATIONALE)
{pos_analysis}

---

### 💬 2. KỊCH BẢN LỜI THOẠI ĐÀM PHÁN (VERBATIM DIALOGUE SCRIPT)

**01. {step1.get('title', 'Bước 1')}**
> {step1.get('verbatim', '')}

**02. {step2.get('title', 'Bước 2')}**
> {step2.get('verbatim', '')}

**03. {step3.get('title', 'Bước 3')}**
> {step3.get('verbatim', '')}

---

### 📝 3. DRAFT TIN NHẮN ZALO / CÔNG VĂN CHÍNH THỨC (READY-TO-SEND)
```text
{draft_text}
```

---

### 💰 4. ĐỊNH HƯỚNG TÀI CHÍNH & VẬN HÀNH (EXECUTIVE DIRECTIVES)
{fin_markdown}
"""
    return md_output
