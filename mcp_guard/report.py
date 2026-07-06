from __future__ import annotations

import json

from mcp_guard.models import Finding, Severity

_SEVERITY_STYLE = {
    Severity.HIGH: "bold red",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "dim",
}


def to_json(findings: list[Finding]) -> str:
    return json.dumps(
        [
            {
                "tool": f.tool_name,
                "rule_id": f.rule_id,
                "severity": str(f.severity).lower(),
                "message": f.message,
            }
            for f in findings
        ],
        indent=2,
    )


def print_table(findings: list[Finding]) -> None:
    from rich.console import Console
    from rich.table import Table

    console = Console()

    if not findings:
        console.print("[green]No findings — nothing matched the current rule set.[/green]")
        return

    table = Table(show_edge=False)
    table.add_column("Tool")
    table.add_column("Severity")
    table.add_column("Finding")

    for f in sorted(findings, key=lambda x: x.severity, reverse=True):
        style = _SEVERITY_STYLE[f.severity]
        table.add_row(f.tool_name, f"[{style}]{f.severity}[/{style}]", f"{f.message} (rule: {f.rule_id})")

    console.print(table)

    counts = {s: sum(1 for f in findings if f.severity == s) for s in Severity}
    summary = ", ".join(
        f"{counts[s]} {s.name.lower()}" for s in (Severity.HIGH, Severity.MEDIUM, Severity.LOW) if counts[s]
    )
    tool_count = len({f.tool_name for f in findings})
    console.print(f"\n{len(findings)} findings across {tool_count} tools ({summary})")


def highest_severity(findings: list[Finding]) -> Severity | None:
    return max((f.severity for f in findings), default=None)
