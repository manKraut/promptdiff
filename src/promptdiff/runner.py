from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from promptdiff import cache as cache_mod
from promptdiff.models import Case, ModelSettings, Output, ProviderResult
from promptdiff.providers.base import Provider
from promptdiff.template import render


def run_case(
    provider: Provider,
    settings: ModelSettings,
    prompt_template: str,
    case: Case,
    version: str,
    use_cache: bool,
) -> Output:
    rendered = render(prompt_template, case.input)
    key = cache_mod.cache_key(rendered, case.input, settings, version)
    result: ProviderResult | None = None

    if use_cache:
        result = cache_mod.load_cache(key)

    if result is None:
        for attempt in range(3):
            result = provider.complete(rendered, settings, case.id, version)
            if not result.error or attempt == 2:
                break
            time.sleep(0.2 * (attempt + 1))
        if use_cache and result and not result.error:
            cache_mod.save_cache(key, result)

    return Output(
        case_id=case.id,
        version=version,  # type: ignore[arg-type]
        text=result.text if result else "",
        tokens_in=result.tokens_in if result else 0,
        tokens_out=result.tokens_out if result else 0,
        latency_ms=result.latency_ms if result else 0,
        error=result.error if result else "no result",
        from_cache=bool(result and result.from_cache),
    )


def run_all(
    provider: Provider,
    settings: ModelSettings,
    prompt_a: str,
    prompt_b: str,
    cases: list[Case],
    use_cache: bool,
    concurrency: int,
) -> tuple[list[Output], list[Output], list[str]]:
    outs_a: list[Output] = []
    outs_b: list[Output] = []
    errors: list[str] = []

    tasks = []
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        for case in cases:
            tasks.append(pool.submit(run_case, provider, settings, prompt_a, case, "a", use_cache))
            tasks.append(pool.submit(run_case, provider, settings, prompt_b, case, "b", use_cache))
        for fut in as_completed(tasks):
            out = fut.result()
            if out.version == "a":
                outs_a.append(out)
            else:
                outs_b.append(out)
            if out.error:
                errors.append(f"{out.case_id}:{out.version}: {out.error}")

    outs_a.sort(key=lambda o: o.case_id)
    outs_b.sort(key=lambda o: o.case_id)
    return outs_a, outs_b, errors
