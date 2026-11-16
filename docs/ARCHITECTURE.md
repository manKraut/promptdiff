# Architecture — promptdiff v1

Status: Phase 00 · 2026-03-25

## Layout

```text
promptdiff/
├── src/promptdiff/
│   ├── __init__.py
│   ├── __main__.py          # python -m promptdiff
│   ├── cli.py               # Click CLI
│   ├── config.py            # promptdiff.yaml loader
│   ├── models.py            # Case, Output, CheckResult, Report, ModelSettings
│   ├── template.py          # {{var}} substitution
│   ├── runner.py              # concurrent execution, retries
│   ├── cache.py               # file cache under .promptdiff/cache/
│   ├── compare.py             # word diff + metrics
│   ├── rules.py               # regression rule engine (v1 vs v2)
│   ├── report.py              # terminal / md / json renderers
│   ├── redact.py              # secret redaction in errors
│   ├── cost.py                # pre-run cost estimate
│   ├── judge.py               # stub; advisory only
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py            # Protocol + ProviderResult
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── ollama_provider.py
│   │   └── recording.py       # fixture/recorded responses for tests
│   └── github/
│       ├── __init__.py
│       ├── comment.py         # sticky PR comment
│       └── action_entry.py    # logic invoked from Action
├── action/
│   ├── action.yml
│   └── README.md
├── tests/
│   ├── conftest.py
│   ├── test_smoke.py
│   ├── test_template.py
│   ├── test_rules.py
│   ├── test_providers_contract.py
│   ├── acceptance/
│   │   └── test_scenarios.py
│   └── fixtures/
│       ├── inputs/            # *.jsonl
│       ├── prompts/           # *.txt pairs
│       └── recordings/        # *.json maps case_id -> output
├── .github/workflows/ci.yml
├── pyproject.toml
└── LICENSE
```

## Data flow

1. **Load** — Parse CLI args or `promptdiff.yaml`; read prompt files and JSONL cases.
2. **Template** — Render each prompt with case `input` dict.
3. **Run** — For each case × (prompt_a, prompt_b): cache lookup or `Provider.complete(rendered, settings)`.
4. **Compare** — Word-level diff; aggregate length, JSON validity, required fields, refusal heuristics.
5. **Rules** — Evaluate relative rules; populate `CheckResult` list; overall exit 0/1.
6. **Report** — Single `Report` object → terminal (Rich side-by-side), Markdown, JSON.
7. **GitHub (CI)** — Action detects changed prompts vs base ref; runs compare; updates sticky comment.

## Provider protocol

```python
class Provider(Protocol):
    name: str
    def complete(self, prompt: str, settings: ModelSettings) -> ProviderResult: ...
```

`ProviderResult`: `text`, `tokens_in`, `tokens_out`, `latency_ms`, `error: str | None`.

**Recording provider** (tests): `PROMPTDIFF_RECORDING_FILE` points to JSON `{"case_id:version": {...}}` keyed by runner.

Live providers use env API keys; never log key material (`redact.py`).

## Cache

Key: `sha256(prompt_text + json.dumps(input) + json.dumps(settings))`.  
Store: `.promptdiff/cache/<key>.json` with `ProviderResult`.  
`--no-cache` bypasses read/write.

## Rules (v1)

All relative **v2 vs v1** unless case `expect` adds per-case JSON/field requirements:

| Rule key | Behavior |
| --- | --- |
| `max_length_increase_pct` | Fail if mean len(v2) > mean len(v1) × (1 + pct/100) |
| `json_valid` | If `required`, fail cases where v2 invalid JSON when expect.format=json |
| `max_new_refusals` | Fail if v2 refuses more cases than v1 (heuristic keywords) |
| `required_fields_missing` | Fail if v2 JSON missing fields from case expect |

Unknown rule name → exit 2.

## Exit codes

0 pass · 1 rule tripped · 2 config/usage · 3 provider blocked run (all cases failed critically)

## GitHub Action

- Workflow in repo: `.github/workflows/promptdiff.yml` (example) + reusable `action/action.yml`.
- Inputs: `prompts_glob`, `inputs`, `config`.
- Uses `GITHUB_TOKEN` for sticky comment marker `<!-- promptdiff -->`.
- Fork PRs: post explanation; `continue-on-error` / success exit.

## CI

```bash
pip install -e ".[dev]"
ruff check src tests
ruff format --check src tests
mypy src/promptdiff --ignore-missing-imports
pytest -q
```

## Phase checklist (01–04)

### 01-scaffold
- [ ] pyproject.toml, LICENSE, cli --help, ci matrix 3.10/3.12

### 02-core
- [ ] R1 compare two prompts over JSONL
- [ ] R2 terminal word diff
- [ ] R3 metrics summary
- [ ] R4 rules + exit codes
- [ ] R5 md/json reports
- [ ] R6 action skeleton
- [ ] R7 three providers + recording
- [ ] R9 cache
- [ ] R10 yaml config

### 03-test-loop
- [ ] Scenarios 1–13 acceptance tests
- [ ] Evidence in ACCEPTANCE.md §6

### 04-integrate
- [ ] README, RELEASE.md, release/candidate PR