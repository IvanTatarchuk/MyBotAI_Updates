#!/usr/bin/env python3
"""Scan every server in servers.yaml with mcp-guard and write results.json.

This is the data-collection half of the MCP Security Observatory. It reuses
mcp-guard's own public API — `list_tools_stdio` to enumerate a server's tools
and `scan_tools` to apply the built-in rule set — so the observatory never
contains a verdict that `mcp-guard scan` wouldn't also produce on its own.

Run it from a directory where the servers are installed (npm packages under
./node_modules, pip packages importable). See observatory/README.md.

    python observatory/scan.py --servers observatory/servers.yaml \
        --out observatory/results.json --timeout 45
"""
from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from mcp_guard.client import StdioTimeout, list_tools_stdio
from mcp_guard.rules_engine import load_rules, scan_tools


def _pkg_version(entry: dict) -> str | None:
    """Best-effort resolved version of the installed package, for provenance."""
    pkg = entry["package"]
    try:
        if entry["ecosystem"] == "npm":
            out = subprocess.run(
                ["node", "-e", f"process.stdout.write(require('{pkg}/package.json').version)"],
                capture_output=True, text=True, timeout=15,
            )
            return out.stdout.strip() or None
        if entry["ecosystem"] == "pypi":
            from importlib.metadata import version
            return version(pkg)
    except Exception:
        return None
    return None


async def _scan_one(entry: dict, rules, timeout: float) -> dict:
    name = entry["name"]
    result = {
        "name": name,
        "package": entry["package"],
        "ecosystem": entry["ecosystem"],
        "official": entry.get("official", False),
        "version": _pkg_version(entry),
        "status": "ok",
        "error": None,
        "tool_count": 0,
        "findings": [],
    }
    try:
        tools = await list_tools_stdio(entry["command"], timeout=timeout)
    except StdioTimeout:
        result["status"] = "timeout"
        result["error"] = f"no response within {timeout}s"
        return result
    except Exception as exc:  # launch/handshake failure — recorded, not fatal
        result["status"] = "error"
        result["error"] = f"{type(exc).__name__}: {exc}"[:300]
        return result

    result["tool_count"] = len(tools)
    for f in scan_tools(tools, rules):
        result["findings"].append(
            {
                "tool": f.tool_name,
                "rule_id": f.rule_id,
                "severity": f.severity.value,
                "message": f.message,
            }
        )
    return result


async def _run(servers: list[dict], timeout: float) -> list[dict]:
    rules = load_rules()
    results = []
    for entry in servers:
        print(f"  scanning {entry['name']} ...", file=sys.stderr, flush=True)
        results.append(await _scan_one(entry, rules, timeout))
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--servers", default="observatory/servers.yaml", type=Path)
    ap.add_argument("--out", default="observatory/results.json", type=Path)
    ap.add_argument("--timeout", default=45.0, type=float)
    args = ap.parse_args()

    servers = yaml.safe_load(args.servers.read_text())
    results = asyncio.run(_run(servers, args.timeout))

    scanned = [r for r in results if r["status"] == "ok"]
    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "mcp_guard_rules": [r.id for r in load_rules()],
        "servers_total": len(results),
        "servers_scanned": len(scanned),
        "results": results,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {args.out} ({len(scanned)}/{len(results)} scanned)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
