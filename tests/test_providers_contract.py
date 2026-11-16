import json
from pathlib import Path

from promptdiff.models import ModelSettings
from promptdiff.providers.anthropic_provider import AnthropicProvider
from promptdiff.providers.ollama_provider import OllamaProvider
from promptdiff.providers.openai_provider import OpenAIProvider
from promptdiff.providers.recording import RecordingProvider


def test_recording_provider(tmp_path: Path) -> None:
    data = {"c1:a": {"text": "hello"}}
    path = tmp_path / "rec.json"
    path.write_text(json.dumps(data))
    p = RecordingProvider(path)
    res = p.complete("p", ModelSettings("recording", "x"), "c1", "a")
    assert res.text == "hello"


def test_live_adapters_return_error_without_keys() -> None:
    for cls in (OpenAIProvider, AnthropicProvider):
        res = cls().complete("p", ModelSettings(cls.name, "m"), "c", "a")
        assert res.error
    res = OllamaProvider().complete("p", ModelSettings("ollama", "m"), "c", "a")
    assert res.error
