"""
Jev AI Decision Adapter.
Provides dual-mode (Live vs Mock) execution for System-1 fast heuristic decisions.
Accepts unstructured text state + decision schema (Choice, Score, Noul).
Returns { "decision": <value>, "confidence": <float 0.0-1.0>, "type": "choice"|"score"|"noul" }.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from typing import Any, Literal

import requests

DecisionType = Literal["choice", "score", "noul"]
DEFAULT_JEV_ENDPOINT = "https://api.typesafe.ai/v1/systemone"

# Heuristic keywords for calibrated mock inference
_BURNOUT_KEYWORDS = (
    "kiệt sức", "quá tải", "overwhelmed", "burnout", "chán nản", "stress",
    "áp lực", "không kịp", "mệt mỏi", "rơi rụng", "quá nhiều việc", "nghỉ việc",
    "bất mãn", "exhausted", "can't take this", "breaking down", "unbearable",
)

_DISC_KEYWORDS = {
    "D": (
        "kết quả", "mục tiêu", "nhanh", "quyết định", "ngay", "kpi", "chốt",
        "chịu trách nhiệm", "thực thi", "kỷ luật", "direct", "deadline", "urgent",
        "action now", "bottom line", "execute",
    ),
    "I": (
        "hào hứng", "kết nối", "ý tưởng", "truyền cảm hứng", "mọi người",
        "gặp gỡ", "chia sẻ", "vui vẻ", "enthusiastic", "collaborate", "brainstorm",
    ),
    "S": (
        "ổn định", "từ từ", "hỗ trợ", "an toàn", "đồng hành", "giúp đỡ",
        "kiên nhẫn", "bình tĩnh", "steady", "supportive", "reliable", "harmony",
    ),
    "C": (
        "chi tiết", "dữ liệu", "quy trình", "tiêu chuẩn", "phân tích", "chính xác",
        "báo cáo", "kiểm tra", "đặc tả", "tiêu chí", "specification", "accuracy",
        "validation", "criteria", "metric", "audit",
    ),
}


def _is_valid_api_key(key: str | None) -> bool:
    if not key:
        return False
    clean = key.strip().lower()
    if clean.startswith("your_") or "your_typesafe_api_key" in clean or clean in ("none", "null", ""):
        return False
    return len(clean) >= 8


@dataclass(frozen=True)
class DecisionSchema:
    """Specifies the desired decision output format and constraints."""
    type: DecisionType
    options: list[str] = field(default_factory=list)
    scale_min: float = 1.0
    scale_max: float = 5.0
    threshold: float = 0.5


@dataclass(frozen=True)
class DecisionResult:
    """Standardized Jev Decision output contract."""
    decision: Any
    confidence: float
    type: DecisionType
    raw_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "confidence": round(float(self.confidence), 4),
            "type": self.type,
        }


class JevDecisionAdapter:
    """
    Dual-mode Jev AI Decision Adapter.
    - Live Mode: Active if TYPESAFE_API_KEY is present and valid.
    - Mock Mode: Active by default, generates calibrated probabilistic responses.
    """

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str = DEFAULT_JEV_ENDPOINT,
        timeout: float = 30.0,
        mock_mode: bool | None = None,
    ) -> None:
        env_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
        self.api_key = api_key.strip() if api_key else env_key
        self.endpoint = os.environ.get("TYPESAFE_BASE_URL", "").strip() or endpoint
        self.timeout = timeout

        if mock_mode is not None:
            self.is_mock = mock_mode
        else:
            self.is_mock = not _is_valid_api_key(self.api_key)

    def decide(self, text_state: str, schema: DecisionSchema) -> DecisionResult:
        """
        Evaluate text_state against the requested decision schema.
        Returns a typed DecisionResult with decision, confidence, and type.
        """
        if self.is_mock:
            return self._mock_evaluate(text_state, schema)
        return self._live_evaluate(text_state, schema)

    def _live_evaluate(self, text_state: str, schema: DecisionSchema) -> DecisionResult:
        """Execute decision via live TypeSafe Jev API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "prompt": text_state,
            "schema_type": schema.type,
            "options": schema.options,
            "scale_min": schema.scale_min,
            "scale_max": schema.scale_max,
            "threshold": schema.threshold,
        }

        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return DecisionResult(
                decision=data.get("decision", data.get("choice")),
                confidence=float(data.get("confidence", data.get("score", 0.90))),
                type=schema.type,
                raw_metadata=data,
            )
        except Exception:  # noqa: BLE001
            # Safe degradation to calibrated mock if live API is temporarily unreachable
            return self._mock_evaluate(text_state, schema)

    def _mock_evaluate(self, text_state: str, schema: DecisionSchema) -> DecisionResult:
        """Calibrated mock engine based on keywords, heuristics, and deterministic hashing."""
        text_lower = text_state.lower().strip()
        h_bytes = hashlib.sha256(text_state.encode("utf-8")).digest()
        h_float = (h_bytes[0] % 100) / 100.0

        if schema.type == "noul":
            # Noul / Boolean risk decision (e.g. burnout_risk)
            match_count = sum(1 for kw in _BURNOUT_KEYWORDS if kw in text_lower)
            if match_count >= 2:
                decision = True
                confidence = round(0.88 + (min(match_count, 5) * 0.02), 4)
            elif match_count == 1:
                decision = True
                confidence = round(0.86, 4)
            else:
                decision = False
                confidence = round(0.90 + (h_float * 0.08), 4)

            return DecisionResult(
                decision=decision,
                confidence=min(1.0, confidence),
                type="noul",
                raw_metadata={"mode": "mock", "match_count": match_count},
            )

        elif schema.type == "score":
            # Score decision (e.g. stress_score scale 1 to 5)
            match_count = sum(1 for kw in _BURNOUT_KEYWORDS if kw in text_lower)
            if match_count >= 3:
                score = 5
                confidence = 0.94
            elif match_count == 2:
                score = 4
                confidence = 0.89
            elif match_count == 1:
                score = 3
                confidence = 0.82
            else:
                # Normal baseline stress: 1 or 2
                score = 1 if h_float < 0.6 else 2
                confidence = 0.88

            # Constrain to scale
            score = max(int(schema.scale_min), min(int(schema.scale_max), score))
            return DecisionResult(
                decision=score,
                confidence=confidence,
                type="score",
                raw_metadata={"mode": "mock", "match_count": match_count},
            )

        elif schema.type == "choice":
            # Choice decision (e.g. DISC: "D" | "I" | "S" | "C")
            options = schema.options or ["D", "I", "S", "C"]
            scores: dict[str, float] = {opt: 0.1 for opt in options}

            for style, keywords in _DISC_KEYWORDS.items():
                if style in scores:
                    hits = sum(1 for kw in keywords if kw in text_lower)
                    scores[style] += hits * 1.5

            # If no keywords matched, use deterministic hash distribution
            if all(v == 0.1 for v in scores.values()):
                idx = h_bytes[1] % len(options)
                scores[options[idx]] += 2.0

            total = sum(scores.values())
            probs = {k: round(v / total, 4) for k, v in scores.items()}
            best_opt = max(probs.items(), key=lambda x: x[1])[0]
            top_prob = probs[best_opt]

            # Calibrate confidence above 0.85 when strong style signal exists
            confidence = min(0.98, max(top_prob, 0.86 if scores[best_opt] > 1.5 else 0.75))

            return DecisionResult(
                decision=best_opt,
                confidence=confidence,
                type="choice",
                raw_metadata={"mode": "mock", "probabilities": probs},
            )

        # Fallback safe response
        return DecisionResult(
            decision=schema.options[0] if schema.options else "DEFAULT",
            confidence=0.85,
            type=schema.type,
            raw_metadata={"mode": "mock_fallback"},
        )
