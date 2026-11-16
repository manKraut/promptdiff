from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from promptdiff.models import Report

COMMENT_LIMIT = 65000
MARKER = "<!-- promptdiff -->"


def truncate_md(md: str, artifact_url: str | None = None) -> str:
    if len(md) <= COMMENT_LIMIT:
        return md
    link = artifact_url or "(see workflow artifacts)"
    keep = COMMENT_LIMIT - 200
    return md[:keep] + f"\n\n…truncated…\n\nFull report: {link}\n"


def render_terminal(report: Report) -> None:
    console = Console()
    table = Table(title="promptdiff summary")
    table.add_column("Rule")
    table.add_column("Pass")
    table.add_column("Detail")
    for chk in report.checks:
        table.add_row(chk.rule, "yes" if chk.passed else "NO", chk.detail)
    console.print(table)
    for diff in report.case_diffs:
        if not diff.diff_lines:
            continue
        adds = [ln[2:] for ln in diff.diff_lines if ln.startswith("+ ")]
        dels = [ln[2:] for ln in diff.diff_lines if ln.startswith("- ")]
        body = f"a: {' '.join(dels[:30]) or '…'}\nb: {' '.join(adds[:30]) or '…'}"
        console.print(Panel(body, title=f"case {diff.case_id}", border_style="cyan"))
    console.print(
        f"Verdict: {'PASS' if report.passed else 'FAIL'} | "
        f"cost ~${report.cost_estimate_usd:.3f} | {report.duration_ms}ms"
    )


def render_md(report: Report) -> str:
    lines = [MARKER, "# promptdiff report", ""]
    lines.append(f"**Verdict:** {'PASS' if report.passed else 'FAIL'}")
    lines.append(f"**Avg length:** a={report.mean_length_a:.1f} b={report.mean_length_b:.1f}")
    lines.append("")
    lines.append("## Rules")
    for chk in report.checks:
        icon = "✅" if chk.passed else "❌"
        lines.append(f"- {icon} `{chk.rule}`: {chk.detail}")
    lines.append("")
    lines.append("## Cases")
    for diff in report.case_diffs:
        lines.append(f"### `{diff.case_id}`")
        if diff.case_id in {c for chk in report.checks for c in chk.case_ids}:
            lines.append("- check failures linked")
        lines.append(f"- len {diff.length_a} → {diff.length_b}")
    return "\n".join(lines)


def render_json(report: Report) -> str:
    payload = {
        "passed": report.passed,
        "mean_length_a": report.mean_length_a,
        "mean_length_b": report.mean_length_b,
        "cost_estimate_usd": report.cost_estimate_usd,
        "duration_ms": report.duration_ms,
        "checks": [
            {
                "rule": c.rule,
                "passed": c.passed,
                "detail": c.detail,
                "case_ids": c.case_ids,
            }
            for c in report.checks
        ],
        "case_diffs": [
            {
                "case_id": d.case_id,
                "length_a": d.length_a,
                "length_b": d.length_b,
                "json_valid_b": d.json_valid_b,
                "missing_fields_b": d.missing_fields_b,
            }
            for d in report.case_diffs
        ],
        "errors": report.errors,
        "advisory_judge": report.advisory_judge,
    }
    return json.dumps(payload, indent=2)


def emit(report: Report, fmt: str) -> str:
    if fmt == "json":
        return render_json(report)
    if fmt == "md":
        return render_md(report)
    render_terminal(report)
    return ""
