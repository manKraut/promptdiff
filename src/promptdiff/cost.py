from __future__ import annotations

from promptdiff.models import ModelSettings, Output

# Rough USD per 1M tokens for smoke estimates (gpt-4o-mini class)
RATE_IN = 0.15
RATE_OUT = 0.60


def estimate_cost(outputs: list[Output], settings: ModelSettings, case_count: int) -> float:
    if settings.provider == "recording":
        return 0.0
    tin = sum(o.tokens_in for o in outputs)
    tout = sum(o.tokens_out for o in outputs)
    if tin == 0 and tout == 0:
        # heuristic for untokenized responses
        chars = sum(len(o.text) for o in outputs)
        tout = chars // 4
        tin = case_count * 200
    return (tin / 1_000_000) * RATE_IN + (tout / 1_000_000) * RATE_OUT
