"""
Living Case Dossiers Service (Kho 30 Án Điển Giải Phẫu Sống).
Provides filtering, full-text search, and scenario-based case matching for real-world power, field crisis, and high-stakes negotiation dossiers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LivingCasesService:
    """Service managing the 30 living case dossiers in knowledge/cases/living_dossiers.json."""

    def __init__(self, data_path: Path | None = None) -> None:
        if data_path is None:
            repo_root = Path(__file__).resolve().parents[3]
            data_path = repo_root / "knowledge" / "cases" / "living_dossiers.json"
        self.data_path = data_path
        self._dossiers: list[dict[str, Any]] = []
        self._by_id: dict[str, dict[str, Any]] = {}
        self.reload()

    def reload(self) -> None:
        if not self.data_path.exists():
            self._dossiers = []
            self._by_id = {}
            return
        raw = json.loads(self.data_path.read_text(encoding="utf-8"))
        dossiers = raw.get("dossiers", []) if isinstance(raw, dict) else []
        self._dossiers = [d for d in dossiers if isinstance(d, dict)]
        self._by_id = {str(d.get("id", "")).upper(): d for d in self._dossiers if d.get("id")}

    def list_dossiers(
        self,
        category: str | None = None,
        query: str | None = None,
    ) -> dict[str, Any]:
        items = list(self._dossiers)
        if category and category.strip() and category.strip() != "all":
            cat_norm = category.strip().lower()
            items = [d for d in items if str(d.get("category", "")).lower() == cat_norm]

        if query and query.strip():
            q_norm = query.strip().lower()
            filtered = []
            for d in items:
                haystack = " ".join(
                    [
                        str(d.get("id", "")),
                        str(d.get("title", "")),
                        str(d.get("industry", "")),
                        str(d.get("power_map", "")),
                        str(d.get("fatal_mistake", "")),
                        " ".join(str(k) for k in d.get("keywords", [])),
                    ]
                ).lower()
                if q_norm in haystack:
                    filtered.append(d)
            items = filtered

        categories_summary = {
            "all": len(self._dossiers),
            "internal_power": sum(1 for d in self._dossiers if d.get("category") == "internal_power"),
            "field_crisis": sum(1 for d in self._dossiers if d.get("category") == "field_crisis"),
            "high_stakes_negotiation": sum(
                1 for d in self._dossiers if d.get("category") == "high_stakes_negotiation"
            ),
        }

        return {
            "status": "success",
            "total": len(items),
            "categories_summary": categories_summary,
            "dossiers": items,
        }

    def get_dossier(self, case_id: str) -> dict[str, Any] | None:
        if not case_id:
            return None
        return self._by_id.get(case_id.strip().upper())

    def match_relevant_dossiers(self, scenario_text: str, top_k: int = 2) -> list[dict[str, Any]]:
        if not self._dossiers:
            return []
        text_lower = (scenario_text or "").lower()
        scored: list[tuple[int, int, dict[str, Any]]] = []
        for idx, d in enumerate(self._dossiers):
            score = 0
            for kw in d.get("keywords", []):
                if str(kw).lower() in text_lower:
                    score += 5
            title_words = [w for w in str(d.get("title", "")).lower().split() if len(w) > 3]
            for w in title_words:
                if w in text_lower:
                    score += 1
            cat_keywords = {
                "field_crisis": ["công trường", "nhà thầu", "tiến độ", "vật tư", "đình công", "nghiệm thu"],
                "internal_power": ["cổ đông", "phó tướng", "nhân sự", "bổ nhiệm", "sáng lập", "chi nhánh", "rút ruột"],
                "high_stakes_negotiation": ["ép giá", "thu nợ", "công nợ", "đàm phán", "khủng hoảng", "ngân hàng", "mặt bằng"],
            }
            cat = str(d.get("category", ""))
            if any(k in text_lower for k in cat_keywords.get(cat, [])):
                score += 4
            scored.append((score, -idx, d))

        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [item[2] for item in scored[:top_k]]


cases_service = LivingCasesService()
