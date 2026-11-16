from __future__ import annotations

import json
from pathlib import Path

from promptdiff.models import Case


def load_cases(path: str | Path, max_cases: int | None = None) -> list[Case]:
    cases: list[Case] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        cases.append(
            Case(
                id=str(obj["id"]),
                input=dict(obj.get("input") or {}),
                expect=dict(obj.get("expect") or {}),
            )
        )
        if max_cases and len(cases) >= max_cases:
            break
    return cases
