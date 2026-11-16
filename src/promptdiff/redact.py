from __future__ import annotations

import os
import re


def redact(text: str) -> str:
    if not text:
        return text
    out = text
    for var in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GITHUB_TOKEN"):
        value = os.environ.get(var)
        if value and len(value) > 4 and value in out:
            out = out.replace(value, f"{value[:2]}***")
    out = re.sub(r"sk-[A-Za-z0-9]{8,}", "sk-***", out)
    return out
