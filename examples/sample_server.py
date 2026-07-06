"""A tiny MCP server for exercising `mcp-guard scan --stdio`.

Mixes a couple of safe tools with a couple of deliberately risky ones so a
scan against this server (over real stdio, not a static manifest) produces
a non-trivial report:

    mcp-guard scan --stdio "python examples/sample_server.py"
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-guard-sample")


@mcp.tool()
def get_weather(city: str) -> str:
    """Returns the current weather for a given city name."""
    return f"It's sunny in {city}."


@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Adds two numbers and returns the sum."""
    return a + b


@mcp.tool()
def run_shell_command(command: str) -> str:
    """Runs an arbitrary shell command on the host and returns stdout/stderr."""
    return f"(not actually executed) would run: {command}"


@mcp.tool()
def read_any_file(path: str) -> str:
    """Reads any file on disk given an absolute path, with full filesystem access."""
    return f"(not actually executed) would read: {path}"


@mcp.tool()
def check_internet_access() -> str:
    """Attempts a real outbound network connection to a public DNS server.

    Genuinely executes (no stub) — used to demonstrate that `mcp-guard probe`'s
    sandbox actually blocks outbound network access rather than just claiming to.
    """
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect(("8.8.8.8", 53))
        return "network reachable"
    finally:
        s.close()


if __name__ == "__main__":
    mcp.run()
