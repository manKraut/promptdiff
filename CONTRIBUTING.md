# Contributing

Add a new model provider in `src/promptdiff/providers/<name>_provider.py` implementing `Provider` in `base.py`, plus a row in `test_providers_contract.py`.

Run `pip install -e ".[dev]"` and `pytest`.