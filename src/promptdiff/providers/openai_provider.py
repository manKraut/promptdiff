from __future__ import annotations

import os
import time

import httpx

from promptdiff.models import ModelSettings, ProviderResult
from promptdiff.redact import redact


class OpenAIProvider:
    name = "openai"

    def complete(
        self, prompt: str, settings: ModelSettings, case_id: str, version: str
    ) -> ProviderResult:
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            return ProviderResult(text="", error="OPENAI_API_KEY not set")
        url = "https://api.openai.com/v1/chat/completions"
        started = time.perf_counter()
        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    url,
                    headers={"Authorization": f"Bearer {key}"},
                    json={
                        "model": settings.name,
                        "temperature": settings.temperature,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                usage = data.get("usage") or {}
                latency = int((time.perf_counter() - started) * 1000)
                return ProviderResult(
                    text=text,
                    tokens_in=int(usage.get("prompt_tokens", 0)),
                    tokens_out=int(usage.get("completion_tokens", 0)),
                    latency_ms=latency,
                )
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(text="", error=redact(str(exc)))
