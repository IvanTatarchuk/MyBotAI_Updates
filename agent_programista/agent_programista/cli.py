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
from .fs_ops import read_text, write_text, copy_path, move_path, delete_path, mkdir_p, chmod_path
from .watch import watch_and_run
from ruamel.yaml import YAML
from .net_ops import download
from .proc_ops import list_processes, kill_pid
from .archive_ops import zip_dir, unzip_file
import shutil

console = Console()

yaml = YAML()

yaml.indent(mapping=2, sequence=2, offset=2)


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
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(config_content, f)
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


@app.command(name="exec")
@click.option("cmd", "--cmd", required=True, help="Komenda powłoki do wykonania")
@click.option("timeout", "--timeout", type=int, default=None, help="Timeout w sekundach")
def exec_cmd(cmd: str, timeout: int | None) -> None:
    """Wykonaj dowolną komendę w repozytorium."""
    repo_root = ensure_git_repo(os.getcwd())
    code = execute_shell_command(cmd, cwd=repo_root, timeout_seconds=timeout)
    sys.exit(code)


@app.command()
@click.option("pattern", "--pattern", required=True, help="Wzorzec do wyszukania (regex)")
def search(pattern: str) -> None:
    from .utils import ripgrep_search

    repo_root = ensure_git_repo(os.getcwd())
    ripgrep_search(pattern, repo_root)


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


@app.group()
def fs() -> None:
    """Operacje na systemie plików."""


@fs.command("read")
@click.option("path", "--path", required=True)
@click.option("head", "--head", type=int, default=None)
@click.option("tail", "--tail", type=int, default=None)
def fs_read(path: str, head: int | None, tail: int | None) -> None:
    text = read_text(path, head=head, tail=tail)
    click.echo(text)


@fs.command("write")
@click.option("path", "--path", required=True)
@click.option("content", "--content", required=True)
@click.option("append", "--append/--overwrite", default=False)
def fs_write(path: str, content: str, append: bool) -> None:
    write_text(path, content, append=append)
    console.print(f"[green]Zapisano:[/green] {path}")


@fs.command("copy")
@click.option("src", "--src", required=True)
@click.option("dst", "--dst", required=True)
def fs_copy(src: str, dst: str) -> None:
    copy_path(src, dst)
    console.print(f"[green]Skopiowano:[/green] {src} -> {dst}")


@fs.command("move")
@click.option("src", "--src", required=True)
@click.option("dst", "--dst", required=True)
def fs_move(src: str, dst: str) -> None:
    move_path(src, dst)
    console.print(f"[green]Przeniesiono:[/green] {src} -> {dst}")


@fs.command("delete")
@click.option("path", "--path", required=True)
def fs_delete(path: str) -> None:
    delete_path(path)
    console.print(f"[green]Usunięto:[/green] {path}")


@fs.command("mkdir")
@click.option("path", "--path", required=True)
def fs_mkdir(path: str) -> None:
    mkdir_p(path)
    console.print(f"[green]Utworzono katalog:[/green] {path}")


@fs.command("chmod")
@click.option("path", "--path", required=True)
@click.option("mode", "--mode", required=True, help="np. 755")
def fs_chmod(path: str, mode: str) -> None:
    chmod_path(path, mode)
    console.print(f"[green]Zmieniono prawa:[/green] {path} -> {mode}")


@app.command()
@click.option("path", "--path", default=".", help="Katalog do obserwacji")
def watch(path: str) -> None:
    """Obserwuj zmiany w plikach i uruchamiaj testy."""
    repo_root = ensure_git_repo(os.getcwd())
    runner = detect_test_runner(repo_root)
    if runner is None:
        console.print("[yellow]Brak runnera testów.[/yellow]")
        return

    def run_tests() -> None:
        execute_shell_command(runner.command, cwd=repo_root)

    watch_and_run(path=path, run=run_tests)


@app.command()
def doctor() -> None:
    """Sprawdź dostępność narzędzi systemowych i konfigurację."""
    repo_root = get_repo_root(os.getcwd()) or os.getcwd()
    tools = ["git", "rg", "pytest", "npm", "pnpm", "yarn"]
    rows = []
    for t in tools:
        path = shutil.which(t)
        rows.append((t, path or "brak"))
    table = Table(title="Narzędzia")
    table.add_column("Narzędzie")
    table.add_column("Ścieżka")
    for name, path in rows:
        table.add_row(name, path)
    console.print(table)
    console.print(f"Repo root: {repo_root}")


@app.group()
def proc() -> None:
    """Zarządzanie procesami."""


@proc.command("list")
@click.option("limit", "--limit", type=int, default=200)
def proc_list(limit: int) -> None:
    click.echo(list_processes(limit=limit))


@proc.command("kill")
@click.option("pid", "--pid", type=int, required=True)
@click.option("sig", "--sig", default="TERM", help="TERM|KILL|INT|HUP")
def proc_kill(pid: int, sig: str) -> None:
    kill_pid(pid, sig=sig)


@app.group()
def net() -> None:
    """Operacje sieciowe."""


@net.command("get")
@click.option("url", "--url", required=True)
@click.option("dest", "--dest", required=True)
@click.option("ua", "--user-agent", default=None)
def net_get(url: str, dest: str, ua: str | None) -> None:
    download(url, dest, user_agent=ua)


@app.group()
def archive() -> None:
    """Operacje na archiwach ZIP."""


@archive.command("zip")
@click.option("src", "--src", required=True)
@click.option("dst", "--dst", required=True)
def archive_zip(src: str, dst: str) -> None:
    zip_dir(src, dst)


@archive.command("unzip")
@click.option("src", "--src", required=True)
@click.option("dst", "--dst", required=True)
def archive_unzip(src: str, dst: str) -> None:
    unzip_file(src, dst)