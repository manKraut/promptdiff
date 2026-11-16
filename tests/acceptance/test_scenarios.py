from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest import mock

import pytest

from promptdiff.config import load_config
from promptdiff.engine import run_comparison
from promptdiff.github import action_entry
from promptdiff.github import comment as gh_comment
from promptdiff.models import ModelSettings
from promptdiff.providers.openai_provider import OpenAIProvider
from promptdiff.redact import redact
from promptdiff.report import render_json, render_md, truncate_md

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures"


def run_cli(
    a: Path, b: Path, inputs: Path, recording: Path, *extra: str
) -> subprocess.CompletedProcess:
    env = {**os.environ, "PROMPTDIFF_RECORDING_FILE": str(recording)}
    cmd = [
        sys.executable,
        "-m",
        "promptdiff",
        str(a),
        str(b),
        "--inputs",
        str(inputs),
        "--format",
        "json",
        "--no-cache",
    ] + list(extra)
    return subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=ROOT)


def test_scenario1_identical_prompts_pass() -> None:
    res = run_cli(
        FIXTURES / "prompts/identical.txt",
        FIXTURES / "prompts/identical.txt",
        FIXTURES / "inputs/five.jsonl",
        FIXTURES / "recordings/scenario1.json",
    )
    assert res.returncode == 0
    body = json.loads(res.stdout)
    assert body["passed"] is True


def test_scenario2_broken_json() -> None:
    res = run_cli(
        FIXTURES / "prompts/base.txt",
        FIXTURES / "prompts/base.txt",
        FIXTURES / "inputs/ten.jsonl",
        FIXTURES / "recordings/scenario2_json.json",
    )
    assert res.returncode == 1
    data = json.loads(res.stdout)
    failed = next(c for c in data["checks"] if c["rule"] == "json_valid")
    assert set(failed["case_ids"]) == {"t1", "t2"}


def test_scenario3_missing_field() -> None:
    res = run_cli(
        FIXTURES / "prompts/base.txt",
        FIXTURES / "prompts/base.txt",
        FIXTURES / "inputs/citations.jsonl",
        FIXTURES / "recordings/scenario3_fields.json",
    )
    assert res.returncode == 1
    data = json.loads(res.stdout)
    rule = next(c for c in data["checks"] if c["rule"] == "required_fields_missing")
    assert set(rule["case_ids"]) == {"f1", "f2", "f3"}


def test_scenario4_length_threshold() -> None:
    res = run_cli(
        FIXTURES / "prompts/base.txt",
        FIXTURES / "prompts/length_v2.txt",
        FIXTURES / "inputs/five.jsonl",
        FIXTURES / "recordings/scenario4_length.json",
    )
    assert res.returncode == 1
    data = json.loads(res.stdout)
    rule = next(c for c in data["checks"] if c["rule"] == "max_length_increase_pct")
    assert rule["passed"] is False
    assert "avg len" in rule["detail"]


def test_scenario5_refusal_increase() -> None:
    res = run_cli(
        FIXTURES / "prompts/base.txt",
        FIXTURES / "prompts/base.txt",
        FIXTURES / "inputs/five.jsonl",
        FIXTURES / "recordings/scenario5_refusal.json",
    )
    assert res.returncode == 1
    data = json.loads(res.stdout)
    rule = next(c for c in data["checks"] if c["rule"] == "max_new_refusals")
    assert "c1" in rule["case_ids"]


def test_scenario6_cache_hit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[str] = []
    from promptdiff.providers import recording as rec_mod

    original = rec_mod.RecordingProvider.complete

    def counting(self, prompt, settings, case_id, version):  # noqa: ANN001
        calls.append(f"{case_id}:{version}")
        return original(self, prompt, settings, case_id, version)

    monkeypatch.setattr(rec_mod.RecordingProvider, "complete", counting)
    cache_dir = tmp_path / "cache"
    monkeypatch.setattr("promptdiff.cache.CACHE_DIR", cache_dir)
    rec = FIXTURES / "recordings/scenario1.json"
    env_rec = str(rec)
    monkeypatch.setenv("PROMPTDIFF_RECORDING_FILE", env_rec)
    code1 = run_comparison(
        str(FIXTURES / "prompts/identical.txt"),
        str(FIXTURES / "prompts/identical.txt"),
        str(FIXTURES / "inputs/five.jsonl"),
        "json",
        True,
        None,
        None,
    )
    first_calls = len(calls)
    assert first_calls == 10  # 5 cases × 2 versions (distinct cache keys)
    code2 = run_comparison(
        str(FIXTURES / "prompts/identical.txt"),
        str(FIXTURES / "prompts/identical.txt"),
        str(FIXTURES / "inputs/five.jsonl"),
        "json",
        True,
        None,
        None,
    )
    assert code1 == 0 and code2 == 0
    assert len(calls) == first_calls


def test_scenario7_provider_failure_isolation() -> None:
    res = run_cli(
        FIXTURES / "prompts/base.txt",
        FIXTURES / "prompts/base.txt",
        FIXTURES / "inputs/ten.jsonl",
        FIXTURES / "recordings/scenario7_error.json",
    )
    assert res.returncode in (0, 1)
    assert res.returncode != 3


def test_scenario8_config_error() -> None:
    with pytest.raises(ValueError, match="Unknown rule"):
        load_config(FIXTURES / "config/bad_rule.yaml")


def test_scenario8_exit_code_via_run() -> None:
    from promptdiff.engine import run_from_config

    assert run_from_config(str(FIXTURES / "config/bad_rule.yaml")) == 2


def test_scenario9_pr_comment_sticky() -> None:
    with mock.patch.object(gh_comment, "_api") as api:
        api.side_effect = [
            [{"id": 5, "body": "<!-- promptdiff --> old"}],
            {},
        ]
        gh_comment.upsert_sticky_comment("o", "r", 1, "new")
        assert api.call_args_list[0][0][0] == "GET"
        assert api.call_args_list[1][0][0] == "PATCH"


def test_scenario10_no_prompt_change_no_run() -> None:
    code = action_entry.run_action(["README.md"], "prompts/**/*.txt")
    assert code == 0


def test_scenario11_fork_pr_message() -> None:
    with mock.patch.dict(
        os.environ,
        {
            "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_REPOSITORY": "fork/repo",
            "GITHUB_BASE_REPOSITORY": "upstream/repo",
            "GITHUB_EVENT_PATH": str(FIXTURES / "github_event.json"),
        },
    ):
        FIXTURES.mkdir(parents=True, exist_ok=True)
        event = FIXTURES / "github_event.json"
        event.write_text(json.dumps({"pull_request": {"number": 7}}))
        with mock.patch.object(gh_comment, "upsert_sticky_comment") as upsert:
            code = action_entry.run_action(["prompts/a.txt"], "prompts/**")
            assert code == 0
            upsert.assert_called_once()


def test_scenario12_secrets_hidden() -> None:
    secret = "sk-abcdefghijklmnopqrstuvwxyz123456"
    with mock.patch.dict(os.environ, {"OPENAI_API_KEY": secret}):
        res = OpenAIProvider().complete("p", ModelSettings("openai", "gpt-4o-mini"), "c", "a")
        assert res.error
        assert secret not in (res.error or "")
        assert secret not in redact(f"boom {secret}")


def test_scenario13_speed_and_cost() -> None:
    started = time.perf_counter()
    res = run_cli(
        FIXTURES / "prompts/base.txt",
        FIXTURES / "prompts/base.txt",
        FIXTURES / "inputs/twenty.jsonl",
        FIXTURES / "recordings/scenario13_twenty.json",
    )
    elapsed = time.perf_counter() - started
    assert res.returncode == 0
    assert elapsed < 60
    assert "Estimated cost" in res.stderr
    cost = float(res.stderr.strip().split("$")[-1])
    assert cost < 0.5


def test_output_formats_share_report() -> None:
    from promptdiff.compare import build_case_diff
    from promptdiff.models import Case, CheckResult, Output, Report
    from promptdiff.report import render_terminal

    case = Case("x", {})
    diff = build_case_diff(
        case,
        Output("x", "a", "hi"),
        Output("x", "b", "hello"),
    )
    report = Report([diff], [CheckResult("r", True, "ok")], True, 2, 5, 0, 1)
    md = render_md(report)
    js = json.loads(render_json(report))
    assert "PASS" in md or "FAIL" in md
    assert js["passed"] is True
    render_terminal(report)


def test_report_truncation() -> None:
    huge = "x" * 70000
    out = truncate_md(huge, "https://example.com/artifact")
    assert len(out) <= 65000
    assert "artifact" in out
