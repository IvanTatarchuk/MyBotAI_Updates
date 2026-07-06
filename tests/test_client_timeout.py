import asyncio
import sys

import pytest

from mcp_guard.client import StdioTimeout, list_tools_stdio


def test_list_tools_stdio_raises_clean_error_on_timeout():
    """A server that never responds must fail fast with a clear message, not hang
    forever or surface a raw ExceptionGroup/TimeoutError traceback.
    """
    # `python -c "import time; time.sleep(60)"` never speaks MCP on stdio, so the
    # initialize handshake will never complete — exactly like the real npx hang
    # this was written to guard against.
    hanging_command = f'{sys.executable} -c "import time; time.sleep(60)"'

    with pytest.raises(StdioTimeout, match="didn't respond within"):
        asyncio.run(list_tools_stdio(hanging_command, timeout=1))
