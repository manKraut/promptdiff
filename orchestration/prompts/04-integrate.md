# Phase 04: Integrate

**Branch:** `release/candidate` (from `main`)  
**Human gate:** Do not merge this PR to `main`.

## Objective

Release-ready branch for human acceptance.

## Deliver

1. **`docs/RELEASE.md`** — changelog, known limits, `OPEN_QUESTIONS.md` summary
2. **`README.md`** — install, quickstart, env vars, link to Action; note README GIF for scenario 2 as optional/static demo
3. **`docs/ACCEPTANCE.md` §6 Evidence** — complete mapping scenario → test name
4. Polish: `pyproject.toml` readme/classifiers for PyPI-ready metadata (no publish unless credentials present — skip publish if BLOCKED)
5. Integration smoke: `pip install .` in fresh venv doc command

## PR

```bash
git checkout -b release/candidate
git push -u origin release/candidate
gh pr create --base main --title "Ready for human acceptance" --body-file docs/RELEASE_PR_BODY.md
```

Create `docs/RELEASE_PR_BODY.md` with:

- Checklist mirroring all 13 acceptance scenarios with test evidence links
- How to verify locally
- Explicit: **human must merge**

**Do not** `gh pr merge` this PR.