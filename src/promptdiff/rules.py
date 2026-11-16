from __future__ import annotations

from promptdiff.models import Case, CaseDiff, CheckResult, RuleConfig


def evaluate_rules(
    cases: list[Case], diffs: list[CaseDiff], rules: RuleConfig
) -> list[CheckResult]:
    results: list[CheckResult] = []
    diff_by_id = {d.case_id: d for d in diffs}

    if rules.max_length_increase_pct is not None:
        mean_a = sum(d.length_a for d in diffs) / max(len(diffs), 1)
        mean_b = sum(d.length_b for d in diffs) / max(len(diffs), 1)
        limit = mean_a * (1 + rules.max_length_increase_pct / 100)
        ok = mean_b <= limit if mean_a > 0 else True
        results.append(
            CheckResult(
                rule="max_length_increase_pct",
                passed=ok,
                detail=f"avg len a={mean_a:.1f} b={mean_b:.1f} (limit {limit:.1f})",
            )
        )

    if rules.json_valid == "required":
        failing = [
            d.case_id
            for c in cases
            if (c.expect.get("format") == "json" and (d := diff_by_id[c.id]).json_valid_b is False)
        ]
        results.append(
            CheckResult(
                rule="json_valid",
                passed=len(failing) == 0,
                detail=f"invalid json in v2: {', '.join(failing) or 'none'}",
                case_ids=failing,
            )
        )

    if rules.max_new_refusals is not None:
        new_ref = [d.case_id for d in diffs if d.refused_b and not d.refused_a]
        ok = len(new_ref) <= rules.max_new_refusals
        results.append(
            CheckResult(
                rule="max_new_refusals",
                passed=ok,
                detail=f"new refusals: {', '.join(new_ref) or 'none'}",
                case_ids=new_ref,
            )
        )

    if rules.required_fields_missing is not None:
        missing_cases = [d.case_id for d in diffs if d.missing_fields_b]
        allowed = rules.required_fields_missing
        ok = len(missing_cases) <= allowed
        results.append(
            CheckResult(
                rule="required_fields_missing",
                passed=ok,
                detail=f"missing fields in: {', '.join(missing_cases) or 'none'}",
                case_ids=missing_cases,
            )
        )

    return results


def overall_passed(checks: list[CheckResult]) -> bool:
    return all(c.passed for c in checks)
