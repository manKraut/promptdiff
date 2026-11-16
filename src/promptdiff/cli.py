"""CLI entrypoint."""

import sys

import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Compare LLM outputs when a prompt changes."""


@main.command()
@click.argument("prompt_a", type=click.Path(exists=True))
@click.argument("prompt_b", type=click.Path(exists=True))
@click.option("--inputs", required=True, type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["terminal", "md", "json"]), default="terminal")
@click.option("--no-cache", is_flag=True)
@click.option("--max-cases", type=int, default=None)
def compare(
    prompt_a: str,
    prompt_b: str,
    inputs: str,
    fmt: str,
    no_cache: bool,
    max_cases: int | None,
) -> None:
    from promptdiff.engine import run_comparison

    raise SystemExit(run_comparison(prompt_a, prompt_b, inputs, fmt, not no_cache, max_cases, None))


@main.command("run")
@click.option("--config", default="promptdiff.yaml", type=click.Path())
def run_cmd(config: str) -> None:
    from promptdiff.engine import run_from_config

    raise SystemExit(run_from_config(config))


def entrypoint() -> None:
    """SPEC: `promptdiff <a> <b> --inputs` without subcommand."""
    argv = sys.argv[1:]
    if (
        argv
        and argv[0] not in ("run", "compare", "--help", "-h", "--version")
        and not argv[0].startswith("-")
    ):
        sys.argv.insert(1, "compare")
    main()
