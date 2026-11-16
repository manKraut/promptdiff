# promptdiff: Acceptance Criteria

Status: Draft v0.1 · 2026-11-11 · Covers SPEC.md v0.1

## 1. Definition of done for v1

All 13 scenarios below pass in CI using recorded provider responses, the README GIF reproduces scenario 2, and `pip install promptdiff` works from a clean environment on Python 3.10 and 3.12.

## 2. Test setup

- **Providers:** recorded or fake responses only. No live API calls in the acceptance suite.
- **Fixtures:** a 5-case and a 10-case JSONL file, prompt pairs (identical, JSON-breaking, field-dropping, longer, refusing), and a `promptdiff.yaml` per scenario.
- **GitHub scenarios:** run against a fake GitHub API or a throwaway test repository.

## 3. Scenarios

Each scenario uses Given / When / Then and maps to a requirement in SPEC.md.

| # | Scenario | Requirement |
| --- | --- | --- |
| 1 | Identical prompts pass | R1, R4 |
| 2 | Broken JSON is caught | R3, R4 |
| 3 | Missing field is caught | R3, R4 |
| 4 | Length threshold | R3, R4 |
| 5 | Refusal increase | R3, R4 |
| 6 | Cache hit | R9 |
| 7 | Provider failure isolation | R1, R7 |
| 8 | Config error | R10 |
| 9 | PR comment | R5, R6 |
| 10 | No prompt change, no run | R6 |
| 11 | Fork PR | R6 |
| 12 | Secrets stay hidden | Security (SPEC 7) |
| 13 | Speed and cost | Quality (SPEC 7) |

### Scenario 1: Identical prompts pass

- **Given** two identical prompt files and a 5-case input file
- **When** `promptdiff` runs
- **Then** the exit code is 0 and the report shows no differences

### Scenario 2: Broken JSON is caught

- **Given** a v2 prompt that makes 2 of 10 outputs invalid JSON, and rule `json_valid: required`
- **When** the comparison runs
- **Then** the exit code is 1 and the report names the 2 failing case ids

### Scenario 3: Missing field is caught

- **Given** cases with `required_fields: [citations]` and a v2 that drops `citations` in 3 cases
- **When** the comparison runs
- **Then** the report lists those 3 cases and the exit code is 1

### Scenario 4: Length threshold

- **Given** `max_length_increase_pct: 30` and a v2 whose average output is 45% longer
- **When** the comparison runs
- **Then** the length rule fails and the report shows both averages

### Scenario 5: Refusal increase

- **Given** `max_new_refusals: 0` and a v2 that refuses 1 case that v1 answered
- **When** the comparison runs
- **Then** the exit code is 1 and the report names the case

### Scenario 6: Cache hit

- **Given** a completed run
- **When** the same command runs again with no changes
- **Then** no provider calls are made and the verdict is identical

### Scenario 7: Provider failure isolation

- **Given** a provider error on 1 of 10 cases
- **When** the comparison runs
- **Then** the other 9 cases are reported, the failed case is marked as an error, and the exit code is 3 only if the failure blocked the comparison

### Scenario 8: Config error

- **Given** an unknown rule name in `promptdiff.yaml`
- **When** the tool starts
- **Then** it exits with code 2 and a message naming the rule

### Scenario 9: PR comment

- **Given** a PR that edits a file matching the prompt glob
- **When** the Action runs
- **Then** exactly one comment containing the Markdown report is posted, and a second push updates that comment instead of adding another

### Scenario 10: No prompt change, no run

- **Given** a PR that changes no files matching the glob
- **When** the workflow triggers
- **Then** the Action makes no provider calls and posts no comment

### Scenario 11: Fork PR

- **Given** a PR from a fork with no secrets available
- **When** the Action runs
- **Then** it posts an explanatory message and does not fail the check

### Scenario 12: Secrets stay hidden

- **Given** an invalid API key
- **When** the run fails
- **Then** the error output and any report contain no part of the key

### Scenario 13: Speed and cost

- **Given** 20 cases on a small model
- **When** the comparison runs on a standard CI runner
- **Then** it completes in under 60 seconds and the printed cost estimate is under $0.50

## 4. Additional checks

| Area | Check |
| --- | --- |
| Output formats | `--format md` and `--format json` render the same Report data as the terminal view |
| Exit codes | Codes 0, 1, 2 and 3 are each produced by at least one scenario above |
| Report size | A report over the comment limit is truncated and links to the full artifact |
| Install | Clean install on Python 3.10 and 3.12, on Linux, macOS and Windows |
| Provider contract | Each shipped adapter passes the same adapter test suite |

## 5. Out of scope for acceptance

Dashboard, accounts, history, dataset management, multi-turn traces, and judge quality. The judge is only checked for being off by default and never changing the exit code.
