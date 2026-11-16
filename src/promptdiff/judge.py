"""Optional LLM judge (stub). Advisory only; never affects exit code."""


def advisory_summary(_report_text: str, enabled: bool) -> str | None:
    if not enabled:
        return None
    return "Judge disabled in v1 stub (advisory only)."
