import subprocess
import sys

import promptdiff


def test_version() -> None:
    assert promptdiff.__version__


def test_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "promptdiff", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "compare" in result.stdout or "Compare" in result.stdout
