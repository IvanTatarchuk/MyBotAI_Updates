import os
import subprocess
from pathlib import Path
from typing import Optional

from git import Repo, InvalidGitRepositoryError, NoSuchPathError
from rich.console import Console

console = Console()


def get_repo_root(start_dir: str) -> Optional[str]:
    try:
        repo = Repo(start_dir, search_parent_directories=True)
        return str(repo.git.rev_parse("--show-toplevel"))
    except Exception:
        return None


def ensure_git_repo(start_dir: str) -> str:
    repo_root = get_repo_root(start_dir)
    if repo_root:
        return repo_root

    # Initialize new repo in start_dir
    Path(start_dir).mkdir(parents=True, exist_ok=True)
    repo = Repo.init(start_dir)
    # Ensure default branch main if empty
    try:
        repo.git.checkout('-B', 'main')
    except Exception:
        pass
    console.print(f"[green]Zainicjalizowano repozytorium Git w[/green] {start_dir}")
    return start_dir


def create_branch(repo_root: str, branch_name: str) -> None:
    repo = Repo(repo_root)
    current = repo.active_branch.name if not repo.head.is_detached else None
    if current == branch_name:
        console.print(f"[blue]Już na branchu[/blue] {branch_name}")
        return
    repo.git.checkout('-B', branch_name)
    console.print(f"[green]Przełączono na branch[/green] {branch_name}")


def commit_all_changes(repo_root: str, message: str) -> None:
    repo = Repo(repo_root)
    repo.git.add(all=True)
    # Skip commit if nothing to commit
    if not repo.index.diff("HEAD") and not repo.untracked_files:
        console.print("[yellow]Brak zmian do commitu.[/yellow]")
        return
    repo.index.commit(message)
    console.print(f"[green]Commit:[/green] {message}")


def push_current_branch(repo_root: str) -> None:
    repo = Repo(repo_root)
    try:
        active = repo.active_branch.name
    except TypeError:
        console.print("[yellow]Brak aktywnego brancha.[/yellow]")
        return

    # Check remote origin
    if 'origin' not in [r.name for r in repo.remotes]:
        console.print("[yellow]Brak zdalnego 'origin'. Pomijam push.[/yellow]")
        return

    try:
        repo.git.push('--set-upstream', 'origin', active)
        console.print(f"[green]Push wysłany:[/green] {active}")
    except Exception as exc:
        console.print(f"[red]Push nieudany:[/red] {exc}")