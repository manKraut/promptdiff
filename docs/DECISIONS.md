# Decisions (ADRs)

Short, append-only records when agents choose beyond SPEC text. Prefer `docs/DEFAULTS.md` for SPEC open questions.

## ADR-001: Autonomous defaults (Move 0)

**Context:** SPEC §10 lists unresolved questions.  
**Decision:** Follow `docs/DEFAULTS.md` for Q1–Q6 until the human accepts v1.  
**Consequences:** Agents may implement without user input; mismatches are fixed at human acceptance against `ACCEPTANCE.md`.

## ADR-002: Repository layout (bootstrap)

**Context:** Initial skeleton included `web/`; product is a Python CLI.  
**Decision:** Python package under `src/promptdiff/`; remove unused `web/`; GitHub Action under `.github/actions/` or workflow in `.github/workflows/`.  
**Consequences:** Phase `01-scaffold` owns `pyproject.toml`, `src/`, and dev tooling.