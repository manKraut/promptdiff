from __future__ import annotations

import sys
import time
from pathlib import Path

from promptdiff import report as report_mod
from promptdiff.compare import build_case_diff
from promptdiff.config import load_config
from promptdiff.cost import estimate_cost
from promptdiff.io_cases import load_cases
from promptdiff.judge import advisory_summary
from promptdiff.models import AppConfig, ModelSettings, Report, RuleConfig
from promptdiff.providers import get_provider
from promptdiff.redact import redact
from promptdiff.rules import evaluate_rules, overall_passed
from promptdiff.runner import run_all


def _default_rules() -> RuleConfig:
    return RuleConfig(
        max_length_increase_pct=30,
        json_valid="required",
        max_new_refusals=0,
        required_fields_missing=0,
    )


def _build_report(
    prompt_a: str,
    prompt_b: str,
    cases_path: str,
    settings: ModelSettings,
    rules: RuleConfig,
    use_cache: bool,
    max_cases: int | None,
    judge_enabled: bool,
    fmt: str,
) -> tuple[Report, int]:
    started = time.perf_counter()
    cases = load_cases(cases_path, max_cases)
    if not cases:
        print(redact("No cases loaded"), file=sys.stderr)
        return Report([], [], False, 0, 0, 0, 0, errors=["no cases"]), 2

    provider = get_provider(settings)
    outs_a, outs_b, errors = run_all(provider, settings, prompt_a, prompt_b, cases, use_cache, 5)

    by_a = {o.case_id: o for o in outs_a}
    by_b = {o.case_id: o for o in outs_b}
    diffs = [build_case_diff(c, by_a[c.id], by_b[c.id]) for c in cases]
    checks = evaluate_rules(cases, diffs, rules)
    passed = overall_passed(checks)

    mean_a = sum(d.length_a for d in diffs) / len(diffs)
    mean_b = sum(d.length_b for d in diffs) / len(diffs)
    cost = estimate_cost(outs_a + outs_b, settings, len(cases))

    adv = advisory_summary("", judge_enabled)
    report = Report(
        case_diffs=diffs,
        checks=checks,
        passed=passed,
        mean_length_a=mean_a,
        mean_length_b=mean_b,
        cost_estimate_usd=cost,
        duration_ms=int((time.perf_counter() - started) * 1000),
        errors=[redact(e) for e in errors],
        advisory_judge=adv,
    )

    text = report_mod.emit(report, fmt)
    if text:
        print(text)

    print(f"Estimated cost: ${cost:.4f}", file=sys.stderr)

    exit_code = 1 if not passed else 0
    if errors and len(errors) >= len(cases):
        exit_code = 3
    return report, exit_code


def run_comparison(
    prompt_a_path: str,
    prompt_b_path: str,
    inputs_path: str,
    output_format: str,
    use_cache: bool,
    max_cases: int | None,
    config: AppConfig | None,
) -> int:
    try:
        prompt_a = Path(prompt_a_path).read_text(encoding="utf-8")
        prompt_b = Path(prompt_b_path).read_text(encoding="utf-8")
    except OSError as exc:
        print(redact(str(exc)), file=sys.stderr)
        return 2

    if config:
        settings = config.model
        rules = config.rules
        judge = config.judge_enabled
    else:
        settings = ModelSettings(provider="recording", name="fixture", temperature=0.0)
        rules = _default_rules()
        judge = False

    _, code = _build_report(
        prompt_a,
        prompt_b,
        inputs_path,
        settings,
        rules,
        use_cache,
        max_cases,
        judge,
        output_format,
    )
    return code


def run_from_config(path: str) -> int:
    try:
        config = load_config(path)
    except ValueError as exc:
        print(redact(str(exc)), file=sys.stderr)
        return 2
    if not config.inputs:
        print("config missing inputs", file=sys.stderr)
        return 2
    # Minimal run: compare first two prompt files under prompts/
    prompts = Path(".").glob("prompts/*.txt")
    files = sorted(prompts)
    if len(files) < 2:
        print("Need two prompt files under prompts/ for run", file=sys.stderr)
        return 2
    return run_comparison(
        str(files[0]),
        str(files[1]),
        config.inputs,
        "terminal",
        True,
        None,
        config,
    )
