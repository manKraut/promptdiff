from __future__ import annotations

from typing import Protocol

from promptdiff.models import ModelSettings, ProviderResult


class Provider(Protocol):
    name: str

    def complete(
        self, prompt: str, settings: ModelSettings, case_id: str, version: str
    ) -> ProviderResult: ...
