# promptdiff

Compare LLM outputs when a prompt changes; fail the build on behavioral regressions.

**Distribution:** Python 3.10+ CLI (`pip install -e .`) and GitHub Action (`action/action.yml`).

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

export PROMPTDIFF_RECORDING_FILE=tests/fixtures/recordings/scenario1.json
promptdiff tests/fixtures/prompts/identical.txt tests/fixtures/prompts/identical.txt \
  --inputs tests/fixtures/inputs/five.jsonl --format terminal
```

Live runs need `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (see `.env.example`).

## Commands

```bash
promptdiff <prompt_a> <prompt_b> --inputs cases.jsonl [--format terminal|md|json] [--no-cache]
promptdiff run --config promptdiff.yaml
```

## Regression rules

Configured in `promptdiff.yaml` (see `docs/SPEC.md`). Exit codes: `0` pass, `1` rule failed, `2` config error, `3` provider blocked.

## CI

GitHub Actions workflow `.github/workflows/ci.yml` runs ruff, mypy, and pytest on Python 3.10 and 3.12.

## Docs

- Product: `docs/SPEC.md`
- Human acceptance: `docs/ACCEPTANCE.md`
- Agents: `AGENTS.md`, `orchestration/`

## Demo (scenario 2 — broken JSON)

With recordings (no live API):

```bash
export PROMPTDIFF_RECORDING_FILE=tests/fixtures/recordings/scenario2_json.json
promptdiff tests/fixtures/prompts/base.txt tests/fixtures/prompts/base.txt \
  --inputs tests/fixtures/inputs/ten.jsonl --format md --no-cache
```

Expect exit code `1` and case ids `t1`, `t2` in the report.