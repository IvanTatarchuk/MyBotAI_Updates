import os
import shutil
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from ruamel.yaml import YAML

from .executor import PlanStep

console = Console()

yaml = YAML()
yaml.preserve_quotes = True

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.load(f) or {}


def pretty_print_plan(plan_steps: List[PlanStep]) -> None:
    table = Table(title="Plan wykonania")
    table.add_column("#", justify="right")
    table.add_column("Rodzaj")
    table.add_column("Opis")
    table.add_column("Komenda/Payload")

    for idx, step in enumerate(plan_steps, start=1):
        payload_preview = step.command or (str(step.payload) if step.payload else "")
        table.add_row(str(idx), step.kind, step.description, payload_preview)

    console.print(table)


def ripgrep_search(pattern: str, cwd: str) -> None:
    rg = shutil.which("rg") or shutil.which("ripgrep")
    if rg is None:
        console.print("[yellow]ripgrep (rg) nie jest dostępny w systemie.[/yellow]")
        return

    os.system(f"cd {shlex_quote(cwd)} && {shlex_quote(rg)} -n --hidden -S -g '!.git' -e {shlex_quote(pattern)} | head -200 | sed -e 's/^/  /'")


def shlex_quote(text: str) -> str:
    # Minimal shell quoting; avoids importing shlex.quote to keep dependencies standard
    safe = text.replace("'", "'\\''")
    return f"'{safe}'"