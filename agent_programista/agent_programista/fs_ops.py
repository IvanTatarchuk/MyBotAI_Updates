import shutil
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def read_text(path: str, head: Optional[int] = None, tail: Optional[int] = None) -> str:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    lines = text.splitlines()
    if head is not None:
        lines = lines[:head]
    if tail is not None:
        lines = lines[-tail:]
    return "\n".join(lines)


def write_text(path: str, content: str, append: bool = False) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with p.open(mode, encoding="utf-8") as f:
        f.write(content)


def copy_path(src: str, dst: str) -> None:
    s, d = Path(src), Path(dst)
    d.parent.mkdir(parents=True, exist_ok=True)
    if s.is_dir():
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(s, d)
    else:
        shutil.copy2(s, d)


def move_path(src: str, dst: str) -> None:
    s, d = Path(src), Path(dst)
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(s), str(d))


def delete_path(path: str) -> None:
    p = Path(path)
    if p.is_dir():
        shutil.rmtree(p)
    elif p.exists():
        p.unlink()


def mkdir_p(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def chmod_path(path: str, mode: str) -> None:
    p = Path(path)
    p.chmod(int(mode, 8))