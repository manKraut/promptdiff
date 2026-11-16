from __future__ import annotations

import re
from typing import Any

_VAR = re.compile(r"\{\{(\w+)\}\}")


def render(template: str, variables: dict[str, Any]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in variables:
            raise KeyError(f"Missing template variable: {key}")
        return str(variables[key])

    return _VAR.sub(repl, template)
