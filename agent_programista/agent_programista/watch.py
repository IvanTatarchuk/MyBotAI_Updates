from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from rich.console import Console

console = Console()

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except Exception:  # pragma: no cover
    FileSystemEventHandler = object  # type: ignore
    Observer = None  # type: ignore


class DebouncedHandler(FileSystemEventHandler):
    def __init__(self, on_change: Callable[[], None], debounce_seconds: float = 0.5) -> None:
        self.on_change = on_change
        self.debounce_seconds = debounce_seconds
        self._last = 0.0

    def on_any_event(self, event):  # type: ignore[no-untyped-def]
        now = time.time()
        if now - self._last >= self.debounce_seconds:
            self._last = now
            self.on_change()


def watch_and_run(path: str, run: Callable[[], None]) -> None:
    if Observer is None:
        console.print("[yellow]watchdog nie jest zainstalowany. Zainstaluj, aby użyć trybu watch.[/yellow]")
        return
    observer = Observer()
    handler = DebouncedHandler(on_change=run)
    observer.schedule(handler, path, recursive=True)
    observer.start()
    console.print(f"[green]Watching:[/green] {path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()