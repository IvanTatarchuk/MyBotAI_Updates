from pathlib import Path
from typing import Dict, List

from rich.console import Console

console = Console()


def _append(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(content)


def _create(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _replace_exact(path: Path, find: str, replace: str) -> None:
    text = path.read_text(encoding="utf-8")
    if find not in text:
        console.print(f"[yellow]Tekst do podmiany nie znaleziony w {path}[/yellow]")
        return
    new_text = text.replace(find, replace)
    path.write_text(new_text, encoding="utf-8")


def apply_edit_spec(spec: Dict, repo_root: str) -> None:
    edits: List[Dict] = spec.get("edits", []) if isinstance(spec, dict) else []
    for edit in edits:
        action = edit.get("action")
        rel_path = edit.get("path")
        if not action or not rel_path:
            console.print("[yellow]Pominięto niepoprawną definicję edycji.[/yellow]")
            continue
        path = Path(repo_root) / rel_path

        if action == "append":
            _append(path, edit.get("content", ""))
            console.print(f"[green]Dodano na końcu:[/green] {path}")
        elif action == "create":
            _create(path, edit.get("content", ""))
            console.print(f"[green]Utworzono plik:[/green] {path}")
        elif action == "replace_exact":
            _replace_exact(path, edit.get("find", ""), edit.get("replace", ""))
            console.print(f"[green]Zmieniono zawartość:[/green] {path}")
        else:
            console.print(f"[yellow]Nieznana akcja edycji:[/yellow] {action}")