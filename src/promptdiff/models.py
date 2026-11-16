from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class Case:
    id: str
    input: dict[str, Any]
    expect: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelSettings:
    provider: str
    name: str
    temperature: float = 0.0
    base_url: str | None = None


@dataclass
class ProviderResult:
    text: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    error: str | None = None
    from_cache: bool = False


@dataclass
class Output:
    case_id: str
    version: Literal["a", "b"]
    text: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    error: str | None = None
    from_cache: bool = False


@dataclass
class CaseDiff:
    case_id: str
    diff_lines: list[str]
    length_a: int
    length_b: int
    json_valid_a: bool | None
    json_valid_b: bool | None
    missing_fields_b: list[str]
    refused_a: bool
    refused_b: bool


@dataclass
class CheckResult:
    rule: str
    passed: bool
    detail: str
    case_ids: list[str] = field(default_factory=list)


@dataclass
class RuleConfig:
    max_length_increase_pct: int | None = None
    json_valid: str | None = None
    max_new_refusals: int | None = None
    required_fields_missing: int | None = None


@dataclass
class AppConfig:
    inputs: str
    model: ModelSettings
    rules: RuleConfig
    judge_enabled: bool = False
    prompts_glob: list[str] = field(default_factory=list)
    concurrency: int = 5


@dataclass
class Report:
    case_diffs: list[CaseDiff]
    checks: list[CheckResult]
    passed: bool
    mean_length_a: float
    mean_length_b: float
    cost_estimate_usd: float
    duration_ms: int
    errors: list[str] = field(default_factory=list)
    advisory_judge: str | None = None
