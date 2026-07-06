import shutil
import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def _netns_supported() -> bool:
    if shutil.which("unshare") is None:
        return False
    try:
        result = subprocess.run(["unshare", "--net", "--", "true"], capture_output=True, timeout=10)
    except OSError:
        return False
    return result.returncode == 0


requires_netns = pytest.mark.skipif(
    not _netns_supported(),
    reason="`unshare --net` is not usable in this environment",
)


@requires_netns
def test_probe_sandbox_actually_blocks_network():
    """The core claim of `mcp-guard probe`: a tool that makes a real outbound
    connection attempt gets blocked by the sandbox, not just described as risky.
    """
    stdio_command = f"{sys.executable} {EXAMPLES_DIR / 'sample_server.py'}"

    result = subprocess.run(
        ["mcp-guard", "probe", "--stdio", stdio_command, "--yes", "--format", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr

    import json

    results_by_tool = {r["tool"]: r for r in json.loads(result.stdout)}

    assert results_by_tool["check_internet_access"]["ok"] is False
    assert "network" in results_by_tool["check_internet_access"]["detail"].lower()

    # tools that don't touch the network still run normally inside the sandbox
    assert results_by_tool["get_weather"]["ok"] is True
    assert results_by_tool["add_numbers"]["ok"] is True
