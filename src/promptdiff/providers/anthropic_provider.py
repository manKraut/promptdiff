from __future__ import annotations

import os
import time

import httpx

from promptdiff.models import ModelSettings, ProviderResult
from promptdiff.redact import redact


class AnthropicProvider:
    name = "anthropic"

    def complete(
        self, prompt: str, settings: ModelSettings, case_id: str, version: str
    ) -> ProviderResult:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return ProviderResult(text="", error="ANTHROPIC_API_KEY not set")
        url = "https://api.anthropic.com/v1/messages"
        started = time.perf_counter()
        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    url,
                    headers={
                        "x-api-key": key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": settings.name,
                        "temperature": settings.temperature,
                        "max_tokens": 1024,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                text = data["content"][0]["text"]
                usage = data.get("usage") or {}
                latency = int((time.perf_counter() - started) * 1000)
                return ProviderResult(
                    text=text,
                    tokens_in=int(usage.get("input_tokens", 0)),
                    tokens_out=int(usage.get("output_tokens", 0)),
                    latency_ms=latency,
                )
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(text="", error=redact(str(exc)))
