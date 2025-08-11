#!/usr/bin/env python3
"""
📈 Business Intelligence Builder - scaffolding for CRM/ERP
"""
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
import json

@dataclass
class BISpec:
    name: str
    workspace: str = "projects"

class BusinessIntelligenceBuilder:
    def __init__(self, workspace: str = "projects"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)

    def create_system(self, spec: BISpec) -> Dict[str, Any]:
        bdir = self.workspace / spec.name
        (bdir / "crm").mkdir(parents=True, exist_ok=True)
        (bdir / "erp").mkdir(parents=True, exist_ok=True)
        (bdir / "crm" / "customers.json").write_text(json.dumps([], indent=2))
        (bdir / "erp" / "inventory.json").write_text(json.dumps([], indent=2))
        (bdir / "README.md").write_text(f"# {spec.name}\nBI scaffold\n")
        return {"bi": spec.name, "path": str(bdir)}

    def demo(self) -> Dict[str, Any]:
        return self.create_system(BISpec(name="bi_system_sample"))