import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel

from .logger import get_logger

console = Console()
logger = get_logger()


@dataclass
class PlanStep:
    kind: str  # shell | edit | search | test | git_commit
    description: str
    command: Optional[str] = None
    payload: Optional[dict] = None


def execute_shell_command(command: str, cwd: Optional[str] = None, timeout_seconds: Optional[int] = None) -> int:
    safe_cwd = cwd or os.getcwd()
    console.print(Panel.fit(f"$ {command}", title="Shell"))
    try:
        proc = subprocess.run(
            command,
            cwd=safe_cwd,
            shell=True,
            check=False,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
        if proc.stdout:
            console.print(proc.stdout)
            logger.info(proc.stdout)
        if proc.stderr:
            console.print(proc.stderr)
            logger.warning(proc.stderr)
        logger.info("command '%s' exited with %s", command, proc.returncode)
        return proc.returncode
    except subprocess.TimeoutExpired:
        console.print("[red]Przekroczono limit czasu komendy.[/red]")
        logger.error("command '%s' timed out after %ss", command, timeout_seconds)
        return 124
    except Exception as exc:
        console.print(f"[red]Błąd wykonania komendy:[/red] {exc}")
        logger.exception("command '%s' failed", command)
        return 1


def execute_plan(plan_steps: List[PlanStep], repo_root: str) -> None:
    for idx, step in enumerate(plan_steps, start=1):
        console.rule(f"Krok {idx}: {step.kind}")

        if step.kind == "shell" and step.command:
            rc = execute_shell_command(step.command, cwd=repo_root)
            if rc != 0:
                console.print(f"[red]Komenda zakończyła się kodem {rc}. Przerywam plan.[/red]")
                break

        elif step.kind == "test" and step.command:
            rc = execute_shell_command(step.command, cwd=repo_root)
            if rc != 0:
                console.print(f"[yellow]Testy nie przeszły (kod {rc}). Kontynuuję, ale rozważ poprawki.[/yellow]")

        elif step.kind == "edit" and step.payload:
            from .editor import apply_edit_spec

            apply_edit_spec(step.payload, repo_root)

        elif step.kind == "search" and step.payload:
            from .utils import ripgrep_search

            query = step.payload.get("query", "")
            ripgrep_search(query, repo_root)

        elif step.kind == "git_commit" and step.payload:
            from .git_ops import commit_all_changes

            message = step.payload.get("message", "agent: commit")
            commit_all_changes(repo_root, message)

        else:
            console.print(f"[yellow]Nieobsługiwany krok: {step}[/yellow]")