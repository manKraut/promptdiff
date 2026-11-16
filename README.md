# promptdiff

Compare LLM outputs when a prompt changes; fail the build on behavioral regressions. Python CLI/library and GitHub Action.

**Docs:** `docs/SPEC.md` (product) · `docs/ACCEPTANCE.md` (human ship bar) · `AGENTS.md` (agent rules)

**Run (after phase 01-scaffold):**

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
promptdiff --help
```

**Autonomous build:** `orchestration/phases.yaml` and `orchestration/prompts/`.