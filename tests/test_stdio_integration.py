import json
import subprocess
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def test_stdio_scan_against_live_sample_server():
    """End-to-end: spawn the real sample MCP server over stdio and scan it.

    Exercises the actual mcp SDK client/session code in mcp_guard/client.py,
    not just the static-manifest path.
    """
    stdio_command = f"{sys.executable} {EXAMPLES_DIR / 'sample_server.py'}"

    result = subprocess.run(
        ["mcp-guard", "scan", "--stdio", stdio_command, "--format", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr

    findings = json.loads(result.stdout)
    findings_by_tool = {f["tool"]: f for f in findings}

    assert findings_by_tool["run_shell_command"]["rule_id"] == "shell-exec"
    assert findings_by_tool["run_shell_command"]["severity"] == "high"
    assert findings_by_tool["read_any_file"]["rule_id"] == "fs-read-any"
    assert "get_weather" not in findings_by_tool
    assert "add_numbers" not in findings_by_tool
