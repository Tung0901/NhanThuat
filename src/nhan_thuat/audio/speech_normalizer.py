"""
Speech Normalizer for Executive Audio Briefing.

Normalizes markdown, cleans punctuation and symbols, expands technical abbreviations,
and segments text into natural conversational chunks suitable for browser Web Speech
synthesis or server-side Neural TTS.
"""

from __future__ import annotations

import re
from typing import Any

# Map technical abbreviations to natural Vietnamese spoken representations
ABBREVIATIONS: dict[str, str] = {
    "KPI": "chỉ số hiệu suất",
    "KPIs": "các chỉ số hiệu suất",
    "OKR": "mục tiêu then chốt",
    "OKRs": "các mục tiêu then chốt",
    "DISC": "mô hình D I S C",
    "CEO": "Giám đốc điều hành",
    "COO": "Giám đốc vận hành",
    "CFO": "Giám đốc tài chính",
    "HR": "nhân sự",
    "PO": "chủ sản phẩm",
    "Plan B": "Phương án dự phòng B",
    "Plan A": "Phương án A",
    "Plan C": "Phương án C",
    "RCA": "phân tích nguyên nhân gốc rễ",
    "AC": "tiêu chí nghiệm thu",
    "Verbatim": "Lời thoại mẫu từng câu chữ",
}


def clean_markdown_for_speech(text: str) -> str:
    """
    Strips markdown formatting, bullet symbols, table markers, and extraneous tags,
    producing fluent, natural-sounding plain text for speech synthesis.
    """
    if not text or not isinstance(text, str):
        return ""

    cleaned = text

    # 1. Remove code blocks ```...```
    cleaned = re.sub(r"```[\s\S]*?```", "", cleaned)

    # 2. Remove inline code `...`
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)

    # 3. Replace markdown links [text](url) -> text
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)

    # 4. Remove image tags ![alt](url)
    cleaned = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", cleaned)

    # 5. Remove headers: #, ##, ###, ####, etc.
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)

    # 6. Remove bold/italic: **text**, *text*, __text__, _text_
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"__([^_]+)__", r"\1", cleaned)
    cleaned = re.sub(r"_([^_]+)_", r"\1", cleaned)

    # 7. Remove blockquotes >
    cleaned = re.sub(r"^>\s*", "", cleaned, flags=re.MULTILINE)

    # 8. Remove horizontal dividers ---, ***, ===
    cleaned = re.sub(r"^[-\*=_]{3,}\s*$", "", cleaned, flags=re.MULTILINE)

    # 9. Handle list bullets (- , * , + , 1. ) -> replace with natural pause
    cleaned = re.sub(r"^[\*\-\+]\s+", "  ", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\d+\.\s+", "  ", cleaned, flags=re.MULTILINE)

    # 10. Handle table dividers |---|---|
    cleaned = re.sub(r"\|[-:\s|]+\|", "", cleaned)
    cleaned = re.sub(r"\|", " , ", cleaned)

    # 11. Mathematical and probability expressions
    cleaned = re.sub(r"P\s*>\s*0?\.(\d+)", r"xác suất trên \1 phần trăm", cleaned)
    cleaned = re.sub(r"P\s*<\s*0?\.(\d+)", r"xác suất dưới \1 phần trăm", cleaned)
    cleaned = re.sub(r"(\d+)%", r"\1 phần trăm", cleaned)

    # 12. Expand technical abbreviations
    for abbr, full_spoken in ABBREVIATIONS.items():
        pattern = rf"\b{re.escape(abbr)}\b"
        cleaned = re.sub(pattern, full_spoken, cleaned)

    # 13. Remove remaining emojis / icons that break TTS prosody
    # Keep Vietnamese letters, numbers, common punctuation, quotes
    cleaned = re.sub(
        r"[^\w\s\.,;:!?'\"\(\)\-–—àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )

    # 14. Collapse consecutive spaces and blank lines
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)

    return cleaned.strip()


def split_into_utterance_chunks(text: str, max_chunk_words: int = 40) -> list[str]:
    """
    Splits text into chunks of comfortable speaking length (typically 20-45 words).
    Speech synthesis engines (especially in Web Speech API) freeze or cancel if an utterance
    is too long. Sentence-based chunking preserves natural breath marks.
    """
    clean_text = clean_markdown_for_speech(text)
    if not clean_text:
        return []

    # Split by primary sentence boundaries: . ! ? or double newline
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n\n+", clean_text)
    chunks: list[str] = []

    for sentence in raw_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        words = sentence.split()
        if len(words) <= max_chunk_words:
            chunks.append(sentence)
        else:
            # Sub-split by comma, semicolon, or colon if a single sentence is very long
            sub_parts = re.split(r"(?<=[,;:])\s+", sentence)
            current_sub: list[str] = []
            current_count = 0

            for part in sub_parts:
                part = part.strip()
                if not part:
                    continue
                part_words = part.split()
                if current_count + len(part_words) > max_chunk_words and current_sub:
                    chunks.append(" ".join(current_sub))
                    current_sub = [part]
                    current_count = len(part_words)
                else:
                    current_sub.append(part)
                    current_count += len(part_words)

            if current_sub:
                chunks.append(" ".join(current_sub))

    return chunks


def extract_speech_modes(advisory_payload: dict[str, Any]) -> dict[str, str]:
    """
    Extracts specialized speech scripts based on the user's intent:
    - 'full': Comprehensive briefing covering analysis, lens, verbatim, and operational directives.
    - 'verbatim_only': Focused dialogue quotes (Step 1, 2, 3) for immediate executive rehearsal.
    - 'executive_summary': Fast 1-minute situational overview.
    """
    if not isinstance(advisory_payload, dict) or not advisory_payload:
        return {"full": "", "verbatim_only": "", "executive_summary": ""}

    if not any(bool(v) for v in advisory_payload.values()):
        return {"full": "", "verbatim_only": "", "executive_summary": ""}

    pos_analysis = str(advisory_payload.get("position_analysis") or "")
    step_1 = advisory_payload.get("step_1_anchor") or {}
    step_2 = advisory_payload.get("step_2_deadline_consequence") or {}
    step_3 = advisory_payload.get("step_3_way_out_plan_b") or {}

    v1 = step_1.get("verbatim", "") if isinstance(step_1, dict) else ""
    t1 = step_1.get("title", "Bước 1") if isinstance(step_1, dict) else "Bước 1"

    v2 = step_2.get("verbatim", "") if isinstance(step_2, dict) else ""
    t2 = step_2.get("title", "Bước 2") if isinstance(step_2, dict) else "Bước 2"

    v3 = step_3.get("verbatim", "") if isinstance(step_3, dict) else ""
    t3 = step_3.get("title", "Bước 3") if isinstance(step_3, dict) else "Bước 3"

    directives = advisory_payload.get("financial_and_operational_directives") or []
    directives_text = "\n".join(directives) if isinstance(directives, list) else str(directives)

    # 1. Verbatim Only (Lời thoại đối đáp thực chiến)
    verbatim_lines: list[str] = [
        "Sau đây là Kịch bản Lời thoại Mẫu ba bước trong tình huống này.",
        f"{t1}: {v1}",
        f"{t2}: {v2}",
        f"{t3}: {v3}",
    ]
    verbatim_only = clean_markdown_for_speech("\n\n".join(verbatim_lines))

    # 2. Executive Summary (Tóm tắt 1 phút)
    exec_summary_lines: list[str] = [
        "Bản tóm tắt tình thế điều hành:",
        pos_analysis,
        "Định hướng then chốt:",
        v1,
    ]
    executive_summary = clean_markdown_for_speech("\n\n".join(exec_summary_lines))

    # 3. Full Briefing (Toàn bộ tham mưu)
    full_lines: list[str] = [
        "Báo cáo tham mưu điều hành Nhân Thuật.",
        "Phần một: Đánh giá vị thế và thế trận.",
        pos_analysis,
        "Phần hai: Kịch bản lời thoại ba bước.",
        f"{t1}. {v1}",
        f"{t2}. {v2}",
        f"{t3}. {v3}",
        "Phần ba: Chỉ đạo tác chiến vận hành.",
        directives_text,
    ]
    full = clean_markdown_for_speech("\n\n".join(full_lines))

    return {
        "full": full,
        "verbatim_only": verbatim_only,
        "executive_summary": executive_summary,
    }
