from __future__ import annotations

from promptdiff.models import ModelSettings
from promptdiff.providers.anthropic_provider import AnthropicProvider
from promptdiff.providers.base import Provider
from promptdiff.providers.ollama_provider import OllamaProvider
from promptdiff.providers.openai_provider import OpenAIProvider
from promptdiff.providers.recording import RecordingProvider


def get_provider(settings: ModelSettings) -> Provider:
    mapping: dict[str, Provider] = {
        "recording": RecordingProvider(),
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
        "ollama": OllamaProvider(),
    }
    provider = mapping.get(settings.provider)
    if not provider:
        raise ValueError(f"Unknown provider: {settings.provider}")
    return provider
