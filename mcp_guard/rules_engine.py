from __future__ import annotations

import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import yaml

from mcp_guard.models import Finding, Severity, ToolDef


@dataclass
class Rule:
    id: str
    name: str
    severity: Severity
    pattern: re.Pattern[str]
    message: str

    @classmethod
    def from_dict(cls, data: dict) -> Rule:
        return cls(
            id=data["id"],
            name=data["name"],
            severity=Severity.from_str(data["severity"]),
            pattern=re.compile(data["pattern"], re.IGNORECASE),
            message=data["message"],
        )


def load_rules(extra_paths: list[Path] | None = None) -> list[Rule]:
    """Load the built-in rule set plus any user-supplied YAML files."""
    rules: list[Rule] = []

    package_rules_dir = resources.files("mcp_guard").joinpath("rules")
    for entry in sorted(package_rules_dir.iterdir(), key=lambda p: p.name):
        if entry.name.endswith((".yaml", ".yml")):
            rules.extend(_load_rule_file(entry.read_text()))

    for path in extra_paths or []:
        rules.extend(_load_rule_file(Path(path).read_text()))

    return rules


def _load_rule_file(text: str) -> list[Rule]:
    data = yaml.safe_load(text) or []
    return [Rule.from_dict(item) for item in data]


def scan_tool(tool: ToolDef, rules: list[Rule]) -> list[Finding]:
    text = tool.searchable_text()
    findings: list[Finding] = []
    for rule in rules:
        if rule.pattern.search(text):
            findings.append(
                Finding(
                    tool_name=tool.name,
                    rule_id=rule.id,
                    severity=rule.severity,
                    message=rule.message,
                )
            )
    return findings


def scan_tools(tools: list[ToolDef], rules: list[Rule] | None = None) -> list[Finding]:
    rules = rules if rules is not None else load_rules()
    findings: list[Finding] = []
    for tool in tools:
        findings.extend(scan_tool(tool, rules))
    return findings
