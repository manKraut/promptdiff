# promptdiff: Specification

Status: Draft v0.1 · 2026-11-11

## 1. Purpose

promptdiff shows what changed in an LLM's outputs when a prompt changes, and fails the build when quality regresses. It ships as a Python CLI and library, plus a GitHub Action that comments on pull requests touching prompt files.

**Problem.** Engineers edit prompts by feel. A git diff shows changed words, not changed behavior: broken JSON, dropped fields, more refusals, longer answers.

**Success definition.** An engineer can compare two prompt versions in one command, and a reviewer can judge a prompt change from one PR comment in under 2 minutes.

## 2. Users

| Persona | Job to be done |
| --- | --- |
| AI engineer (primary) | Know what a prompt edit changes before merging |
| Reviewer / tech lead | Judge a prompt PR quickly from a behavior summary |
| Solo builder / OSS maintainer | Get regression safety with near-zero setup |

Not targeted: researchers running large benchmarks, teams needing dashboards, annotation queues or run history.

## 3. Scope

### 3.1 Requirements

Priority: M = must, S = should, C = could.

| ID | Requirement | Priority |
| --- | --- | --- |
| R1 | Compare two prompt files over a JSONL test-input file, using identical model settings for both | M |
| R2 | Terminal side-by-side output diff with word-level highlighting | M |
| R3 | Per-run behavior summary: length change, JSON validity, missing required fields, refusal rate | M |
| R4 | Regression rules that set a non-zero exit code when tripped | M |
| R5 | Markdown report suitable for a PR comment | M |
| R6 | GitHub Action that posts the report as one sticky PR comment, only when prompt files change | M |
| R7 | Provider adapters: OpenAI, Anthropic, and one local option (Ollama or OpenAI-compatible endpoint) | M |
| R8 | Optional LLM-judge summary line, off by default, never affects the exit code | S |
| R9 | Output cache keyed by hash of prompt + input + model settings | S |
| R10 | `promptdiff.yaml` config file | S |
| R11 | Multi-sample runs (N samples per input) with reported spread | C |

### 3.2 Non-goals for v1

Web dashboard, database, user accounts, prompt hosting or versioning, dataset management, human annotation, fine-tuning, multi-turn agent traces.

## 4. Behavior

### 4.1 Command

```
promptdiff <prompt_a> <prompt_b> --inputs tests.jsonl [--format terminal|md|json] [--no-cache] [--max-cases N]
promptdiff run            # uses promptdiff.yaml; in CI compares each changed prompt to its base-branch version
```

### 4.2 Run flow

1. **Trigger.** Local invocation, or the Action finds prompt files changed in the PR and pairs each with its base-branch version.
2. **Load.** Read both prompt versions, the JSONL cases and the config. Exit 2 on a bad file or unknown rule.
3. **Run.** Send every case to both versions with identical model settings. Serve repeats from the cache. Run requests concurrently (default 5). Record a failed case as an error without stopping the others. Retry transient errors with backoff.
4. **Compare.** Diff outputs word by word. Compute length change, JSON validity, missing fields and refusal rate. Evaluate each regression rule.
5. **Report.** Render the terminal view, plus Markdown or JSON when requested. All three render the same Report object.
6. **Post (CI only).** Create or update one sticky PR comment with the Markdown report.
7. **Verdict.** Exit 0 if no rule tripped, 1 if at least one did.

### 4.3 Exit codes

| Code | Meaning |
| --- | --- |
| 0 | No rule tripped |
| 1 | At least one regression rule tripped |
| 2 | Usage or config error (bad file, unknown rule) |
| 3 | Provider or network failure that blocked the comparison |

## 5. Inputs and data model

### 5.1 Test inputs (JSONL, one case per line)

```json
{"id": "refund-1", "input": {"question": "Can I return opened items?"}, "expect": {"format": "json", "required_fields": ["answer", "citations"]}}
{"id": "refund-2", "input": {"question": "How long do refunds take?"}}
```

`expect` is optional and drives per-case checks.

### 5.2 Prompt files

Plain text with `{{variable}}` placeholders filled from each case's `input` object. Single-turn only in v1 (see open question Q1).

### 5.3 Config (`promptdiff.yaml`)

```yaml
prompts: ["prompts/**/*.txt"]
inputs: tests/prompt_inputs.jsonl
model: {provider: openai, name: gpt-4o-mini, temperature: 0}
rules:
  max_length_increase_pct: 30
  json_valid: required
  max_new_refusals: 0
  required_fields_missing: 0
judge: {enabled: false}
```

### 5.4 Entities

| Entity | Fields |
| --- | --- |
| Case | `id`, `input`, optional `expect` |
| Run | prompt version label, model settings, list of outputs |
| Output | case id, text, tokens in/out, latency ms, error if any |
| Check result | case id, rule name, pass or fail, detail |
| Report | per-case diffs, aggregate metrics, rule verdicts, overall verdict |

## 6. Integrations

| Integration | Direction | Purpose | Auth / config |
| --- | --- | --- | --- |
| OpenAI API | Outbound | Run prompts | `OPENAI_API_KEY` |
| Anthropic API | Outbound | Run prompts, optional judge | `ANTHROPIC_API_KEY` |
| Local models | Outbound | Free local runs | Base URL in config |
| GitHub Actions | Inbound trigger | Run on PRs changing files matching a glob | Workflow YAML in the user's repo |
| GitHub REST API | Outbound | Post or update one sticky PR comment | `GITHUB_TOKEN` with `pull-requests: write` |
| Git | Local | Resolve base-branch prompt versions | Checkout with `fetch-depth: 0` |
| PyPI | Distribution | `pip install promptdiff` | Trusted publishing from GitHub |

**Provider adapter contract.** One function takes a prompt, an input and model settings, and returns text, token counts and latency. A new provider is one file plus one test.

## 7. Quality attributes

| Attribute | Target | Approach |
| --- | --- | --- |
| Determinism | Same inputs and settings give the same verdict on re-run | Temperature 0 default, cache, structural rules |
| Cost | 20 cases under $0.50 on a small model | Small default model, cache, judge off by default, cost estimate printed before the run |
| Speed | 20 cases in under 60 seconds | Concurrency limit (default 5) |
| Security | API keys never printed or written to reports | Env vars only, redact keys in errors, no telemetry |
| Privacy | Test inputs may hold sensitive text | Reports truncate inputs by default, `--no-cache` option, only provider calls leave the machine |
| Portability | Linux, macOS, Windows; Python 3.10+ | Pure-Python dependencies |
| Contributor friendliness | New provider in one file and one test | Adapter protocol, `CONTRIBUTING.md`, recorded-response fixtures |

## 8. Constraints

- GitHub comments are limited to roughly 65,000 characters: the Markdown report needs a truncation mode with a link to the full artifact.
- PRs from forks have no access to secrets: the Action must post an explanatory message and not fail the check.
- Provider rate limits and transient errors need retries with backoff, and one failed case must not hide the others.

## 9. Risks

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Flaky verdicts from sampling noise | High | Temperature 0, structural rules, optional multi-sample mode with a tolerance |
| Crowded niche (existing eval tools) | High | Stay tiny: PR-comment workflow and one-command setup |
| API cost surprises in CI | Medium | Cost estimate before run, `--max-cases` cap, cache |
| LLM judge disagrees with humans | Medium | Advisory only, never changes the exit code |
| Fork PRs cannot read secrets | Medium | Detect and post an explanatory comment |

## 10. Open questions

- [ ] Q1. Single-turn `{{variable}}` templates only, or also chat-message arrays (system + user)?
- [ ] Q2. Can a rule compare against absolute thresholds, or only against the base version?
- [ ] Q3. Is the judge built in for v1, or a plugin interface only?
- [ ] Q4. Which three providers ship in v1?
- [ ] Q5. One sticky PR comment updated in place, or a new comment per push? (This spec assumes sticky.)
- [ ] Q6. License (MIT is the usual choice) and name availability on PyPI and GitHub.

## 11. Decisions log

| Decision | Value |
| --- | --- |
| Language | Python |
| Distribution | PyPI package and GitHub Action |
| State storage | Plain files in the user's repo, no database |
| Default model temperature | 0 |
| Judge | Off by default, advisory only |
