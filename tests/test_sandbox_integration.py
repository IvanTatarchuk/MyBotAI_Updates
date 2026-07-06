import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
CANARY_FILE = EXAMPLES_DIR / "write_probe_canary.txt"


def _sandbox_supported() -> bool:
    if shutil.which("unshare") is None:
        return False
    try:
        result = subprocess.run(
            ["unshare", "--mount", "--net", "--pid", "--mount-proc", "--fork", "--", "true"],
            capture_output=True,
            timeout=10,
        )
    except OSError:
        return False
    return result.returncode == 0


requires_sandbox = pytest.mark.skipif(
    not _sandbox_supported(),
    reason="this environment doesn't support the mount+net+pid namespaces mcp-guard probe needs",
)


@requires_sandbox
def test_probe_sandbox_actually_blocks_network_and_filesystem_writes():
    """The core claim of `mcp-guard probe`: tools that make a real outbound
    connection or a real write outside /tmp get blocked by the sandbox, not
    just described as risky — while unrelated tools keep working normally.
    """
    CANARY_FILE.unlink(missing_ok=True)
    stdio_command = f"{sys.executable} {EXAMPLES_DIR / 'sample_server.py'}"

    try:
        result = subprocess.run(
            ["mcp-guard", "probe", "--stdio", stdio_command, "--yes", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, result.stderr

        results_by_tool = {r["tool"]: r for r in json.loads(result.stdout)}

        assert results_by_tool["check_internet_access"]["ok"] is False
        assert "network" in results_by_tool["check_internet_access"]["detail"].lower()

        assert results_by_tool["write_outside_tmp"]["ok"] is False
        assert "read-only" in results_by_tool["write_outside_tmp"]["detail"].lower()
        assert not CANARY_FILE.exists(), "sandbox reported the write as blocked, but the file exists"

        # tools that don't touch the network/filesystem still run normally inside the sandbox
        assert results_by_tool["get_weather"]["ok"] is True
        assert results_by_tool["add_numbers"]["ok"] is True
    finally:
        CANARY_FILE.unlink(missing_ok=True)
