from __future__ import annotations

import hashlib
import json
from pathlib import Path

from promptdiff.models import ModelSettings, ProviderResult

CACHE_DIR = Path(".promptdiff/cache")


def cache_key(prompt: str, case_input: dict, settings: ModelSettings) -> str:
    payload = json.dumps(
        {
            "prompt": prompt,
            "input": case_input,
            "settings": {
                "provider": settings.provider,
                "name": settings.name,
                "temperature": settings.temperature,
                "base_url": settings.base_url,
            },
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def load_cache(key: str) -> ProviderResult | None:
    path = CACHE_DIR / f"{key}.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return ProviderResult(
        text=data["text"],
        tokens_in=data.get("tokens_in", 0),
        tokens_out=data.get("tokens_out", 0),
        latency_ms=data.get("latency_ms", 0),
        error=data.get("error"),
        from_cache=True,
    )


def save_cache(key: str, result: ProviderResult) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{key}.json"
    path.write_text(
        json.dumps(
            {
                "text": result.text,
                "tokens_in": result.tokens_in,
                "tokens_out": result.tokens_out,
                "latency_ms": result.latency_ms,
                "error": result.error,
            }
        ),
        encoding="utf-8",
    )
