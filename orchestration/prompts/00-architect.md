# Phase 00: Architect

**Branch:** `agent/00-architect` (from `main`)  
**Forbidden:** Edit `docs/SPEC.md`, change `ACCEPTANCE.md` scenario Given/When/Then.

## Objective

Produce `docs/ARCHITECTURE.md` that an implementer can follow without further product decisions.

## Read

- `docs/SPEC.md`, `docs/DEFAULTS.md`, `docs/ACCEPTANCE.md` (requirements only)
- `docs/DECISIONS.md`

## Write / update

1. **`docs/ARCHITECTURE.md`** — include all of:
   - Directory tree (`src/promptdiff/`, `tests/`, `fixtures/`, `.github/`)
   - Module boundaries: `cli`, `config`, `models`, `template`, `runner`, `cache`, `compare`, `rules`, `report`, `providers/*`, `github_action`, `judge` (stub)
   - Data flow from CLI → Report (align with SPEC entities)
   - Provider adapter protocol (callable + recorded `fixtures` provider for tests)
   - Cache layout under `.promptdiff/cache/`
   - GitHub Action: workflow path + entry script
   - CI commands: `ruff check`, `ruff format --check`, `mypy`, `pytest`
   - Phase plan for 01–04 (bullet checklist tied to R1–R10 and scenarios 1–13)

2. **`docs/PROGRESS.md`** — phases 01–04 as checkboxes (all unchecked).

3. **`docs/DECISIONS.md`** — append ADRs only if architect overrides a default.

4. **Refine orchestration prompts 01–04** only if architecture requires retargeting (minimal edits).

## Done when

- `docs/ARCHITECTURE.md` is complete (no TBD placeholders).
- `pytest` not required yet (no package).

## Git

```bash
git checkout -b agent/00-architect
git commit -m "agent(00-architect): architecture and progress plan"
git push -u origin agent/00-architect
gh pr create --base main --title "agent(00-architect): architecture" --body "Architecture for v1. Auto-merge eligible."
```

Merge PR to `main` after push (agent may `gh pr merge --merge`).