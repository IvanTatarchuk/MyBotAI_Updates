#!/usr/bin/env python3
"""
🏭 IoT Builder - scaffolding for IoT/embedded
"""
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class IoTSpec:
    name: str
    workspace: str = "projects"

class IoTBuilder:
    def __init__(self, workspace: str = "projects"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)

    def create_iot_project(self, spec: IoTSpec) -> Dict[str, Any]:
        idir = self.workspace / spec.name
        (idir / "device").mkdir(parents=True, exist_ok=True)
        (idir / "cloud").mkdir(parents=True, exist_ok=True)
        (idir / "device" / "main.py").write_text("""
#!/usr/bin/env python3
print('Sensor read placeholder')
""")
        (idir / "cloud" / "ingest.py").write_text("""
#!/usr/bin/env python3
print('Cloud ingest placeholder')
""")
        return {"iot": spec.name, "path": str(idir)}

    def demo(self) -> Dict[str, Any]:
        return self.create_iot_project(IoTSpec(name="iot_project_sample"))