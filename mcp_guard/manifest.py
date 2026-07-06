from __future__ import annotations

import json
from pathlib import Path

from mcp_guard.models import ToolDef


def load_manifest(path: str | Path) -> list[ToolDef]:
    """Load tool definitions from a static JSON manifest.

    Expected shape (matches the `tools` array of an MCP `tools/list` response):

        {"tools": [{"name": "...", "description": "...", "inputSchema": {...}}]}

    A bare top-level list of the same tool objects is also accepted.
    """
    data = json.loads(Path(path).read_text())
    tools_data = data["tools"] if isinstance(data, dict) else data

    return [
        ToolDef(
            name=t["name"],
            description=t.get("description", ""),
            input_schema=t.get("inputSchema", t.get("input_schema", {})),
        )
        for t in tools_data
    ]
