from __future__ import annotations

import os
import subprocess
import sys


def run_action(changed_files: list[str], prompts_glob: str) -> int:
    if os.environ.get("GITHUB_EVENT_NAME") == "pull_request" and os.environ.get(
        "GITHUB_HEAD_REF", ""
    ).endswith("/merge"):
        pass
    fork = os.environ.get("GITHUB_REPOSITORY") != os.environ.get("GITHUB_BASE_REPOSITORY", "")
    if fork:
        from promptdiff.github.comment import upsert_sticky_comment

        owner = os.environ["GITHUB_REPOSITORY"].split("/")[0]
        repo = os.environ["GITHUB_REPOSITORY"].split("/")[1]
        pr = int(os.environ.get("GITHUB_REF", "").split("/")[-1]) if False else 0
        _pr = os.environ.get("GITHUB_EVENT_PATH")
        if _pr:
            import json
            from pathlib import Path

            ev = json.loads(Path(_pr).read_text())
            pr = int(ev["pull_request"]["number"])
            upsert_sticky_comment(
                owner,
                repo,
                pr,
                "promptdiff cannot run on fork PRs without secrets. "
                "Run locally or use trusted branches.",
            )
        return 0

    matched = [f for f in changed_files if _glob_match(f, prompts_glob)]
    if not matched:
        return 0
    proc = subprocess.run(
        [sys.executable, "-m", "promptdiff", "run"],
        capture_output=True,
        text=True,
    )
    return proc.returncode


def _glob_match(path: str, pattern: str) -> bool:
    from fnmatch import fnmatch

    return fnmatch(path, pattern)
