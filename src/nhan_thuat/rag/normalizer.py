"""
Vietnamese text normalization and tokenization utilities for RAG Engine.
Handles diacritics removal, tokenization, stop-words, and field extraction.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any


VIETNAMESE_ACCENTS_MAP = {
    "à": "a", "á": "a", "ả": "a", "ã": "a", "ạ": "a",
    "ă": "a", "ằ": "a", "ắ": "a", "ẳ": "a", "ẵ": "a", "ặ": "a",
    "â": "a", "ầ": "a", "ấ": "a", "ẩ": "a", "ẫ": "a", "ậ": "a",
    "è": "e", "é": "e", "ẻ": "e", "ẽ": "e", "ẹ": "e",
    "ê": "e", "ề": "e", "ế": "e", "ể": "e", "ễ": "e", "ệ": "e",
    "ì": "i", "í": "i", "ỉ": "i", "ĩ": "i", "ị": "i",
    "ò": "o", "ó": "o", "ỏ": "o", "õ": "o", "ọ": "o",
    "ô": "o", "ồ": "o", "ố": "o", "ổ": "o", "ỗ": "o", "ộ": "o",
    "ơ": "o", "ờ": "o", "ớ": "o", "ở": "o", "ỡ": "o", "ợ": "o",
    "ù": "u", "ú": "u", "ủ": "u", "ũ": "u", "ụ": "u",
    "ư": "u", "ừ": "u", "ứ": "u", "ử": "u", "ữ": "u", "ự": "u",
    "ỳ": "y", "ý": "y", "ỷ": "y", "ỹ": "y", "ỵ": "y",
    "đ": "d",
    "À": "a", "Á": "a", "Ả": "a", "Ã": "a", "Ạ": "a",
    "Ă": "a", "Ằ": "a", "Ắ": "a", "Ẳ": "a", "Ẵ": "a", "Ặ": "a",
    "Â": "a", "Ầ": "a", "Ấ": "a", "Ẩ": "a", "Ẫ": "a", "Ậ": "a",
    "È": "e", "É": "e", "Ẻ": "e", "Ẽ": "e", "Ẹ": "e",
    "Ê": "e", "Ề": "e", "Ế": "e", "Ể": "e", "Ễ": "e", "Ệ": "e",
    "Ì": "i", "Í": "i", "Ỉ": "i", "Ĩ": "i", "Ị": "i",
    "Ò": "o", "Ó": "o", "Ỏ": "o", "Õ": "o", "Ọ": "o",
    "Ô": "o", "Ồ": "o", "Ố": "o", "Ổ": "o", "Ỗ": "o", "Ộ": "o",
    "Ơ": "o", "Ờ": "o", "Ớ": "o", "Ở": "o", "Ỡ": "o", "Ợ": "o",
    "Ù": "u", "Ú": "u", "Ủ": "u", "Ũ": "u", "Ụ": "u",
    "Ư": "u", "Ừ": "u", "Ứ": "u", "Ử": "u", "Ữ": "u", "Ự": "u",
    "Ỳ": "y", "Ý": "y", "Ỷ": "y", "Ỹ": "y", "Ỵ": "y",
    "Đ": "d",
}

VI_STOP_WORDS = {
    "va", "la", "cua", "cho", "trong", "khi", "nhung", "cac", "mot", "nhieu",
    "den", "o", "tai", "ra", "vao", "voi", "neu", "thi", "do", "bi", "duoc",
    "va", "ma", "hay", "hoac", "co", "khong", "se", "da", "dang", "nhu",
}


def strip_accents(text: str) -> str:
    """Remove Vietnamese diacritics / accents from text."""
    res = []
    for ch in text:
        res.append(VIETNAMESE_ACCENTS_MAP.get(ch, ch))
    normalized = "".join(res)
    # Also apply NFKD normalization fallback
    return unicodedata.normalize("NFKD", normalized).encode("ASCII", "ignore").decode("utf-8")


def tokenize(text: str, include_unaccented: bool = True, min_len: int = 2) -> list[str]:
    """
    Tokenize text into lowercase words, optionally including unaccented duplicates.
    Preserves alphanumeric terms, hyphens, and Vietnamese words.
    """
    if not text:
        return []
    
    text_clean = re.sub(r"[^\w\s\-]", " ", text.lower(), flags=re.UNICODE)
    raw_tokens = [t.strip() for t in text_clean.split() if len(t.strip()) >= min_len]
    
    tokens = []
    for t in raw_tokens:
        tokens.append(t)
        if include_unaccented:
            unacc = strip_accents(t)
            if unacc != t and len(unacc) >= min_len:
                tokens.append(unacc)
                
    return tokens


def extract_unit_text_corpus(unit_data: dict[str, Any]) -> str:
    """Extract weighted corpus string from a Knowledge Unit payload."""
    parts = []
    
    # High Priority Fields
    title = str(unit_data.get("title", ""))
    unit_id = str(unit_data.get("id", unit_data.get("unit_id", "")))
    tags = " ".join(str(t) for t in unit_data.get("tags", []))
    domain = str(unit_data.get("primary_domain", unit_data.get("domain", "")))
    
    parts.extend([unit_id, title, title, tags, domain])
    
    # Core Content
    summary = str(unit_data.get("summary", ""))
    definition = str(unit_data.get("definition", ""))
    parts.extend([summary, definition])
    
    # Mechanism & Rules
    mechanisms = " ".join(str(m) for m in unit_data.get("mechanism", unit_data.get("key_mechanisms", [])))
    rules = " ".join(str(r) for r in unit_data.get("operational_rules", unit_data.get("rules", [])))
    conditions = " ".join(str(c) for c in unit_data.get("conditions", []))
    exceptions = " ".join(str(e) for e in unit_data.get("exceptions", []))
    risks = " ".join(str(rk) for rk in unit_data.get("risks", []))
    
    parts.extend([mechanisms, rules, conditions, exceptions, risks])
    
    return " ".join(parts)
