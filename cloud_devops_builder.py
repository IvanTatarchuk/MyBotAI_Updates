#!/usr/bin/env python3
"""
☁️ Cloud & DevOps Builder - scaffolding for CI/CD and infra
"""
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
import json

@dataclass
class DevOpsSpec:
    name: str
    provider: str = "generic"  # aws, azure, gcp, generic
    workspace: str = "projects"

class CloudDevOpsBuilder:
    def __init__(self, workspace: str = "projects"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)

    def create_infra(self, spec: DevOpsSpec) -> Dict[str, Any]:
        infra_dir = self.workspace / spec.name / "infra"
        infra_dir.mkdir(parents=True, exist_ok=True)
        (infra_dir / "pipeline.yml").write_text("""
name: ci
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: echo "Build"
""")
        (infra_dir / "terraform.tf").write_text("""
terraform {
  required_version = ">= 1.0.0"
}
provider "null" {}
resource "null_resource" "example" {}
""")
        (infra_dir / "env.json").write_text(json.dumps({"provider": spec.provider}, indent=2))
        return {"infra": str(infra_dir), "files": 3}

    def suggest_dependencies(self) -> List[str]:
        return ["terraform", "github actions", "docker"]

    def demo(self) -> Dict[str, Any]:
        return self.create_infra(DevOpsSpec(name="infra_sample"))