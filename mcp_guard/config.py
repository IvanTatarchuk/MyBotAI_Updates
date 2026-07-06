from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_NAME = "mcp-guard.json"


def load_config(path: Path | None) -> dict[str, Any]:
    """Load policy defaults from a JSON config file.

    Recognized keys: "fail_on" (str), "ignore" (list[str] of rule ids),
    "rules" (list[str] of extra rule YAML paths, relative to the config file).

    If `path` is None, falls back to `./mcp-guard.json` when present, and to
    an empty config (all CLI defaults apply) otherwise. An explicit `path`
    that doesn't exist is an error.
    """
    if path is None:
        default_path = Path(DEFAULT_CONFIG_NAME)
        if not default_path.exists():
            return {}
        path = default_path

    data = json.loads(Path(path).read_text())

    base_dir = Path(path).parent
    data["rules"] = [str(base_dir / r) for r in data.get("rules", [])]

    return data
