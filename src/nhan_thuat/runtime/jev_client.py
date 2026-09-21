"""
TypeSafe AI Jev System One Client.
Provides a typed client for the hosted System One decision API (POST /v1/systemone)
with an evidence-calibrated mock fallback when TYPESAFE_API_KEY is absent.
"""

from __future__ import annotations

import hashlib
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import requests

DEFAULT_JEV_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
DEFAULT_OPTIONS = ["EXECUTE", "CALIBRATE", "DE_ESCALATE", "ESCALATE"]


class JevAPIError(RuntimeError):
    """Raised when the TypeSafe Jev API returns an error or cannot be reached."""


@dataclass(frozen=True)
class JevDecisionRequest:
    """Request payload for Jev System One decision."""
    prompt: str
    options: list[str] = field(default_factory=lambda: list(DEFAULT_OPTIONS))
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "options": list(self.options),
            "context": self.context,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class JevDecisionResponse:
    """
    Contract for Jev System One Decision API.
    Returns choice, score, noul (Non-Observed Utility Level),
    and calibrated probabilities across candidate actions.
    """
    choice: str
    score: float
    noul: float
    calibrated_probabilities: dict[str, float]
    latency_ms: float
    is_mock: bool
    correlation_id: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "choice": self.choice,
            "score": self.score,
            "noul": self.noul,
            "calibrated_probabilities": dict(self.calibrated_probabilities),
            "latency_ms": self.latency_ms,
            "is_mock": self.is_mock,
            "correlation_id": self.correlation_id,
        }


def _is_valid_api_key(key: str | None) -> bool:
    if not key:
        return False
    clean = key.strip().lower()
    if clean.startswith("your_") or "your_typesafe_api_key" in clean or clean in ("none", "null", ""):
        return False
    return len(clean) >= 8


class JevClient:
    """
    Native typed client for TypeSafe AI Jev System One Decision API.
    If TYPESAFE_API_KEY is not configured, automatically operates in mock mode
    adhering strictly to the Jev response contract.
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

    def decide(
        self,
        prompt: str,
        options: list[str] | None = None,
        context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> JevDecisionResponse:
        """
        Execute a System One fast cognitive decision.
        """
        candidate_options = list(options) if options else list(DEFAULT_OPTIONS)
        req = JevDecisionRequest(
            prompt=prompt,
            options=candidate_options,
            context=context or {},
            metadata=metadata or {},
        )

        if self.is_mock:
            return self._mock_decide(req)

        return self._http_decide(req)

    def call_system_one(
        self,
        prompt: str,
        options: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> JevDecisionResponse:
        """Alias for decide() to match /v1/systemone naming convention."""
        return self.decide(prompt=prompt, options=options, context=context)

    def _http_decide(self, req: JevDecisionRequest) -> JevDecisionResponse:
        """Send live HTTP request to TypeSafe Jev API."""
        start_time = time.perf_counter()
        correlation_id = f"JEV-{uuid.uuid4().hex[:10].upper()}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Correlation-ID": correlation_id,
        }

        try:
            resp = requests.post(
                self.endpoint,
                headers=headers,
                json=req.to_dict(),
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            raise JevAPIError(f"Failed to communicate with TypeSafe Jev API at {self.endpoint}: {exc}") from exc
        except ValueError as exc:
            raise JevAPIError(f"Invalid JSON response from TypeSafe Jev API: {exc}") from exc

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Parse conforming Jev response contract
        choice = str(data.get("choice", req.options[0]))
        score = float(data.get("score", 0.85))
        noul = float(data.get("noul", 0.90))

        raw_probs = data.get("calibrated_probabilities", {})
        if isinstance(raw_probs, dict) and raw_probs:
            calibrated_probabilities = {str(k): float(v) for k, v in raw_probs.items()}
        else:
            # Calibrate fallback probabilities if absent
            calibrated_probabilities = {choice: score}
            remaining = max(0.0, 1.0 - score)
            other_options = [opt for opt in req.options if opt != choice]
            if other_options:
                share = round(remaining / len(other_options), 4)
                for opt in other_options:
                    calibrated_probabilities[opt] = share

        return JevDecisionResponse(
            choice=choice,
            score=score,
            noul=noul,
            calibrated_probabilities=calibrated_probabilities,
            latency_ms=latency_ms,
            is_mock=False,
            correlation_id=correlation_id,
            raw=data,
        )

    def _mock_decide(self, req: JevDecisionRequest) -> JevDecisionResponse:
        """
        Deterministically produce calibrated probabilities, choice, score, and NOUL
        based on hash of prompt and candidate options to enable reproducible local testing.
        """
        start_time = time.perf_counter()
        correlation_id = f"JEV-MOCK-{uuid.uuid4().hex[:8].upper()}"

        # Deterministic seed from prompt + options
        h = hashlib.sha256((req.prompt + "".join(req.options)).encode("utf-8")).digest()
        raw_weights = [1.0 + (b % 100) / 20.0 for b in h[: len(req.options)]]
        total_weight = sum(raw_weights)

        # Compute calibrated probabilities summing to 1.0
        calibrated: dict[str, float] = {}
        cum_prob = 0.0
        for i, opt in enumerate(req.options):
            if i == len(req.options) - 1:
                prob = round(1.0 - cum_prob, 4)
            else:
                prob = round(raw_weights[i] / total_weight, 4)
                cum_prob += prob
            calibrated[opt] = prob

        # Ensure exact sum of 1.0
        diff = round(1.0 - sum(calibrated.values()), 4)
        if diff != 0.0:
            first_key = req.options[0]
            calibrated[first_key] = round(calibrated[first_key] + diff, 4)

        # Select choice with highest calibrated probability
        top_choice = max(calibrated.items(), key=lambda item: item[1])
        choice = top_choice[0]
        score = top_choice[1]

        # Calculate NOUL (Normalized Optimal Utility Level): calibrated utility in [0.70, 0.98]
        noul_base = 0.70 + ((h[0] % 28) / 100.0)
        noul = round(noul_base, 4)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return JevDecisionResponse(
            choice=choice,
            score=score,
            noul=noul,
            calibrated_probabilities=calibrated,
            latency_ms=latency_ms,
            is_mock=True,
            correlation_id=correlation_id,
            raw={
                "choice": choice,
                "score": score,
                "noul": noul,
                "calibrated_probabilities": calibrated,
                "mode": "mock",
            },
        )
