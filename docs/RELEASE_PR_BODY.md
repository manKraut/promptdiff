## Ready for human acceptance

**Do not merge without running `docs/ACCEPTANCE.md`.**

### Acceptance evidence

| # | Scenario | Evidence |
| --- | --- | --- |
| 1 | Identical prompts pass | `test_scenario1_identical_prompts_pass` |
| 2 | Broken JSON | `test_scenario2_broken_json` |
| 3 | Missing field | `test_scenario3_missing_field` |
| 4 | Length threshold | `test_scenario4_length_threshold` |
| 5 | Refusal increase | `test_scenario5_refusal_increase` |
| 6 | Cache hit | `test_scenario6_cache_hit` |
| 7 | Provider failure isolation | `test_scenario7_provider_failure_isolation` |
| 8 | Config error | `test_scenario8_config_error`, `test_scenario8_exit_code_via_run` |
| 9 | PR comment | `test_scenario9_pr_comment_sticky` |
| 10 | No prompt change | `test_scenario10_no_prompt_change_no_run` |
| 11 | Fork PR | `test_scenario11_fork_pr_message` |
| 12 | Secrets hidden | `test_scenario12_secrets_hidden` |
| 13 | Speed and cost | `test_scenario13_speed_and_cost` |

Full mapping in `docs/ACCEPTANCE.md` §6.

### Test plan

```bash
pip install -e ".[dev]"
ruff check src tests && mypy src/promptdiff && pytest
```

### Human gate

Approve and merge this PR to ship v0.1.0 to `main`.