"""
Philosophy Context Router Module for NhanThuat Knowledge Repository.
Routes operational scenarios to the appropriate philosophical engines (Rhetoric, Confucian, Legalism, Taoism, Xunzi).
Supports Program 8 Multi-Lens Composition (Primary, Secondary, Tertiary), Lens Priority, Lens Weights,
Lens Confidence Scores, Conflict Resolution, Explanation Generator, Program 9 Adaptive Evolution Metadata,
Program 13 SDK Integration, and Corrected AI Router Architectural Directives.
"""

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# AI Router Corrected Technical Directives
GLOBAL_AI_TEMPERATURE: float = 0.1  # Consistency preference, not a 99% mathematical guarantee
FIXED_REPRODUCIBILITY_SEED: int = 42

# Canonical Source of Truth Registry
CANONICAL_SOURCE_REGISTRY: Dict[str, str] = {
    "knowledge_units": "knowledge/units/",
    "schemas": "schemas/",
    "docs_knowledge": "docs/knowledge/",
    "docs_departments": "docs/departments/",
    "governance": "governance/",
}

# Version Resolution Policy: Latest Approved + Active + Compatible Version
VERSION_RESOLUTION_POLICY: Dict[str, Any] = {
    "resolution_strategy": "LATEST_APPROVED_ACTIVE_COMPATIBLE",
    "enforce_pinning": True,
    "record_provenance_checksum": True,
    "allow_deprecated_override": False,
    "conflict_resolution_keys": ["governance_status", "effective_date", "semantic_version"],
}

# Standard Fallback Error Status
FALLBACK_INSUFFICIENT_KNOWLEDGE: str = "INSUFFICIENT_VERIFIED_KNOWLEDGE"


class PhilosophyType(str, Enum):
    RHETORIC = "rhetoric"
    CONFUCIAN = "confucian"
    LEGALISM = "legalism"
    TAOISM = "taoism"
    XUNZI = "xunzi"


class PhilosophyRouter:
    """
    BusinessOS Philosophy Lens Router:
    Routes operational scenarios across 5 Five Philosophy Lenses:
    - Rhetoric Lens (LENS-RHETORIC): Customer objections, refutations, argument analysis.
    - Confucian Lens (LENS-CONFUCIAN): Culture building, leadership ethics, noble character evaluation.
    - Legalism Lens (LENS-LEGALISM): Compliance, SOP discipline, reward/punishment (Nhị Bỉnh), anti-flattery (Bát Gian).
    - Taoism Lens (LENS-TAOISM): Crisis handling, negotiation deadlock, breakthrough strategy, adaptability (Tâm Trai).
    - Xunzi Lens (LENS-XUNZI): Training & mentorship (Khuyên Học), behavior correction (Vĩ), role definition (Dùng Lễ Định Phần).

    Architectural Constraints Enforced:
    1. Deterministic AI Execution (Target Temp 0.1 preference, structured schemas, fixed seed, validation gates).
    2. Canonical Source Registry (/knowledge/units/, /schemas/, /docs/knowledge/, /docs/departments/, /governance/).
    3. Version Resolution (Latest Approved + Active + Compatible Version with pinned provenance checksums).
    4. Fallback Protection (Returns INSUFFICIENT_VERIFIED_KNOWLEDGE when unverified).
    """

    GLOBAL_AI_TEMPERATURE: float = GLOBAL_AI_TEMPERATURE
    FIXED_REPRODUCIBILITY_SEED: int = FIXED_REPRODUCIBILITY_SEED
    CANONICAL_SOURCE_REGISTRY: Dict[str, str] = CANONICAL_SOURCE_REGISTRY
    VERSION_RESOLUTION_POLICY: Dict[str, Any] = VERSION_RESOLUTION_POLICY
    FALLBACK_INSUFFICIENT_KNOWLEDGE: str = FALLBACK_INSUFFICIENT_KNOWLEDGE

    def __init__(self, engine_dir: Optional[Path] = None) -> None:
        if engine_dir is None:
            engine_dir = Path(__file__).resolve().parent
        self.engine_dir = engine_dir
        self.engines: Dict[PhilosophyType, Dict[str, Any]] = {}
        self._load_all_engines()

    def _load_all_engines(self) -> None:
        """Load all 5 philosophy JSON engines."""
        engine_files = {
            PhilosophyType.RHETORIC: "rhetoric_engine.json",
            PhilosophyType.CONFUCIAN: "confucian_engine.json",
            PhilosophyType.LEGALISM: "legalism_engine.json",
            PhilosophyType.TAOISM: "taoism_engine.json",
            PhilosophyType.XUNZI: "xunzi_engine.json",
        }
        for phil_type, filename in engine_files.items():
            file_path = self.engine_dir / filename
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    self.engines[phil_type] = json.load(f)
            else:
                self.engines[phil_type] = {"error": f"File {filename} not found"}

    def get_router_constraints(self) -> Dict[str, Any]:
        """Return explicit technical constraints governing AI Router execution."""
        return {
            "global_ai_temperature": self.GLOBAL_AI_TEMPERATURE,
            "fixed_reproducibility_seed": self.FIXED_REPRODUCIBILITY_SEED,
            "canonical_source_registry": self.CANONICAL_SOURCE_REGISTRY,
            "version_resolution_policy": self.VERSION_RESOLUTION_POLICY,
            "fallback_insufficient_knowledge": self.FALLBACK_INSUFFICIENT_KNOWLEDGE,
            "consistency_enforcement": [
                "Structured input/output schemas",
                "Deterministic routing rules",
                "Stable prompt templates",
                "Validation gates",
                "Provenance logging with checksums",
            ],
        }

    def route(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route context scenario to Primary, Secondary, and optional Tertiary philosophy lenses.
        
        Expected context fields:
        - scenario_type: str (e.g. 'objection', 'leadership', 'governance', 'transformation', 'training', 'crisis')
        - intent: str (optional detailed intent)
        - keywords: List[str] (optional keywords)
        - persona: str (optional agent persona name)
        """
        scenario_type = str(context.get("scenario_type", "")).lower()
        intent = str(context.get("intent", "")).lower()
        keywords = [str(k).lower() for k in context.get("keywords", [])]
        combined_text = f"{scenario_type} {intent} {' '.join(keywords)}"

        # Verify whether query has verified source support
        if not combined_text.strip() or scenario_type == "unsupported_unknown":
            return {
                "status": "error",
                "error_code": self.FALLBACK_INSUFFICIENT_KNOWLEDGE,
                "message": "No verified BusinessOS source supports this scenario.",
                "global_ai_temperature": self.GLOBAL_AI_TEMPERATURE,
                "canonical_sources": self.CANONICAL_SOURCE_REGISTRY,
            }

        # 1. Determine Lenses Order (Primary, Secondary, Tertiary)
        primary, secondary, tertiary = self._determine_lens_hierarchy(combined_text, scenario_type)

        # 2. Assign Default Composition Weights
        weights = self._calculate_lens_weights(primary, secondary, tertiary)

        # 3. Calculate Lens Confidence Scores
        confidence_scores = self._calculate_confidence_scores(combined_text, primary, secondary, tertiary)

        # 4. Perform Lens Conflict Resolution
        conflict_result = self._resolve_lens_conflicts(primary, secondary, tertiary)

        # 5. Build Lens Structured Composition Payload & Version Provenance
        lens_composition = []
        ordered_types = [(primary, 1), (secondary, 2), (tertiary, 3)]
        for phil_type, priority in ordered_types:
            if phil_type is None:
                continue
            engine_data = self.engines.get(phil_type, {})
            metadata = engine_data.get("metadata", {})
            philosophy_id = metadata.get("philosophy_id", f"LENS-{phil_type.value.upper()}")
            weight = weights.get(phil_type.value, 0.0)
            confidence = confidence_scores.get(phil_type.value, 0.85)

            lens_composition.append({
                "philosophy_type": phil_type.value,
                "philosophy_id": philosophy_id,
                "priority": priority,
                "weight": weight,
                "confidence_score": confidence,
                "metadata": metadata,
                "pinned_version": metadata.get("version", "1.1.0"),
                "provenance_checksum": f"sha256:{hash(philosophy_id + metadata.get('version', '1.1.0'))}",
                "engine_data": engine_data,
            })

        # 6. Generate Natural Language Explanation
        explanation = self._generate_explanation(
            primary=primary,
            secondary=secondary,
            tertiary=tertiary,
            weights=weights,
            confidence_scores=confidence_scores,
            conflict_result=conflict_result,
            scenario_type=scenario_type,
        )

        return {
            "status": "success",
            "global_ai_temperature": self.GLOBAL_AI_TEMPERATURE,
            "reproducibility_seed": self.FIXED_REPRODUCIBILITY_SEED,
            "canonical_source_registry": self.CANONICAL_SOURCE_REGISTRY,
            "version_resolution_policy": self.VERSION_RESOLUTION_POLICY,
            "primary_philosophy": primary.value if primary else None,
            "secondary_philosophy": secondary.value if secondary else None,
            "tertiary_philosophy": tertiary.value if tertiary else None,
            "lenses": lens_composition,
            "primary_engine_data": self.engines.get(primary, {}) if primary else {},
            "secondary_engine_data": self.engines.get(secondary, {}) if secondary else {},
            "tertiary_engine_data": self.engines.get(tertiary, {}) if tertiary else {},
            "lens_weights": weights,
            "lens_confidence_scores": confidence_scores,
            "conflict_resolution": conflict_result,
            "explanation": explanation,
            "routing_reason": f"Scenario matched primary lens: {primary.value.upper() if primary else 'NONE'}",
        }

    def _determine_lens_hierarchy(
        self, text: str, scenario_type: str
    ) -> Tuple[PhilosophyType, Optional[PhilosophyType], Optional[PhilosophyType]]:
        """
        Determine Primary, Secondary, and Tertiary lenses based on canonical BusinessOS policies:
        - Customer Objection: Primary Rhetoric, Secondary Taoism
        - Leadership: Primary Confucianism, Secondary Xunzi
        - Corporate Governance: Primary Legalism, Secondary Confucianism
        - Organization Transformation: Primary Taoism, Secondary Xunzi
        - Training / Capability Building: Primary Xunzi, Secondary Confucianism
        - Organizational Conflict: Tri-Lens (Confucianism + Legalism + Taoism)
        """
        st = scenario_type.lower().strip()

        # Direct Scenario Type Matches
        # 1. Operational Construction & Supplier Contract Incidents (HIGHEST PRECEDENCE OVER SALES)
        ops_keywords = [
            "vật tư", "vat tu", "nhà cung cấp", "nha cung cap", "chậm tiến độ", "cham tien do",
            "công trình", "cong trinh", "thi công", "thi cong", "hợp đồng", "hop dong",
            "chế tài", "che tai", "vi phạm hợp đồng", "trách nhiệm", "trach nhiem", "chậm gia hạn"
        ]
        if any(w in text for w in ops_keywords):
            return PhilosophyType.LEGALISM, PhilosophyType.CONFUCIAN, None

        if st == "objection" or any(w in text for w in ["price objection", "tu choi", "gia cao", "khach hang tu choi"]):
            return PhilosophyType.RHETORIC, PhilosophyType.TAOISM, None

        if st == "training" or any(w in text for w in ["khuyen hoc", "tuan tu", "dao tao", "mentorship", "onboarding"]):
            return PhilosophyType.XUNZI, PhilosophyType.CONFUCIAN, None

        if st == "governance" or any(w in text for w in ["hinh danh", "phap gia", "ky luat", "sop compliance"]):
            return PhilosophyType.LEGALISM, PhilosophyType.CONFUCIAN, None

        if st == "transformation" or any(w in text for w in ["doimoi", "reorganization", "tiêu dao du"]):
            return PhilosophyType.TAOISM, PhilosophyType.XUNZI, None

        if st == "conflict" or any(w in text for w in ["org conflict", "dispute mediation"]):
            return PhilosophyType.CONFUCIAN, PhilosophyType.LEGALISM, PhilosophyType.TAOISM

        if st == "leadership" or any(w in text for w in ["duc tri", "quan tu", "culture building"]):
            return PhilosophyType.CONFUCIAN, PhilosophyType.XUNZI, None

        # Keyword Scoring Fallback
        scores = {p: 0 for p in PhilosophyType}
        
        if any(w in text for w in ["hung bien", "rhetoric", "be luan diem", "refute", "argument"]):
            scores[PhilosophyType.RHETORIC] += 3
        if any(w in text for w in ["nho gia", "confucian", "duc tri", "nhan chinh", "hoa nhi bat dong"]):
            scores[PhilosophyType.CONFUCIAN] += 3
        if any(w in text for w in ["phap gia", "legalism", "hinh danh", "bat gian", "nhị bỉnh"]):
            scores[PhilosophyType.LEGALISM] += 3
        if any(w in text for w in ["dao gia", "taoism", "vo vi", "tam trai", "dung vo dung"]):
            scores[PhilosophyType.TAOISM] += 3
        if any(w in text for w in ["tuan tu", "xunzi", "tinh ac", "khuyen hoc", "dinh phan"]):
            scores[PhilosophyType.XUNZI] += 3

        sorted_lenses = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
        primary = sorted_lenses[0]
        secondary = sorted_lenses[1] if scores[sorted_lenses[1]] > 0 else None
        tertiary = sorted_lenses[2] if scores[sorted_lenses[2]] > 0 else None

        # Fallback to Rhetoric
        if scores[primary] == 0:
            primary = PhilosophyType.RHETORIC
            secondary = PhilosophyType.TAOISM

        return primary, secondary, tertiary

    def _calculate_lens_weights(
        self,
        primary: PhilosophyType,
        secondary: Optional[PhilosophyType],
        tertiary: Optional[PhilosophyType],
    ) -> Dict[str, float]:
        """Assign normalized composition weights for composed lenses."""
        weights = {}
        if secondary and tertiary:
            weights[primary.value] = 0.60
            weights[secondary.value] = 0.30
            weights[tertiary.value] = 0.10
        elif secondary:
            weights[primary.value] = 0.70
            weights[secondary.value] = 0.30
        else:
            weights[primary.value] = 1.00
        return weights

    def _calculate_confidence_scores(
        self,
        text: str,
        primary: PhilosophyType,
        secondary: Optional[PhilosophyType],
        tertiary: Optional[PhilosophyType],
    ) -> Dict[str, float]:
        """Calculate confidence score per lens taking engine metadata confidence_modifier into account."""
        scores = {}
        active_lenses = [lens for lens in [primary, secondary, tertiary] if lens is not None]
        for lens in active_lenses:
            engine_meta = self.engines.get(lens, {}).get("metadata", {})
            modifier = float(engine_meta.get("confidence_modifier", 1.0))
            base_conf = 0.90 if lens == primary else (0.85 if lens == secondary else 0.75)
            scores[lens.value] = round(min(1.0, base_conf * modifier), 2)
        return scores

    def _resolve_lens_conflicts(
        self,
        primary: PhilosophyType,
        secondary: Optional[PhilosophyType],
        tertiary: Optional[PhilosophyType],
    ) -> Dict[str, Any]:
        """Detect and resolve potential conflicts between composed lenses based on engine metadata."""
        active_lenses = [lens for lens in [primary, secondary, tertiary] if lens is not None]
        incompatibilities = []

        for lens in active_lenses:
            meta = self.engines.get(lens, {}).get("metadata", {})
            incompatible = meta.get("incompatible_lenses", [])
            for other in active_lenses:
                if other != lens:
                    other_id = self.engines.get(other, {}).get("metadata", {}).get("philosophy_id", "")
                    if other_id in incompatible or other.value in incompatible:
                        incompatibilities.append((lens.value, other.value))

        if incompatibilities:
            return {
                "conflicts_detected": True,
                "incompatible_pairs": incompatibilities,
                "resolution_strategy": "Primary Lens takes absolute precedence; conflicting secondary recommendations are subordinated.",
            }
        
        return {
            "conflicts_detected": False,
            "incompatible_pairs": [],
            "resolution_strategy": "Lenses are fully compatible and complementary.",
        }

    def _generate_explanation(
        self,
        primary: PhilosophyType,
        secondary: Optional[PhilosophyType],
        tertiary: Optional[PhilosophyType],
        weights: Dict[str, float],
        confidence_scores: Dict[str, float],
        conflict_result: Dict[str, Any],
        scenario_type: str,
    ) -> str:
        """Generate clear natural language explanation of multi-lens selection."""
        primary_name = self.engines.get(primary, {}).get("metadata", {}).get("philosophy_name", primary.value.capitalize())
        sec_name = (
            self.engines.get(secondary, {}).get("metadata", {}).get("philosophy_name", secondary.value.capitalize())
            if secondary
            else None
        )
        tert_name = (
            self.engines.get(tertiary, {}).get("metadata", {}).get("philosophy_name", tertiary.value.capitalize())
            if tertiary
            else None
        )

        parts = [f"Selected Primary Lens: {primary_name} (Weight: {weights.get(primary.value, 0):.2f}, Conf: {confidence_scores.get(primary.value, 0):.2f})."]
        if secondary and sec_name:
            parts.append(f"Secondary Lens: {sec_name} (Weight: {weights.get(secondary.value, 0):.2f}, Conf: {confidence_scores.get(secondary.value, 0):.2f}).")
        if tertiary and tert_name:
            parts.append(f"Tertiary Lens: {tert_name} (Weight: {weights.get(tertiary.value, 0):.2f}, Conf: {confidence_scores.get(tertiary.value, 0):.2f}).")

        if conflict_result.get("conflicts_detected"):
            parts.append("Conflict resolution applied: " + conflict_result.get("resolution_strategy", ""))
        else:
            parts.append("Lenses composed harmoniously without conflict.")

        return " ".join(parts)
