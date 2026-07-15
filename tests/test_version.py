import re
import subprocess
from pathlib import Path

import mcp_guard


def _pyproject_version() -> str:
    # Read without tomllib so the test runs on Python 3.10 too (tomllib is 3.11+).
    pyproject = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text()
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', pyproject)
    assert match, "could not find version in pyproject.toml"
    return match.group(1)


def test_package_version_matches_pyproject():
    # __version__ is resolved from installed metadata, so this locks the source
    # tree's declared version to the version actually installed/built — the two
    # drifted once (pyproject at 0.2.0 while __init__ still said 0.1.0).
    assert mcp_guard.__version__ == _pyproject_version()


def test_cli_version_flag_reports_pyproject_version():
    result = subprocess.run(["mcp-guard", "--version"], capture_output=True, text=True, timeout=10)

    assert result.returncode == 0
    assert _pyproject_version() in result.stdout
