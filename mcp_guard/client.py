from __future__ import annotations

import asyncio
import shlex

from mcp_guard.models import ToolDef

DEFAULT_TIMEOUT_SECONDS = 30


class StdioTimeout(RuntimeError):
    """Raised when the server doesn't respond within the timeout.

    Notably: `npx -y <package>` is a common way MCP servers are documented to be
    run, but npx itself can swallow/delay the initialize handshake in a way that
    hangs forever rather than erroring. Prefer resolving to the actual
    interpreter + entry point (e.g. `node .../index.js`) if you hit this.
    """


def _is_or_contains_timeout(exc: BaseException) -> bool:
    """True if `exc` is a TimeoutError, or an (Exception)Group containing one.

    anyio/MCP's TaskGroups re-wrap a TimeoutError raised by `asyncio.wait_for`
    inside an ExceptionGroup by the time it reaches our `except` clause, so a
    plain `except TimeoutError` doesn't catch it. Avoids `except*` (3.11+ only
    syntax) since this project supports Python 3.10.
    """
    if isinstance(exc, TimeoutError):
        return True
    sub_exceptions = getattr(exc, "exceptions", None)
    if not sub_exceptions:
        return False
    return any(_is_or_contains_timeout(e) for e in sub_exceptions)


def _timeout_message(timeout: float) -> str:
    return (
        f"server didn't respond within {timeout}s. If the command uses `npx`, try resolving it "
        "to the actual interpreter and entry point instead (npx can hang the initialize handshake)."
    )


async def list_tools_stdio(command_line: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> list[ToolDef]:
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

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await asyncio.wait_for(session.initialize(), timeout=timeout)
                response = await asyncio.wait_for(session.list_tools(), timeout=timeout)
    except Exception as exc:
        if _is_or_contains_timeout(exc):
            raise StdioTimeout(_timeout_message(timeout)) from exc
        raise

    return [
        ToolDef(
            name=tool.name,
            description=tool.description or "",
            input_schema=tool.inputSchema or {},
        )
        for tool in response.tools
    ]
