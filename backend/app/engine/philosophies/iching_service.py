"""
Draft I Ching catalog lookup service.
Oracle output is unavailable until the algorithm and interpretation pass review.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent / "iching_64_hexagrams.json"


class IChingService:
    """Service for searching, retrieving, and consulting the 64 Hexagrams of I Ching."""

    def __init__(self, data_file: Path | None = None) -> None:
        self.data_file = data_file or DATA_PATH
        self._data: dict[str, Any] = {}
        self._hexagrams: list[dict[str, Any]] = []
        self._by_number: dict[int, dict[str, Any]] = {}
        self._by_name: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.data_file.exists():
            try:
                self._data = json.loads(self.data_file.read_text(encoding="utf-8"))
                self._hexagrams = self._data.get("hexagrams", [])
                for h in self._hexagrams:
                    num = int(h.get("number", 0))
                    self._by_number[num] = h
                    name = h.get("name", "").strip().lower()
                    if name:
                        self._by_name[name] = h
            except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
                print(f"[WARN] Failed to load I Ching hexagrams data: {exc}")

    @property
    def total_count(self) -> int:
        return len(self._hexagrams)

    def list_hexagrams(self, palace: str = "", query: str = "") -> list[dict[str, Any]]:
        """List hexagrams with optional palace filter or keyword search."""
        res = self._hexagrams
        if palace:
            p_clean = palace.strip().lower()
            res = [h for h in res if p_clean in h.get("palace", "").lower()]

        if query:
            q_clean = query.strip().lower()
            res = [
                h for h in res
                if q_clean in h.get("name", "").lower()
                or q_clean in h.get("corporate_state", "").lower()
                or q_clean in h.get("strategic_warning", "").lower()
                or q_clean in h.get("action_script", "").lower()
                or q_clean in h.get("nature", "").lower()
                or str(h.get("number")) == q_clean
            ]
        return res

    def get_hexagram(self, ref: int | str) -> dict[str, Any] | None:
        """Find a hexagram by number (1..64), ID ('HEX-01'), or Vietnamese name."""
        if isinstance(ref, int) or (isinstance(ref, str) and ref.isdigit()):
            return self._by_number.get(int(ref))

        ref_str = str(ref).strip().lower()
        if not ref_str:
            return None
        if ref_str.startswith("hex-"):
            clean_num = ref_str.replace("hex-", "").lstrip("0")
            if clean_num.isdigit():
                return self._by_number.get(int(clean_num))

        if ref_str in self._by_name:
            return self._by_name[ref_str]

        for h in self._hexagrams:
            if ref_str in h.get("name", "").lower():
                return h
        return None

    def cast_oracle(self, inquiry: str = "", seed: int | None = None) -> dict[str, Any]:
        """Do not emit divination or executive advice from an unverified algorithm."""
        return {
            "status": "error",
            "error_code": "ORACLE_UNAVAILABLE",
            "epistemic_status": "unreviewed",
            "message": (
                "Phần gieo quẻ đang được thẩm định phương pháp và nguồn nội dung; "
                "chưa cung cấp kết quả hay chỉ đạo điều hành."
            ),
        }


# Global Singleton
iching_service = IChingService()
