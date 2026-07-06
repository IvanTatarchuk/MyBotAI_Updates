from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click

from mcp_guard.manifest import load_manifest
from mcp_guard.models import Severity
from mcp_guard.report import highest_severity, print_table, to_json
from mcp_guard.rules_engine import load_rules, scan_tools


@click.group()
@click.version_option(package_name="mcp-guard")
def main() -> None:
    """mcp-guard: security scanner for MCP servers."""


@main.command()
@click.option("--stdio", "stdio_command", metavar="COMMAND", help='Launch and scan a live server, e.g. --stdio "python server.py"')
@click.option("--manifest", "manifest_path", type=click.Path(exists=True, path_type=Path), help="Scan a static tools/list JSON manifest instead of a live server")
@click.option("--format", "output_format", type=click.Choice(["table", "json"]), default="table")
@click.option("--rules", "extra_rules", type=click.Path(exists=True, path_type=Path), multiple=True, help="Additional rule YAML file(s), on top of the built-in rule set")
@click.option("--fail-on", type=click.Choice(["low", "medium", "high"]), default=None, help="Exit non-zero if any finding is at or above this severity (for CI)")
def scan(
    stdio_command: str | None,
    manifest_path: Path | None,
    output_format: str,
    extra_rules: tuple[Path, ...],
    fail_on: str | None,
) -> None:
    """Scan an MCP server's tools for risky patterns."""
    if bool(stdio_command) == bool(manifest_path):
        raise click.UsageError("pass exactly one of --stdio or --manifest")

    if manifest_path:
        tools = load_manifest(manifest_path)
    else:
        from mcp_guard.client import list_tools_stdio

        tools = asyncio.run(list_tools_stdio(stdio_command))

    rules = load_rules(extra_paths=list(extra_rules))
    findings = scan_tools(tools, rules)

    if output_format == "json":
        click.echo(to_json(findings))
    else:
        print_table(findings)

    if fail_on:
        threshold = Severity.from_str(fail_on)
        worst = highest_severity(findings)
        if worst is not None and worst >= threshold:
            sys.exit(1)


if __name__ == "__main__":
    main()
