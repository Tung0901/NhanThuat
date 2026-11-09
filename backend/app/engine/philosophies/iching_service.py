"""
I Ching catalog lookup and strategic phase transition service.
Provides structured access to 64 Hexagrams, 8x8 Coordinates Matrix,
12 Sovereign Hexagrams (Thập Nhị Tức Quái), and Moving-Line Phase Simulation.
Oracle output remains strictly unavailable to preserve epistemic rigor.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent / "iching_64_hexagrams.json"

TRIGRAM_ORDER = ["Càn", "Đoài", "Ly", "Chấn", "Tốn", "Khảm", "Cấn", "Khôn"]


class IChingService:
    """Service for searching, retrieving, matrix mapping, and consulting the 64 Hexagrams of I Ching."""

    def __init__(self, data_file: Path | None = None) -> None:
        self.data_file = data_file or DATA_PATH
        self._data: dict[str, Any] = {}
        self._hexagrams: list[dict[str, Any]] = []
        self._by_number: dict[int, dict[str, Any]] = {}
        self._by_name: dict[str, dict[str, Any]] = {}
        self._by_pattern: dict[str, dict[str, Any]] = {}
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
                    pattern = h.get("binary_pattern", "")
                    if pattern:
                        self._by_pattern[pattern] = h
            except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
                print(f"[WARN] Failed to load I Ching hexagrams data: {exc}")

    @property
    def total_count(self) -> int:
        return len(self._hexagrams)

    def list_hexagrams(
        self,
        palace: str = "",
        query: str = "",
        stance: str = "",
        tag: str = "",
    ) -> list[dict[str, Any]]:
        """List hexagrams with optional palace, stance, tag filter or keyword search."""
        res = self._hexagrams
        if palace:
            p_clean = palace.strip().lower()
            res = [h for h in res if p_clean in h.get("palace", "").lower()]

        if stance:
            s_clean = stance.strip().lower()
            res = [h for h in res if s_clean == h.get("strategic_stance", "").lower()]

        if tag:
            t_clean = tag.strip().lower()
            res = [
                h for h in res
                if any(t_clean in str(tg).lower() for tg in h.get("diagnostic_tags", []))
            ]

        if query:
            q_clean = query.strip().lower()
            res = [
                h for h in res
                if q_clean in h.get("name", "").lower()
                or q_clean in h.get("corporate_state", "").lower()
                or q_clean in h.get("strategic_warning", "").lower()
                or q_clean in h.get("action_script", "").lower()
                or q_clean in h.get("nature", "").lower()
                or q_clean in h.get("strategic_stance", "").lower()
                or any(q_clean in str(tg).lower() for tg in h.get("diagnostic_tags", []))
                or str(h.get("number")) == q_clean
            ]
        return res

    def get_hexagram(self, ref: int | str) -> dict[str, Any] | None:
        """Find a hexagram by number (1..64), ID ('HEX-01'), or Vietnamese name, with hydrated relation summaries."""
        h: dict[str, Any] | None = None
        if isinstance(ref, int) or (isinstance(ref, str) and ref.isdigit()):
            h = self._by_number.get(int(ref))
        else:
            ref_str = str(ref).strip().lower()
            if not ref_str:
                return None
            if ref_str.startswith("hex-"):
                clean_num = ref_str.replace("hex-", "").lstrip("0")
                if clean_num.isdigit():
                    h = self._by_number.get(int(clean_num))

            if h is None and ref_str in self._by_name:
                h = self._by_name[ref_str]

            if h is None:
                for item in self._hexagrams:
                    if ref_str in item.get("name", "").lower():
                        h = item
                        break

        if h is None:
            return None

        # Return a copy enriched with relation summaries (Quẻ Hỗ, Thác, Tung)
        enriched = dict(h)
        n_num = h.get("nuclear_hex_number")
        if n_num and n_num in self._by_number:
            n_target = self._by_number[n_num]
            enriched["nuclear_hexagram"] = {
                "number": n_target["number"],
                "name": n_target["name"],
                "symbol": n_target.get("symbol", ""),
                "corporate_state": n_target.get("corporate_state", ""),
            }

        o_num = h.get("opposite_hex_number")
        if o_num and o_num in self._by_number:
            o_target = self._by_number[o_num]
            enriched["opposite_hexagram"] = {
                "number": o_target["number"],
                "name": o_target["name"],
                "symbol": o_target.get("symbol", ""),
                "corporate_state": o_target.get("corporate_state", ""),
            }

        i_num = h.get("inverted_hex_number")
        if i_num and i_num in self._by_number:
            i_target = self._by_number[i_num]
            enriched["inverted_hexagram"] = {
                "number": i_target["number"],
                "name": i_target["name"],
                "symbol": i_target.get("symbol", ""),
                "corporate_state": i_target.get("corporate_state", ""),
            }

        return enriched

    def get_matrix_8x8(self) -> dict[str, Any]:
        """
        Returns the 8x8 Matrix representation of the 64 Hexagrams.
        Rows = Upper Trigram (Ngoại Quái - Thiên thời/Môi trường bên ngoài)
        Cols = Lower Trigram (Nội Quái - Địa lợi/Nội lực tổ chức)
        """
        matrix: list[dict[str, Any]] = []
        for upper_name in TRIGRAM_ORDER:
            row_cells: list[dict[str, Any]] = []
            for lower_name in TRIGRAM_ORDER:
                # Find hexagram matching upper and lower trigrams
                match = None
                for h in self._hexagrams:
                    u = h.get("upper_trigram", {}).get("name")
                    l_trig = h.get("lower_trigram", {}).get("name")
                    if u == upper_name and l_trig == lower_name:
                        match = h
                        break
                if match:
                    row_cells.append({
                        "number": match["number"],
                        "name": match["name"],
                        "symbol": match.get("symbol", ""),
                        "palace": match.get("palace", ""),
                        "element": match.get("element", ""),
                        "stance": match.get("strategic_stance", "Biến"),
                        "corporate_state": match.get("corporate_state", ""),
                    })
                else:
                    row_cells.append({})
            matrix.append({
                "upper_trigram": upper_name,
                "cells": row_cells,
            })

        return {
            "trigrams_order": TRIGRAM_ORDER,
            "matrix": matrix,
        }

    def get_sovereign_hexagrams(self) -> list[dict[str, Any]]:
        """Returns the 12 Sovereign Hexagrams (Thập Nhị Tức Quái) in natural phase order (1..12)."""
        sovereigns = [
            h for h in self._hexagrams
            if h.get("twelve_sovereign", {}).get("is_sovereign")
        ]
        sovereigns.sort(
            key=lambda item: item.get("twelve_sovereign", {}).get("phase_order") or 99
        )
        return sovereigns

    def simulate_transition(
        self,
        ref: int | str,
        moving_lines: list[int] | None = None,
    ) -> dict[str, Any]:
        """
        Simulate a hexagram phase transition when one or more lines change (Hào Biến).
        moving_lines: list of line numbers (1..6) that are changing.
        """
        primary = self.get_hexagram(ref)
        if not primary:
            return {
                "status": "error",
                "message": f"Không tìm thấy quẻ gốc với định danh: {ref}",
            }

        valid_moving = [m for m in (moving_lines or []) if isinstance(m, int) and 1 <= m <= 6]
        valid_moving = sorted(set(valid_moving))

        pattern = list(primary.get("binary_pattern", "111111"))
        for line_no in valid_moving:
            idx = line_no - 1  # 0-indexed
            pattern[idx] = "0" if pattern[idx] == "1" else "1"

        new_pattern = "".join(pattern)
        transformed = self._by_pattern.get(new_pattern)
        if not transformed:
            transformed = primary

        # Formulate transition rationale
        script_parts = []
        if not valid_moving:
            script_parts.append("Không có hào biến: Giữ nguyên trạng thái vận hành hiện tại.")
        else:
            line_desc = ", ".join(f"Hào {m}" for m in valid_moving)
            script_parts.append(
                f"Tổ chức biến động tại {line_desc}. "
                f"Tình thế chuyển pha từ [{primary['name']}] sang [{transformed['name']}]."
            )
            script_parts.append(f"Môi trường mới: {transformed.get('corporate_state', '')}")
            script_parts.append(f"Trọng tâm can thiệp: {transformed.get('action_script', '')}")

        return {
            "status": "success",
            "primary_hexagram": {
                "number": primary["number"],
                "name": primary["name"],
                "symbol": primary.get("symbol", ""),
                "binary_pattern": primary.get("binary_pattern", ""),
                "corporate_state": primary.get("corporate_state", ""),
                "strategic_warning": primary.get("strategic_warning", ""),
            },
            "moving_lines": valid_moving,
            "transformed_hexagram": {
                "number": transformed["number"],
                "name": transformed["name"],
                "symbol": transformed.get("symbol", ""),
                "binary_pattern": transformed.get("binary_pattern", ""),
                "corporate_state": transformed.get("corporate_state", ""),
                "strategic_warning": transformed.get("strategic_warning", ""),
                "action_script": transformed.get("action_script", ""),
            },
            "transition_summary": " ".join(script_parts),
        }

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
