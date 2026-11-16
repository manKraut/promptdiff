from __future__ import annotations

import json
import os
from urllib import request

from promptdiff.report import MARKER, truncate_md


def _api(method: str, url: str, body: dict | None = None) -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    data = None if body is None else json.dumps(body).encode()
    req = request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    with request.urlopen(req, timeout=30) as resp:  # noqa: S310
        raw = resp.read().decode()
        return json.loads(raw) if raw else {}


def upsert_sticky_comment(owner: str, repo: str, pr_number: int, body_md: str) -> None:
    body_md = truncate_md(f"{MARKER}\n{body_md}")
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    comments = _api("GET", url)
    existing_id = None
    for c in comments:
        if MARKER in (c.get("body") or ""):
            existing_id = c["id"]
            break
    if existing_id:
        _api(
            "PATCH",
            f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{existing_id}",
            {"body": body_md},
        )
    else:
        _api("POST", url, {"body": body_md})
