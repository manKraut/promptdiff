# Phase 03: Test loop

**Branch:** `agent/03-test-loop`  
**Loop:** Up to 5 iterations until CI green and acceptance tests pass.

## Objective

All **13 scenarios** in `docs/ACCEPTANCE.md` pass via **recorded/fake** providers (no live API in CI).

## Work

1. `tests/fixtures/`: 5- and 10-case JSONL, prompt pairs, recorded response maps per scenario
2. `tests/acceptance/` or parametrized tests mapping scenario 1–13
3. Scenarios 9–11: mock GitHub API (`httpx` mock or `unittest.mock`)
4. Scenario 12: assert key redaction in errors
5. Scenario 13: 20-case fixture run with mocked latency/cost estimate (no live API)
6. Report truncation test for 65k limit
7. Append **Evidence** table to `docs/ACCEPTANCE.md` §6 (new section) listing test module per scenario — **do not** edit Given/When/Then in §3

## Loop protocol

Each iteration:

```bash
ruff check src tests && ruff format --check src tests
mypy src/promptdiff
pytest -q --cov=src/promptdiff
```

Fix failures; commit `agent(03-test-loop): fix <scenario>` until all pass or 5 iterations exhausted (document remainder in `OPEN_QUESTIONS.md`).

## Done when

`pytest` passes all acceptance tests; CI workflow green on push.

## Git

Push branch; PR to main; merge when green.