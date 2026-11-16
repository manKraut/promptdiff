from promptdiff.compare import build_case_diff
from promptdiff.models import Case, Output, RuleConfig
from promptdiff.rules import evaluate_rules, overall_passed


def test_length_rule_fails() -> None:
    case = Case(id="c1", input={}, expect={})
    a = Output("c1", "a", "short")
    b = Output("c1", "b", "much longer output text here")
    diff = build_case_diff(case, a, b)
    rules = RuleConfig(max_length_increase_pct=10)
    checks = evaluate_rules([case], [diff], rules)
    assert not overall_passed(checks)
