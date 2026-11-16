# Phase 01: Scaffold

**Branch:** `agent/01-scaffold` (from `main` after 00 merged)  
**Depends on:** `docs/ARCHITECTURE.md`

## Objective

Shippable Python package skeleton, dev tooling, CI, and `.cursor/environment.json` that works.

## Create

- `pyproject.toml`: project `promptdiff`, Python 3.10+, deps: `click`, `pyyaml`, `httpx`, `rich`, `difflib` (stdlib); dev: `pytest`, `pytest-cov`, `ruff`, `mypy`
- `src/promptdiff/__init__.py`, `cli.py` with `promptdiff --help`
- `LICENSE` MIT
- `.env.example` listing `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`
- `CONTRIBUTING.md` (brief provider adapter note)
- Update `.github/workflows/ci.yml`: Python 3.10 & 3.12 matrix, `pip install -e ".[dev]"`, ruff, mypy, pytest (smoke test passes)
- Update `.cursor/environment.json`: `pip install -e ".[dev]"`, `promptdiff --help`
- `tests/test_smoke.py`: import package, CLI exits 0 for `--help`

## Done when

```bash
pip install -e ".[dev]"
ruff check src tests
ruff format --check src tests
mypy src/promptdiff
pytest -q
```

All pass locally.

## Git

Branch `agent/01-scaffold`, commit `agent(01-scaffold): python package and ci`, push, PR to main, merge.