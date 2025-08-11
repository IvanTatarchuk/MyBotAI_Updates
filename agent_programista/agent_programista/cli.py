import json
import os
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from slugify import slugify

from .detectors import detect_test_runner
from .executor import execute_shell_command, execute_plan
from .git_ops import ensure_git_repo, create_branch, commit_all_changes, push_current_branch, get_repo_root
from .planner import generate_plan
from .editor import apply_edit_spec
from .utils import load_yaml, pretty_print_plan

console = Console()


@click.group()
def app() -> None:
    """Agent Programista CLI."""


@app.command()
def init() -> None:
    """Utwórz podstawowy plik konfiguracyjny .agent.yml w katalogu repozytorium."""
    repo_root = ensure_git_repo(os.getcwd())
    config_path = Path(repo_root) / ".agent.yml"

    if config_path.exists():
        console.print(f"[yellow]Plik konfiguracyjny już istnieje:[/yellow] {config_path}")
        return

    config_content = {
        "default_branch": "main",
        "commit_prefix": "agent:",
        "push": False,
    }
    config_path.write_text(json.dumps(config_content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    console.print(f"[green]Utworzono[/green] {config_path}")


@app.command()
@click.option("task", "--task", required=True, help="Opis zadania do wykonania")
def plan(task: str) -> None:
    """Wygeneruj plan kroków dla zadania (bez wykonywania)."""
    repo_root = get_repo_root(os.getcwd()) or os.getcwd()
    test_runner = detect_test_runner(repo_root)
    plan_steps = generate_plan(task_description=task, repo_root=repo_root, test_runner=test_runner)
    pretty_print_plan(plan_steps)


@app.command()
@click.option("task", "--task", required=True, help="Opis zadania do wykonania")
@click.option("dry_run", "--dry-run", is_flag=True, default=False, help="Tylko pokaż plan bez wykonywania")
@click.option("push", "--push/--no-push", default=False, help="Po zakończeniu spróbuj wykonać git push")
def run(task: str, dry_run: bool, push: bool) -> None:
    """Wykonaj zadanie: planowanie, branch, testy, edycje, commity."""
    repo_root = ensure_git_repo(os.getcwd())

    branch_name = f"agent/{slugify(task)[:40]}-{datetime.now().strftime('%Y%m%d-%H%M')}"
    create_branch(repo_root, branch_name)

    test_runner = detect_test_runner(repo_root)
    plan_steps = generate_plan(task_description=task, repo_root=repo_root, test_runner=test_runner)

    if dry_run:
        pretty_print_plan(plan_steps)
        console.print("[yellow]Dry-run zakończony.[/yellow]")
        return

    execute_plan(plan_steps, repo_root)

    commit_all_changes(repo_root, message=f"agent: {task}")

    if push:
        push_current_branch(repo_root)


@app.command()
@click.option("spec_path", "--spec", type=click.Path(exists=True, dir_okay=False), required=True, help="Ścieżka do pliku YAML ze specyfikacją edycji")
def edit(spec_path: str) -> None:
    """Zastosuj edycje plików zgodnie ze specyfikacją YAML."""
    repo_root = ensure_git_repo(os.getcwd())
    spec = load_yaml(spec_path)
    apply_edit_spec(spec, repo_root)
    console.print("[green]Edycje zostały zastosowane.[/green]")


@app.command()
def test() -> None:
    """Uruchom wykryty zestaw testów w repozytorium."""
    repo_root = ensure_git_repo(os.getcwd())
    runner = detect_test_runner(repo_root)

    if runner is None:
        console.print("[yellow]Nie wykryto runnera testów.[/yellow]")
        sys.exit(0)

    exit_code = execute_shell_command(runner.command, cwd=repo_root)
    sys.exit(exit_code)


@app.command()
@click.option("message", "--message", required=True, help="Wiadomość commitu")
def commit(message: str) -> None:
    """Wykonaj commit wszystkich zmian z podaną wiadomością."""
    repo_root = ensure_git_repo(os.getcwd())
    commit_all_changes(repo_root, message=message)
    console.print("[green]Commit wykonany.[/green]")