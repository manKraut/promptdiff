# Defaults for autonomous execution

Resolves `docs/SPEC.md` open questions **without editing SPEC**. Agents may update this file only when a default proves wrong; mirror substantive changes in `docs/DECISIONS.md`.

| ID | Question (SPEC §10) | Default for v1 |
| --- | --- | --- |
| Q1 | Single-turn templates vs chat arrays | Single-turn `{{variable}}` templates only |
| Q2 | Rules vs base vs absolute thresholds | Compare **v2 vs v1** (relative); no absolute-only rules in v1 |
| Q3 | Judge in v1 | **Plugin interface stub**; built-in judge off, advisory when enabled later |
| Q4 | Providers in v1 | **OpenAI**, **Anthropic**, **Ollama** (local) |
| Q5 | PR comment strategy | **One sticky comment** updated in place |
| Q6 | License / PyPI name | **MIT**; package name **`promptdiff`** (confirm PyPI availability in scaffold; document in `DECISIONS.md` if taken) |

Additional defaults (from SPEC §11):

- Python **3.10+**, temperature **0**, judge **off**, distribution **PyPI + GitHub Action**
- Acceptance tests use **recorded responses**; scenario 13 is enforced via **fixture scale + mocked latency/cost**, not live API in CI