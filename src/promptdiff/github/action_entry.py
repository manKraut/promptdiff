from __future__ import annotations

import json
import os
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path


def run_action(changed_files: list[str], prompts_glob: str) -> int:
    matched = [f for f in changed_files if fnmatch(f, prompts_glob)]
    if not matched:
        return 0

    fork = bool(
        os.environ.get("GITHUB_BASE_REPOSITORY")
        and os.environ.get("GITHUB_REPOSITORY") != os.environ.get("GITHUB_BASE_REPOSITORY")
    )
    if fork:
        from promptdiff.github.comment import upsert_sticky_comment

        owner = os.environ["GITHUB_REPOSITORY"].split("/")[0]
        repo = os.environ["GITHUB_REPOSITORY"].split("/")[1]
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        if event_path:
            ev = json.loads(Path(event_path).read_text(encoding="utf-8"))
            pr = int(ev["pull_request"]["number"])
            upsert_sticky_comment(
                owner,
                repo,
                pr,
                "promptdiff cannot run on fork PRs without secrets. "
                "Run locally or use trusted branches.",
            )
        return 0

    proc = subprocess.run(
        [sys.executable, "-m", "promptdiff", "run"],
        capture_output=True,
        text=True,
    )
    return proc.returncode
