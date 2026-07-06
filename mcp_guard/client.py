from __future__ import annotations

import shlex

from mcp_guard.models import ToolDef


async def list_tools_stdio(command_line: str) -> list[ToolDef]:
    """Launch an MCP server over stdio and return its advertised tools.

    `command_line` is a shell-style string, e.g. "python my_mcp_server.py".
    Requires the `mcp` package (the official MCP SDK) at import time so that
    manifest-only usage of mcp-guard doesn't need it installed.
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    parts = shlex.split(command_line)
    if not parts:
        raise ValueError("empty --stdio command")
    command, args = parts[0], parts[1:]

    server_params = StdioServerParameters(command=command, args=args)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.list_tools()

    return [
        ToolDef(
            name=tool.name,
            description=tool.description or "",
            input_schema=tool.inputSchema or {},
        )
        for tool in response.tools
    ]
