from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @classmethod
    def from_str(cls, value: str) -> "Severity":
        return cls[value.strip().upper()]

    def __str__(self) -> str:
        return self.name


@dataclass
class ToolDef:
    """A single MCP tool definition, as returned by tools/list."""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)

    def searchable_text(self) -> str:
        import json

        schema_text = json.dumps(self.input_schema, sort_keys=True) if self.input_schema else ""
        return "\n".join([self.name, self.description, schema_text])


@dataclass
class Finding:
    tool_name: str
    rule_id: str
    severity: Severity
    message: str
