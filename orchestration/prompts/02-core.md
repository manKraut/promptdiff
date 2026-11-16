# Phase 02: Core

**Branch:** `agent/02-core` (from `main`)

## Objective

Implement v1 core per `docs/SPEC.md` and `docs/ARCHITECTURE.md` (R1–R7, R9–R10; R8 judge stub; defer R11).

## Implement

| Area | Deliverable |
| --- | --- |
| Models | `Case`, `Output`, `CheckResult`, `Report` (dataclasses/pydantic or dataclasses) |
| Template | `{{var}}` fill from case `input` |
| Config | Load `promptdiff.yaml`; exit 2 on unknown rule keys |
| Providers | `openai`, `anthropic`, `ollama` HTTP adapters; **`recording`** fixture provider reading JSON maps |
| Runner | Concurrent (default 5), retries, per-case errors don’t abort batch |
| Cache | Hash(prompt+input+settings); `.promptdiff/cache/`; `--no-cache` |
| Compare | Word-level diff (side-by-side terminal via rich); metrics: length, JSON, fields, refusals |
| Rules | Relative v1 vs v2: `max_length_increase_pct`, `json_valid`, `max_new_refusals`, `required_fields_missing` |
| Reports | `--format terminal|md|json` same Report |
| CLI | `promptdiff <a> <b> --inputs FILE [--format] [--no-cache] [--max-cases N]` |
| CLI | `promptdiff run` reads `promptdiff.yaml` |
| GitHub | `action.yml` + workflow template under `action/` or `.github/action/`; sticky comment helper (library) |
| Judge | Stub module; `judge.enabled` no-op |

## Fixtures (start)

- `tests/fixtures/` layout for acceptance (can expand in phase 03)

## Tests

- Unit tests for template, rules, JSON checks, redaction
- Provider contract test shared by adapters

## Done when

Core commands run against **recording** provider with sample fixtures (not full acceptance yet).

```bash
pytest -q
ruff check src tests && mypy src/promptdiff
```

## Git

`agent/02-core`, push, PR, merge to main.