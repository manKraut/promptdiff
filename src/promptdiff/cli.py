"""CLI entrypoint."""

import click


@click.group()
@click.version_option(package_name="promptdiff")
def main() -> None:
    """Compare LLM outputs when a prompt changes."""


@main.command("compare")
@click.argument("prompt_a", type=click.Path(exists=True))
@click.argument("prompt_b", type=click.Path(exists=True))
@click.option("--inputs", required=True, type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["terminal", "md", "json"]), default="terminal")
@click.option("--no-cache", is_flag=True)
@click.option("--max-cases", type=int, default=None)
def compare_cmd(
    prompt_a: str,
    prompt_b: str,
    inputs: str,
    fmt: str,
    no_cache: bool,
    max_cases: int | None,
) -> None:
    """Compare two prompt files over a JSONL input file."""
    from promptdiff.engine import run_comparison

    code = run_comparison(
        prompt_a_path=prompt_a,
        prompt_b_path=prompt_b,
        inputs_path=inputs,
        output_format=fmt,
        use_cache=not no_cache,
        max_cases=max_cases,
        config=None,
    )
    raise SystemExit(code)


@main.command("run")
@click.option("--config", default="promptdiff.yaml", type=click.Path())
def run_cmd(config: str) -> None:
    """Run comparisons from promptdiff.yaml."""
    from promptdiff.engine import run_from_config

    code = run_from_config(config)
    raise SystemExit(code)
