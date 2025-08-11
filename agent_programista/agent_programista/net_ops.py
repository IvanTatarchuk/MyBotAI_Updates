from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request

from rich.console import Console

console = Console()


def download(url: str, dest_path: str, user_agent: Optional[str] = None) -> None:
    headers = {"User-Agent": user_agent or "agent-programista/0.1"}
    req = Request(url, headers=headers)
    with urlopen(req) as resp:  # nosec - trusted by user input, minimal agent tool
        data = resp.read()
    p = Path(dest_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    console.print(f"[green]Pobrano:[/green] {url} -> {dest_path} ({len(data)} B)")