# Agent playbook

Global rules for every orchestration phase. Phase-specific work lives in `orchestration/prompts/`.

## Read order

1. `docs/SPEC.md` — **read-only; never edit**
2. `docs/ACCEPTANCE.md` — **do not change scenario definitions**; you may add an "Evidence" subsection with links or test names
3. Current file from `orchestration/phases.yaml` → `orchestration/prompts/`
4. `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/DEFAULTS.md`, `docs/OPEN_QUESTIONS.md`
5. `orchestration/phases.yaml` — branch name, `depends_on`, loop limits

## Autonomy

- **Do not ask the user questions.** Do not use interactive confirmations for product or design choices.
- If `docs/SPEC.md` is silent, follow `docs/DEFAULTS.md`, then record the choice in `docs/DECISIONS.md`.
- If still blocked, append to `docs/OPEN_QUESTIONS.md`, pick the default, and continue.
- **`BLOCKED` only** for missing required secrets (name the env var; ensure `.env.example` documents it). Stop the phase and document in `OPEN_QUESTIONS.md` if no default exists.

## Scope and layout

- **v1 is a Python CLI/library + GitHub Action**, not a web app. Package code under `src/promptdiff/` (or layout mandated in `ARCHITECTURE.md` after phase 00). Do not add `web/`.
- Stay within requirements **R1–R10** unless `ARCHITECTURE.md` and a `DECISIONS.md` entry justify deferring an Should/Could item.
- One phase → one branch (name from `phases.yaml`). Commit in logical chunks with messages: `agent(<phase-id>): <short description>`.

## Quality gates

Before marking a phase done:

- Run the commands listed in that phase’s prompt (lint, typecheck, tests).
- Do not mark tasks complete while CI is red (once real CI exists from phase `01-scaffold`).
- Acceptance scenarios are implemented via **recorded/fake provider fixtures** unless a scenario explicitly requires live E2E (see `ACCEPTANCE.md`).

## Git and PRs

- Push the phase branch to `origin`.
- Open a PR toward the integration branch defined in `phases.yaml` (usually `main` or the previous phase branch).
- Do not force-push `main`. Do not commit secrets, `.env`, or API keys.
- Phase `04-integrate` opens `release/candidate` for **human acceptance** only.

## Forbidden edits

| Path | Rule |
| --- | --- |
| `docs/SPEC.md` | Never |
| `docs/ACCEPTANCE.md` scenarios §3 | Never change Given/When/Then; evidence append only |
| User credentials | Never log or write to reports |

## Cloud Agent environment

If using Cursor Cloud Agents, run install/start from `.cursor/environment.json` after phase `01-scaffold` updates it.