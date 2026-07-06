from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click

from mcp_guard.config import load_config
from mcp_guard.manifest import load_manifest
from mcp_guard.models import Severity
from mcp_guard.report import highest_severity, print_table, to_json
from mcp_guard.rules_engine import load_rules, scan_tools


@click.group()
@click.version_option(package_name="mcp-guard")
def main() -> None:
    """mcp-guard: security scanner for MCP servers."""


@main.command()
@click.option(
    "--stdio",
    "stdio_command",
    metavar="COMMAND",
    help='Launch and scan a live server, e.g. --stdio "python server.py"',
)
@click.option(
    "--manifest",
    "manifest_path",
    type=click.Path(exists=True, path_type=Path),
    help="Scan a static tools/list JSON manifest instead of a live server",
)
@click.option("--format", "output_format", type=click.Choice(["table", "json"]), default="table")
@click.option(
    "--rules",
    "extra_rules",
    type=click.Path(exists=True, path_type=Path),
    multiple=True,
    help="Additional rule YAML file(s), on top of the built-in rule set",
)
@click.option(
    "--fail-on",
    type=click.Choice(["low", "medium", "high"]),
    default=None,
    help="Exit non-zero if any finding is at or above this severity (for CI). Overrides mcp-guard.json.",
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Policy file (default: ./mcp-guard.json if present)",
)
@click.option(
    "--timeout",
    type=float,
    default=None,
    help="Seconds to wait for the server to respond before giving up (default: 30). "
    "If the command uses `npx`, a hang usually means resolving it to the actual "
    "interpreter/entry point instead would fix it.",
)
def scan(
    stdio_command: str | None,
    manifest_path: Path | None,
    output_format: str,
    extra_rules: tuple[Path, ...],
    fail_on: str | None,
    config_path: Path | None,
    timeout: float | None,
) -> None:
    """Scan an MCP server's tools for risky patterns."""
    if bool(stdio_command) == bool(manifest_path):
        raise click.UsageError("pass exactly one of --stdio or --manifest")

    config = load_config(config_path)

    if manifest_path:
        tools = load_manifest(manifest_path)
    else:
        assert stdio_command is not None  # guaranteed by the exactly-one-of check above
        from mcp_guard.client import DEFAULT_TIMEOUT_SECONDS, StdioTimeout, list_tools_stdio

        try:
            tools = asyncio.run(list_tools_stdio(stdio_command, timeout=timeout or DEFAULT_TIMEOUT_SECONDS))
        except StdioTimeout as exc:
            raise click.ClickException(str(exc)) from exc

    rule_paths = list(extra_rules) + list(config.get("rules", []))
    rules = load_rules(extra_paths=rule_paths)
    findings = scan_tools(tools, rules)

    ignored_ids = set(config.get("ignore", []))
    if ignored_ids:
        findings = [f for f in findings if f.rule_id not in ignored_ids]

    if output_format == "json":
        click.echo(to_json(findings))
    else:
        print_table(findings)

    effective_fail_on = fail_on or config.get("fail_on")
    if effective_fail_on:
        threshold = Severity.from_str(effective_fail_on)
        worst = highest_severity(findings)
        if worst is not None and worst >= threshold:
            sys.exit(1)


@main.command(name="rules")
@click.option(
    "--rules",
    "extra_rules",
    type=click.Path(exists=True, path_type=Path),
    multiple=True,
    help="Additional rule YAML file(s), on top of the built-in rule set",
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Policy file (default: ./mcp-guard.json if present) — resolves extra rules and ignored ids",
)
def list_rules(extra_rules: tuple[Path, ...], config_path: Path | None) -> None:
    """List every detection rule that would be applied by `scan`."""
    from mcp_guard.report import print_rules_table

    config = load_config(config_path)
    rule_paths = list(extra_rules) + list(config.get("rules", []))
    rules = load_rules(extra_paths=rule_paths)
    ignored_ids = set(config.get("ignore", []))

    print_rules_table(rules, ignored_ids)


@main.command()
@click.option(
    "--stdio",
    "stdio_command",
    metavar="COMMAND",
    required=True,
    help='Command that launches the MCP server, e.g. --stdio "python server.py"',
)
@click.option("--format", "output_format", type=click.Choice(["table", "json"]), default="table")
@click.option(
    "--yes",
    "confirmed",
    is_flag=True,
    help="Required: confirms you understand this actually runs the server and calls its tools for real.",
)
@click.option(
    "--timeout",
    type=float,
    default=None,
    help="Seconds to wait for the server/each tool call to respond before giving up (default: 30).",
)
def probe(stdio_command: str, output_format: str, confirmed: bool, timeout: float | None) -> None:
    """Actually call every tool once with synthesized arguments, inside a sandbox.

    EXPERIMENTAL. Unlike `scan`, this executes the server's real code — it launches
    the server and calls each tool with placeholder arguments derived from its input
    schema, to see what happens instead of only reading what its description claims.

    The sandbox blocks outbound network access and filesystem writes outside a
    throwaway scratch directory (Linux namespaces via `unshare`). It does NOT
    prevent the tool from reading real files, and the read-only remount doesn't
    cover separately-mounted filesystems. Read THREAT_MODEL.md before relying on
    this.
    """
    import shlex

    from mcp_guard.client import DEFAULT_TIMEOUT_SECONDS, StdioTimeout
    from mcp_guard.probe import probe_tools_stdio
    from mcp_guard.report import print_probe_table, to_probe_json
    from mcp_guard.sandbox import SandboxUnavailable, build_sandboxed_command, describe_sandbox

    if not confirmed:
        raise click.ClickException(
            "`probe` actually runs the target server and calls its tools for real "
            "(filesystem reads are not sandboxed, and the read-only remount doesn't cover "
            "separately-mounted filesystems — see THREAT_MODEL.md). "
            "Re-run with --yes once you understand this."
        )

    try:
        sandboxed_command = build_sandboxed_command(shlex.split(stdio_command))
    except SandboxUnavailable as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Sandbox: {describe_sandbox()}", err=True)
    try:
        results = asyncio.run(probe_tools_stdio(sandboxed_command, timeout=timeout or DEFAULT_TIMEOUT_SECONDS))
    except StdioTimeout as exc:
        raise click.ClickException(str(exc)) from exc

    if output_format == "json":
        click.echo(to_probe_json(results))
    else:
        print_probe_table(results)


if __name__ == "__main__":
    main()
