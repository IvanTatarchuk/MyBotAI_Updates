import os
import signal
import subprocess
from typing import Optional

from rich.console import Console

console = Console()


def list_processes(limit: int = 200) -> str:
    try:
        out = subprocess.check_output(
            ["bash", "-lc", f"ps -eo pid,ppid,stat,cmd --sort=pid | head -n {limit}"],
            text=True,
        )
        return out
    except Exception as exc:
        return f"Nie udało się pobrać listy procesów: {exc}"


def kill_pid(pid: int, sig: str = "TERM") -> None:
    sig_map = {
        "TERM": signal.SIGTERM,
        "KILL": signal.SIGKILL,
        "INT": signal.SIGINT,
        "HUP": signal.SIGHUP,
    }
    signum = sig_map.get(sig.upper(), signal.SIGTERM)
    os.kill(pid, signum)
    console.print(f"[green]Wysłano sygnał {sig} do PID {pid}[/green]")