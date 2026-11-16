from __future__ import annotations

import json
import os
from pathlib import Path

from promptdiff.models import ModelSettings, ProviderResult
from promptdiff.redact import redact


class RecordingProvider:
    name = "recording"

    def __init__(self, path: str | Path | None = None) -> None:
        env = os.environ.get("PROMPTDIFF_RECORDING_FILE")
        self.path = Path(path or env or "")
        self._data: dict[str, dict] = {}
        if self.path and self.path.is_file():
            self._data = json.loads(self.path.read_text(encoding="utf-8"))

    def complete(
        self, prompt: str, settings: ModelSettings, case_id: str, version: str
    ) -> ProviderResult:
        key = f"{case_id}:{version}"
        if key not in self._data:
            err = f"No recording for {key}"
            return ProviderResult(text="", error=redact(err))

        row = self._data[key]
        if row.get("error"):
            return ProviderResult(text="", error=redact(str(row["error"])))
        return ProviderResult(
            text=str(row.get("text", "")),
            tokens_in=int(row.get("tokens_in", 0)),
            tokens_out=int(row.get("tokens_out", 0)),
            latency_ms=int(row.get("latency_ms", 1)),
        )
