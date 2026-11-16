# Release candidate v0.1.0

## Changelog

- Python CLI: compare two prompt files over JSONL inputs with regression rules
- Providers: OpenAI, Anthropic, Ollama, plus recording provider for CI
- Reports: terminal (Rich), Markdown (PR comments), JSON
- File cache under `.promptdiff/cache/`
- GitHub Action composite (`action/action.yml`) and PR sticky comment helper
- Acceptance suite: scenarios 1–13 with recorded responses (`pytest`)

## Known limits

- `promptdiff run` compares first two `prompts/*.txt` files (full glob pairing deferred)
- Judge is stub-only, advisory, does not affect exit code
- Multi-sample (R11) not implemented
- PyPI publish not automated in this candidate

## Verify locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
promptdiff tests/fixtures/prompts/identical.txt tests/fixtures/prompts/identical.txt \
  --inputs tests/fixtures/inputs/five.jsonl \
  --format terminal \
  --no-cache
# with recordings:
export PROMPTDIFF_RECORDING_FILE=tests/fixtures/recordings/scenario1.json
```

## Open questions

See `docs/OPEN_QUESTIONS.md`. Defaults in `docs/DEFAULTS.md`.