from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ProbeResult:
    tool_name: str
    arguments: dict[str, Any]
    ok: bool
    detail: str


def synthesize_args(input_schema: dict[str, Any]) -> dict[str, Any]:
    """Derive minimal, inert arguments for a tool's required parameters.

    Only fills in `required` properties, using benign placeholder values keyed
    off each property's declared type — the goal is to trigger the tool's real
    code path without supplying anything meaningfully adversarial.
    """
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])
    return {name: _placeholder_for(properties.get(name, {})) for name in required}


def _placeholder_for(schema: dict[str, Any]) -> Any:
    if schema.get("enum"):
        return schema["enum"][0]
    if "default" in schema:
        return schema["default"]

    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        for candidate in schema_type:
            if candidate != "null":
                return _placeholder_for({**schema, "type": candidate})
        return None

    if schema_type == "string":
        return "http://127.0.0.1:0/mcp-guard-probe" if schema.get("format") in ("uri", "url") else "mcp-guard-probe"
    if schema_type in ("integer", "number"):
        return 0
    if schema_type == "boolean":
        return False
    if schema_type == "array":
        return []
    if schema_type == "object":
        return {}
    return "mcp-guard-probe"


async def probe_tools_stdio(command: list[str]) -> list[ProbeResult]:
    """Launch `command` (already sandbox-wrapped) as an MCP server over stdio,
    then call every tool it advertises once, with synthesized arguments.
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    server_params = StdioServerParameters(command=command[0], args=command[1:])

    results: list[ProbeResult] = []
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_tools()

            for tool in listing.tools:
                arguments = synthesize_args(tool.inputSchema or {})
                results.append(await _call_one(session, tool.name, arguments))

    return results


async def _call_one(session: Any, tool_name: str, arguments: dict[str, Any]) -> ProbeResult:
    try:
        result = await session.call_tool(tool_name, arguments)
    except Exception as exc:  # noqa: BLE001 - transport/tool errors are exactly what we report
        return ProbeResult(tool_name, arguments, ok=False, detail=str(exc))

    detail = _extract_text(result.content) or ("ok" if not result.isError else "tool returned an error")
    return ProbeResult(tool_name, arguments, ok=not result.isError, detail=detail)


def _extract_text(content: list[Any]) -> str:
    parts = [block.text for block in content if hasattr(block, "text")]
    return " ".join(parts).strip()[:200]
