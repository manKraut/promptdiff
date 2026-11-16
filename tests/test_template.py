import pytest

from promptdiff.template import render


def test_render() -> None:
    assert render("Hello {{name}}", {"name": "World"}) == "Hello World"


def test_missing_var() -> None:
    with pytest.raises(KeyError):
        render("{{x}}", {})
