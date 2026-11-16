from __future__ import annotations

import time

import httpx

from promptdiff.models import ModelSettings, ProviderResult
from promptdiff.redact import redact


class OllamaProvider:
    name = "ollama"

    def complete(
        self, prompt: str, settings: ModelSettings, case_id: str, version: str
    ) -> ProviderResult:
        base = settings.base_url or "http://127.0.0.1:11434"
        url = f"{base.rstrip('/')}/api/generate"
        started = time.perf_counter()
        try:
            with httpx.Client(timeout=120) as client:
                resp = client.post(
                    url,
                    json={
                        "model": settings.name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": settings.temperature},
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                text = data.get("response", "")
                latency = int((time.perf_counter() - started) * 1000)
                return ProviderResult(text=text, latency_ms=latency)
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(text="", error=redact(str(exc)))
