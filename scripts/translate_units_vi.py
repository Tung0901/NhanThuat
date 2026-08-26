"""Translate knowledge-unit YAML content from English to Vietnamese (batch, LLM-assisted).

Preserves all non-text fields (id, type, status, version, primary_domain,
secondary_domains, domain_area, evidence, relations, tags, created_at) and
updates ``updated_at``. Also enriches ``tags`` with English search keywords
derived from the original content so bilingual resolver queries still match.

Usage:
    python scripts/translate_units_vi.py [--only NT-LAW-0002] [--batch 3] [--dry-run]

The API key is read from ``.env`` (GEMINI_API_KEY) or the environment.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nhan_thuat.runtime.synthesizer import DEFAULT_BASE_URL, DEFAULT_MODEL  # noqa: E402

VN_DIACRITICS = set("ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")

TRANSLATABLE_FIELDS = ("title", "summary", "definition", "mechanism", "conditions", "exceptions", "risks")
PRESERVED_FIELDS = (
    "id", "type", "status", "version", "primary_domain", "secondary_domains",
    "domain_area", "evidence", "relations", "created_at",
)
TAG_CAP = 8


def _load_env() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _api_key() -> str:
    return (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("DEEPSEEK_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or ""
    ).strip()


def is_vietnamese(text: str) -> bool:
    return bool(text) and any(c.lower() in VN_DIACRITICS for c in text)


def is_translated(data: dict[str, Any]) -> bool:
    return is_vietnamese(str(data.get("title", "")))


def _parse_json(text: str) -> Any:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def call_gemini(prompt: str, timeout: int = 180) -> str:
    delay = 5.0
    for attempt in range(6):
        response = requests.post(
            f"{DEFAULT_BASE_URL.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {_api_key()}"},
            json={
                "model": DEFAULT_MODEL,
                "messages": [
                    {"role": "system", "content": "Bạn là một biên tập viên và dịch giả chuyên nghiệp."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            },
            timeout=timeout,
        )
        if response.status_code == 429:
            print(f"    rate-limited on {DEFAULT_MODEL}; sleeping {int(delay)}s...")
            time.sleep(delay)
            delay *= 2
            continue
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]
    raise RuntimeError("rate limited after 6 backoff attempts")


MODEL_ROTATION = [
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-flash-lite-latest",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-3.6-flash",
]


def call_gemini_rotating(prompt: str, timeout: int = 180) -> str:
    """Call the API rotating across models to spread the free-tier daily quota."""
    last_error: Exception | None = None
    for model in MODEL_ROTATION:
        delay = 4.0
        for attempt in range(4):
            try:
                response = requests.post(
                    f"{DEFAULT_BASE_URL.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {_api_key()}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "Bạn là một biên tập viên và dịch giả chuyên nghiệp."},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.2,
                    },
                    timeout=timeout,
                )
                if response.status_code == 429:
                    print(f"    model {model} rate-limited; trying next after {int(delay)}s")
                    time.sleep(delay)
                    delay *= 2
                    continue
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except requests.exceptions.HTTPError as exc:
                last_error = exc
                if exc.response is not None and exc.response.status_code == 429:
                    continue
                raise
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                break
    raise RuntimeError(f"all models rate-limited: {last_error}")


def build_prompt(units: list[dict[str, Any]]) -> str:
    payload = [
        {
            "id": unit.get("id"),
            "title": unit.get("title"),
            "summary": unit.get("summary"),
            "definition": unit.get("definition"),
            "mechanism": unit.get("mechanism", []),
            "conditions": unit.get("conditions", []),
            "exceptions": unit.get("exceptions", []),
            "applications": unit.get("applications", {}),
            "risks": unit.get("risks", []),
        }
        for unit in units
    ]
    return (
        "Dịch chính xác và tự nhiên sang tiếng Việt nội dung các đơn vị tri thức tổ chức/hành vi sau đây.\n"
        "Quy tắc:\n"
        "- Giữ nguyên ID của mỗi đơn vị.\n"
        "- title, summary, definition, mỗi phần tử của mechanism/conditions/exceptions/risks: dịch sang tiếng Việt chuẩn, chuyên nghiệp.\n"
        "- applications: giữ nguyên khóa section (management, negotiation, leadership, review, environment...), chỉ dịch các chuỗi bên trong.\n"
        "- Giữ nguyên số lượng phần tử trong mỗi mảng (không thêm, không bớt).\n"
        "- Ràng buộc độ dài: title >= 3 ký tự, summary >= 20 ký tự, definition >= 20 ký tự, mỗi phần tử mảng >= 3 ký tự.\n"
        "- Ngoài ra, thêm trường \"search_keywords\": mảng 3-6 từ khóa TIẾNG ANH (chữ thường, kebab-case, mỗi từ hợp lệ a-z0-9 và dấu gạch ngang) mô tả bản chất đơn vị, để tìm kiếm tiếng Anh vẫn hoạt động.\n"
        "- Trả lời CHỈ bằng một mảng JSON, mỗi phần tử ứng với một đơn vị theo thứ tự, với các khóa:\n"
        "  id, title, summary, definition, mechanism, conditions, exceptions, applications, risks, search_keywords.\n"
        "Dữ liệu đầu vào:\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )


def merge_translation(original: dict[str, Any], translated: dict[str, Any]) -> dict[str, Any]:
    merged = dict(original)
    for field in TRANSLATABLE_FIELDS:
        if field in translated:
            merged[field] = translated[field]
    applications = translated.get("applications")
    if isinstance(applications, dict) and isinstance(original.get("applications"), dict):
        merged["applications"] = applications
    enriched = [str(tag) for tag in original.get("tags", [])]
    for keyword in translated.get("search_keywords", []):
        cleaned = re.sub(r"[^a-z0-9-]", "-", str(keyword).strip().lower())
        cleaned = re.sub(r"-+", "-", cleaned).strip("-")
        if cleaned and cleaned not in enriched and len(enriched) < TAG_CAP:
            enriched.append(cleaned)
    merged["tags"] = enriched
    merged["updated_at"] = time.strftime("%Y-%m-%d")
    return merged


def write_unit(path: Path, data: dict[str, Any]) -> None:
    text = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    )
    path.write_text(text, encoding="utf-8")


def find_unit_files() -> list[Path]:
    base = REPO_ROOT / "knowledge" / "units"
    return sorted(path for path in base.rglob("*.yaml"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="", help="only translate this unit id")
    parser.add_argument("--batch", type=int, default=3, help="units per API call")
    parser.add_argument("--dry-run", action="store_true", help="show plan without writing")
    args = parser.parse_args()

    _load_env()
    if not _api_key():
        print("ERROR: missing DEEPSEEK_API_KEY, GEMINI_API_KEY or GOOGLE_API_KEY (in .env or environment)")
        return 1

    files = find_unit_files()
    todo: list[tuple[Path, dict[str, Any]]] = []
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not data.get("id"):
            print(f"SKIP (invalid): {path}")
            continue
        if args.only and data["id"] != args.only:
            continue
        if not is_translated(data):
            todo.append((path, data))

    if not todo:
        print("Nothing to translate (all units already Vietnamese).")
        return 0
    print(f"To translate: {len(todo)} unit(s) in {len(files)} file(s).")
    if args.dry_run:
        for path, data in todo[:10]:
            print(f"  - {path.name}: {data['id']} | {data['title']}")
        return 0

    done = failed = 0
    for start in range(0, len(todo), args.batch):
        batch = todo[start : start + args.batch]
        prompt = build_prompt([data for _, data in batch])
        translated_batch: list[dict[str, Any]] | None = None
        for attempt in range(3):
            try:
                text = call_gemini_rotating(prompt)
                parsed = _parse_json(text)
                if isinstance(parsed, dict):
                    parsed = [parsed]
                if not isinstance(parsed, list) or len(parsed) != len(batch):
                    raise ValueError(f"expected {len(batch)} items, got {type(parsed).__name__}")
                translated_batch = parsed
                break
            except Exception as exc:  # noqa: BLE001
                print(f"  batch@{start} attempt {attempt + 1} failed: {exc}")
                time.sleep(4)
        if translated_batch is None:
            failed += len(batch)
            print(f"  batch@{start}: FAILED after retries")
            continue
        for (path, original), translated in zip(batch, translated_batch):
            merged = merge_translation(original, translated)
            write_unit(path, merged)
            done += 1
            print(f"  OK {merged['id']} | {merged['title']}")
        time.sleep(1.5)

    print(f"\nDone: {done} translated, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())