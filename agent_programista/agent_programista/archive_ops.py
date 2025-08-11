import shutil
import zipfile
from pathlib import Path

from rich.console import Console

console = Console()


def zip_dir(src_dir: str, dest_zip: str) -> None:
    src = Path(src_dir)
    dest = Path(dest_zip)
    dest.parent.mkdir(parents=True, exist_ok=True)
    # shutil.make_archive expects filename without extension
    base = dest.with_suffix("")
    out = shutil.make_archive(str(base), "zip", root_dir=str(src))
    # Ensure final name matches dest_zip
    Path(out).replace(dest)
    console.print(f"[green]Spakowano:[/green] {src} -> {dest}")


def unzip_file(src_zip: str, dest_dir: str) -> None:
    src = Path(src_zip)
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src, "r") as zf:
        zf.extractall(dest)
    console.print(f"[green]Rozpakowano:[/green] {src} -> {dest}")