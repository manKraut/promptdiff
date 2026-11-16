from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from promptdiff.models import AppConfig, ModelSettings, RuleConfig

KNOWN_RULES = frozenset(
    {
        "max_length_increase_pct",
        "json_valid",
        "max_new_refusals",
        "required_fields_missing",
    }
)


def load_config(path: str | Path) -> AppConfig:
    data: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not data:
        raise ValueError("Empty config")

    rules_raw = data.get("rules") or {}
    for key in rules_raw:
        if key not in KNOWN_RULES:
            raise ValueError(f"Unknown rule name: {key}")

    model_raw = data.get("model") or {}
    model = ModelSettings(
        provider=str(model_raw.get("provider", "recording")),
        name=str(model_raw.get("name", "fixture")),
        temperature=float(model_raw.get("temperature", 0)),
        base_url=model_raw.get("base_url"),
    )

    judge = data.get("judge") or {}
    rules = RuleConfig(
        max_length_increase_pct=rules_raw.get("max_length_increase_pct"),
        json_valid=rules_raw.get("json_valid"),
        max_new_refusals=rules_raw.get("max_new_refusals"),
        required_fields_missing=rules_raw.get("required_fields_missing"),
    )

    return AppConfig(
        inputs=str(data.get("inputs", "")),
        model=model,
        rules=rules,
        judge_enabled=bool(judge.get("enabled", False)),
        prompts_glob=list(data.get("prompts") or []),
        concurrency=int(data.get("concurrency", 5)),
    )
