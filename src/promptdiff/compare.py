from __future__ import annotations

import json
import re
from difflib import ndiff

from promptdiff.models import Case, CaseDiff, Output

REFUSAL = re.compile(r"\b(I can'?t|I cannot|I'm sorry|unable to help)\b", re.I)


def parse_json_text(text: str) -> tuple[bool, dict | None]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return True, json.loads(cleaned)
    except json.JSONDecodeError:
        return False, None


def is_refusal(text: str) -> bool:
    return bool(REFUSAL.search(text))


def word_diff(a: str, b: str) -> list[str]:
    return list(ndiff(a.split(), b.split()))


def build_case_diff(case: Case, out_a: Output, out_b: Output) -> CaseDiff:
    ja, _ = parse_json_text(out_a.text) if out_a.text else (None, None)
    jb, obj_b = parse_json_text(out_b.text) if out_b.text else (None, None)

    missing: list[str] = []
    req = case.expect.get("required_fields") or []
    if req and obj_b is not None:
        for field in req:
            if field not in obj_b:
                missing.append(field)

    return CaseDiff(
        case_id=case.id,
        diff_lines=word_diff(out_a.text or "", out_b.text or ""),
        length_a=len(out_a.text or ""),
        length_b=len(out_b.text or ""),
        json_valid_a=ja,
        json_valid_b=jb,
        missing_fields_b=missing,
        refused_a=is_refusal(out_a.text or ""),
        refused_b=is_refusal(out_b.text or ""),
    )
