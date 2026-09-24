"""
Continuous Behavioral Profiler & Flight Risk Early-Warning Engine.
Module: modules.nhan_thuat.continuous_profiler

Operationalizes Nhan Thuat formal models:
- NT-MODEL-0008: Default Expression Under Load (Biểu hiện mặc định khi quá tải).
- NT-MODEL-0011: Context Behavior Predictive Model (Dự báo hành vi theo bối cảnh).
- NT-MODEL-0007: Person-Role Fit (Độ tương thích người và vai trò).

Provides real-time streaming profile computation, stress trajectory tracking,
burnout velocity, and flight risk radar.
"""

from __future__ import annotations

import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any

from modules.nhan_thuat.service import BehavioralEvaluationEvent


@dataclass(frozen=True)
class LoadExpressionBehavior:
    """Represents behavioral revert tendencies under high cognitive/emotional load (NT-MODEL-0008)."""
    disc_style: str
    stress_threshold: int
    default_tendency: str
    operational_risk: str
    mitigation_strategy: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Default Expression Under Load Matrix (NT-MODEL-0008 mapping)
LOAD_EXPRESSION_CATALOG: dict[str, LoadExpressionBehavior] = {
    "D": LoadExpressionBehavior(
        disc_style="D",
        stress_threshold=4,
        default_tendency="Độc đoán áp đặt, bỏ qua quy trình tham vấn, dễ bộc phát xung đột trực diện.",
        operational_risk="Gây rạn nứt niềm tin đội ngũ, ép tiến độ bất chấp an toàn hệ thống, tạo phản ứng ngầm.",
        mitigation_strategy="Giao toàn quyền trong phạm vi có rào chắn số liệu (guardrails), yêu cầu báo cáo chỉ số khách quan.",
    ),
    "I": LoadExpressionBehavior(
        disc_style="I",
        stress_threshold=4,
        default_tendency="Mất tập trung, ra quyết định theo cảm xúc bốc đồng, hứa hẹn vượt quá khả năng thực thi.",
        operational_risk="Bỏ sót chi tiết kỹ thuật, xáo trộn ưu tiên dự án, gây hoang mang truyền thông nội bộ.",
        mitigation_strategy="Bổ sung trợ lý kỹ thuật kèm cặp (anchor), định lượng hóa cam kết thành checklist cụ thể.",
    ),
    "S": LoadExpressionBehavior(
        disc_style="S",
        stress_threshold=4,
        default_tendency="Bằng mặt không bằng lòng, trì hoãn thụ động, thu mình im lặng né tránh đối thoại.",
        operational_risk="Điểm nghẽn thông tin ngầm, ngấm ngầm tìm đường rút lui, nộp đơn nghỉ việc bất ngờ.",
        mitigation_strategy="Tạo không gian an toàn tâm lý (Psychological Safety), chủ động tháo gỡ áp lực không phán xét.",
    ),
    "C": LoadExpressionBehavior(
        disc_style="C",
        stress_threshold=4,
        default_tendency="Cầu toàn cực đoan (Analysis Paralysis), bắt bẻ câu chữ chi tiết, từ chối nghiệm thu.",
        operational_risk="Làm chậm trễ tiến độ toàn chuỗi, từ chối thỏa hiệp dù tình thế khẩn cấp, cô lập bản thân.",
        mitigation_strategy="Giới hạn rõ ràng khung thời gian ra quyết định, xác lập tiêu chuẩn 'đủ tốt' (Good Enough Threshold).",
    ),
}


@dataclass(frozen=True)
class ContextStrengthEvaluation:
    """Evaluates contextual situation strength affecting individual vs environment dominance (NT-MODEL-0011)."""
    situation_strength: str  # "STRONG" | "MODERATE" | "WEAK"
    clarity_level: float     # 0.0 - 1.0 (Quy chế rõ ràng)
    consistency_level: float # 0.0 - 1.0 (Thực thi nhất quán)
    constraints_level: float # 0.0 - 1.0 (Rào cản hành vi)
    dominant_determinant: str # "ENVIRONMENT_SITUATION" vs "PERSONALITY_TRAITS"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ContinuousBehavioralProfile:
    """Aggregated continuous profile of an individual over streaming interactions."""
    author_id: str
    sample_count: int
    baseline_disc: str
    disc_distribution: dict[str, float]
    average_stress: float
    stress_trajectory: list[int]
    burnout_velocity: float  # Slope of stress over recent interactions
    current_burnout_risk: bool
    flight_risk_score: float  # 0.0 - 1.0
    flight_risk_level: str   # "LOW" | "ELEVATED" | "CRITICAL"
    under_load_forecast: LoadExpressionBehavior
    context_strength: ContextStrengthEvaluation
    recommended_interventions: list[str] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "author_id": self.author_id,
            "sample_count": self.sample_count,
            "baseline_disc": self.baseline_disc,
            "disc_distribution": self.disc_distribution,
            "average_stress": round(self.average_stress, 2),
            "stress_trajectory": self.stress_trajectory,
            "burnout_velocity": round(self.burnout_velocity, 2),
            "current_burnout_risk": self.current_burnout_risk,
            "flight_risk_score": round(self.flight_risk_score, 2),
            "flight_risk_level": self.flight_risk_level,
            "under_load_forecast": self.under_load_forecast.to_dict(),
            "context_strength": self.context_strength.to_dict(),
            "recommended_interventions": self.recommended_interventions,
            "last_updated": self.last_updated,
        }


class ContinuousBehavioralProfiler:
    """Stateful continuous profiler maintaining longitudinal employee profiles."""

    def __init__(self) -> None:
        self._history: dict[str, list[BehavioralEvaluationEvent]] = {}
        self._profiles: dict[str, ContinuousBehavioralProfile] = {}

    def ingest_event(
        self,
        event: BehavioralEvaluationEvent,
        context_clarity: float = 0.8,
        context_constraints: float = 0.7,
    ) -> ContinuousBehavioralProfile:
        """Ingest a new behavioral event and update the author's continuous profile."""
        author_id = event.author_id
        self._history.setdefault(author_id, []).append(event)
        events = self._history[author_id]

        sample_count = len(events)
        stress_trajectory = [e.stress_score for e in events]
        avg_stress = sum(stress_trajectory) / sample_count

        # Compute burnout velocity (difference between recent 3 and earlier average)
        if sample_count >= 3:
            recent_avg = sum(stress_trajectory[-3:]) / 3.0
            earlier_avg = sum(stress_trajectory[:-3]) / len(stress_trajectory[:-3]) if len(stress_trajectory) > 3 else stress_trajectory[0]
            burnout_velocity = recent_avg - earlier_avg
        else:
            burnout_velocity = 0.0

        # Compute DISC baseline & distribution
        styles = [e.behavior_style for e in events]
        counts = Counter(styles)
        disc_dist = {s: round(counts.get(s, 0) / sample_count, 3) for s in ["D", "I", "S", "C"]}
        baseline_disc = counts.most_common(1)[0][0] if counts else event.behavior_style

        # Evaluate Context Strength (NT-MODEL-0011)
        clarity = max(0.0, min(1.0, context_clarity))
        constraints = max(0.0, min(1.0, context_constraints))
        strength_score = (clarity + constraints) / 2.0
        if strength_score >= 0.75:
            situation_str = "STRONG"
            determinant = "ENVIRONMENT_SITUATION"
        elif strength_score >= 0.45:
            situation_str = "MODERATE"
            determinant = "BALANCED_INTERACTION"
        else:
            situation_str = "WEAK"
            determinant = "PERSONALITY_TRAITS"

        context_eval = ContextStrengthEvaluation(
            situation_strength=situation_str,
            clarity_level=clarity,
            consistency_level=0.85,
            constraints_level=constraints,
            dominant_determinant=determinant,
        )

        # Load expression under load forecast (NT-MODEL-0008)
        load_forecast = LOAD_EXPRESSION_CATALOG.get(
            baseline_disc, LOAD_EXPRESSION_CATALOG["S"]
        )

        # Calculate Flight Risk Score (0.0 to 1.0)
        # Factors: High stress + burnout flag + high burnout velocity + low stability
        flight_risk = 0.10
        if event.burnout_risk:
            flight_risk += 0.40
        if avg_stress >= 4.0:
            flight_risk += 0.30
        elif avg_stress >= 3.0:
            flight_risk += 0.15
        if burnout_velocity > 0.8:
            flight_risk += 0.20

        flight_risk = max(0.05, min(0.98, flight_risk))
        if flight_risk >= 0.70:
            risk_level = "CRITICAL"
        elif flight_risk >= 0.40:
            risk_level = "ELEVATED"
        else:
            risk_level = "LOW"

        # Formulate actionable interventions
        interventions: list[str] = []
        if risk_level == "CRITICAL":
            interventions.append("Kích hoạt ngay chế độ giảm tải công việc (Workload Throttle) trong 48 giờ.")
            interventions.append(f"Áp dụng sách lược ứng phó phong cách {baseline_disc}: {load_forecast.mitigation_strategy}")
            interventions.append("Thiết lập phiên đối thoại 1-1 kín tháo gỡ uẩn ức theo lăng kính Nho Gia / Đạo Gia.")
        elif risk_level == "ELEVATED":
            interventions.append(f"Theo dõi sát sao biểu hiện phong cách {baseline_disc} khi đối mặt deadline lớn.")
            interventions.append("Tăng cường độ rõ ràng của bối cảnh (Context Clarity) để giảm thiểu áp lực tự điều chỉnh.")
        else:
            interventions.append("Duy trì nhịp độ giao việc ổn định và ghi nhận định kỳ các cột mốc hoàn thành.")

        profile = ContinuousBehavioralProfile(
            author_id=author_id,
            sample_count=sample_count,
            baseline_disc=baseline_disc,
            disc_distribution=disc_dist,
            average_stress=avg_stress,
            stress_trajectory=stress_trajectory,
            burnout_velocity=burnout_velocity,
            current_burnout_risk=event.burnout_risk,
            flight_risk_score=flight_risk,
            flight_risk_level=risk_level,
            under_load_forecast=load_forecast,
            context_strength=context_eval,
            recommended_interventions=interventions,
            last_updated=time.time(),
        )

        self._profiles[author_id] = profile
        return profile

    def get_profile(self, author_id: str) -> ContinuousBehavioralProfile | None:
        """Retrieve current profile by author_id."""
        return self._profiles.get(author_id)

    def get_team_radar(self) -> dict[str, Any]:
        """Aggregate all tracked employee profiles into a managerial radar view."""
        if not self._profiles:
            return {
                "status": "empty",
                "total_monitored": 0,
                "critical_flight_risk_count": 0,
                "profiles": [],
            }

        critical_count = sum(1 for p in self._profiles.values() if p.flight_risk_level == "CRITICAL")
        elevated_count = sum(1 for p in self._profiles.values() if p.flight_risk_level == "ELEVATED")

        return {
            "status": "success",
            "total_monitored": len(self._profiles),
            "critical_flight_risk_count": critical_count,
            "elevated_flight_risk_count": elevated_count,
            "profiles": [p.to_dict() for p in self._profiles.values()],
        }

    def seed_demo_data(self) -> None:
        """Seed initial realistic personnel profiles for the flight risk radar."""
        if self._profiles:
            return

        now = time.time()
        demo_profiles = [
            ContinuousBehavioralProfile(
                author_id="EMP-LONG (Nguyễn Hoàng Long - VP Eng)",
                sample_count=8,
                baseline_disc="D",
                disc_distribution={"D": 0.65, "I": 0.15, "S": 0.05, "C": 0.15},
                average_stress=4.2,
                stress_trajectory=[3, 3, 4, 4, 5],
                burnout_velocity=0.68,
                current_burnout_risk=False,
                flight_risk_score=0.55,
                flight_risk_level="ELEVATED",
                under_load_forecast=LOAD_EXPRESSION_CATALOG["D"],
                context_strength=ContextStrengthEvaluation(
                    situation_strength="MODERATE",
                    clarity_level=0.5,
                    consistency_level=0.7,
                    constraints_level=0.4,
                    dominant_determinant="PERSONALITY_TRAITS",
                ),
                recommended_interventions=[
                    "Theo dõi sát biểu hiện độc đoán áp đặt khi đối mặt hạn chót chuyển giao hệ thống.",
                    "Thiết lập rào chắn số liệu (guardrails) và yêu cầu đối thoại khách quan tránh cọ xát cá nhân.",
                ],
                last_updated=now - 1200,
            ),
            ContinuousBehavioralProfile(
                author_id="EMP-HA (Trần Thu Hà - Head of Product)",
                sample_count=12,
                baseline_disc="I",
                disc_distribution={"D": 0.10, "I": 0.60, "S": 0.20, "C": 0.10},
                average_stress=4.8,
                stress_trajectory=[3, 4, 4, 5, 5],
                burnout_velocity=0.89,
                current_burnout_risk=True,
                flight_risk_score=0.88,
                flight_risk_level="CRITICAL",
                under_load_forecast=LOAD_EXPRESSION_CATALOG["I"],
                context_strength=ContextStrengthEvaluation(
                    situation_strength="WEAK",
                    clarity_level=0.3,
                    consistency_level=0.4,
                    constraints_level=0.3,
                    dominant_determinant="PERSONALITY_TRAITS",
                ),
                recommended_interventions=[
                    "Kích hoạt ngay chế độ giảm tải công việc (Workload Throttle) trong 48 giờ.",
                    "Bổ sung trợ lý kỹ thuật kèm cặp (anchor) để định lượng hóa và tháo gỡ khối lượng cam kết.",
                    "Thiết lập phiên đối thoại 1-1 kín tháo gỡ uẩn ức theo lăng kính Nho Gia / Đạo Gia.",
                ],
                last_updated=now - 600,
            ),
            ContinuousBehavioralProfile(
                author_id="EMP-TUAN (Lê Quốc Tuấn - Ops Lead)",
                sample_count=6,
                baseline_disc="C",
                disc_distribution={"D": 0.10, "I": 0.10, "S": 0.20, "C": 0.60},
                average_stress=2.2,
                stress_trajectory=[2, 2, 3, 2, 2],
                burnout_velocity=0.15,
                current_burnout_risk=False,
                flight_risk_score=0.18,
                flight_risk_level="LOW",
                under_load_forecast=LOAD_EXPRESSION_CATALOG["C"],
                context_strength=ContextStrengthEvaluation(
                    situation_strength="STRONG",
                    clarity_level=0.8,
                    consistency_level=0.8,
                    constraints_level=0.8,
                    dominant_determinant="ENVIRONMENT_SITUATION",
                ),
                recommended_interventions=[
                    "Duy trì nhịp độ giao việc ổn định và ghi nhận định kỳ các cột mốc hoàn thành.",
                ],
                last_updated=now - 3600,
            ),
            ContinuousBehavioralProfile(
                author_id="EMP-TRANG (Phạm Minh Trang - Customer Success)",
                sample_count=9,
                baseline_disc="S",
                disc_distribution={"D": 0.05, "I": 0.25, "S": 0.60, "C": 0.10},
                average_stress=3.6,
                stress_trajectory=[2, 3, 3, 4, 4],
                burnout_velocity=0.52,
                current_burnout_risk=False,
                flight_risk_score=0.48,
                flight_risk_level="ELEVATED",
                under_load_forecast=LOAD_EXPRESSION_CATALOG["S"],
                context_strength=ContextStrengthEvaluation(
                    situation_strength="MODERATE",
                    clarity_level=0.6,
                    consistency_level=0.5,
                    constraints_level=0.6,
                    dominant_determinant="PERSONALITY_TRAITS",
                ),
                recommended_interventions=[
                    "Tạo không gian an toàn tâm lý (Psychological Safety) để lắng nghe khó khăn.",
                    "Tránh áp đặt các thay đổi đột ngột làm xáo trộn cảm giác an toàn và ổn định.",
                ],
                last_updated=now - 1800,
            ),
        ]
        for p in demo_profiles:
            self._profiles[p.author_id] = p


# Global singleton instance
continuous_profiler = ContinuousBehavioralProfiler()
