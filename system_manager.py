#!/usr/bin/env python3
"""
🖥️ System Manager - Safe local computer management utilities (stdlib only)
- Read-only by default
- Destructive operations require explicit allow flag
- Path operations constrained to an allowed root directory
"""
from __future__ import annotations
import os
import sys
import platform
import socket
import time
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

SAFE_DEFAULT_ROOT = Path(os.environ.get("SYSTEM_MANAGER_ROOT", "/workspace")).resolve()

@dataclass
class SystemInfo:
    hostname: str
    os: str
    kernel: str
    python: str
    uptime_seconds: float
    load_avg: Tuple[float, float, float]
    cpu_count: int
    mem_total_mb: float
    mem_free_mb: float
    disk_total_gb: float
    disk_used_gb: float
    disk_free_gb: float

class SystemManager:
    def __init__(self, allowed_root: Path = SAFE_DEFAULT_ROOT, allow_destructive: bool = False):
        self.allowed_root = allowed_root.resolve()
        self.allow_destructive = allow_destructive

    # ---------- Helpers ----------
    def _assert_within_root(self, path: Path):
        resolved = path.resolve()
        if not str(resolved).startswith(str(self.allowed_root)):
            raise PermissionError(f"Path {resolved} is outside allowed root {self.allowed_root}")

    def _run(self, cmd: List[str], timeout: int = 10) -> Tuple[int, str, str]:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
            return 124, out, err
        return proc.returncode, out, err

    # ---------- Read-only operations ----------
    def get_system_info(self) -> SystemInfo:
        hostname = socket.gethostname()
        os_name = platform.platform()
        kernel = platform.release()
        python_ver = sys.version.split(" ")[0]
        # uptime
        uptime_seconds = 0.0
        try:
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.read().split()[0])
        except Exception:
            pass
        # load average
        try:
            load_avg = os.getloadavg()
        except Exception:
            load_avg = (0.0, 0.0, 0.0)
        cpu_count = os.cpu_count() or 1
        # memory
        mem_total_kb = 0.0
        mem_free_kb = 0.0
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        mem_total_kb = float(line.split()[1])
                    if line.startswith("MemAvailable:"):
                        mem_free_kb = float(line.split()[1])
        except Exception:
            pass
        # disk
        usage = shutil.disk_usage(str(self.allowed_root))
        return SystemInfo(
            hostname=hostname,
            os=os_name,
            kernel=kernel,
            python=python_ver,
            uptime_seconds=uptime_seconds,
            load_avg=load_avg,
            cpu_count=cpu_count,
            mem_total_mb=mem_total_kb / 1024.0,
            mem_free_mb=mem_free_kb / 1024.0,
            disk_total_gb=usage.total / (1024**3),
            disk_used_gb=usage.used / (1024**3),
            disk_free_gb=usage.free / (1024**3),
        )

    def list_processes(self, limit: int = 20) -> List[Dict[str, Any]]:
        code, out, _ = self._run(["ps", "-eo", "pid,ppid,comm,pcpu,pmem", "--sort=-pcpu"], timeout=5)
        procs: List[Dict[str, Any]] = []
        if code == 0:
            lines = out.strip().splitlines()[1:limit+1]
            for line in lines:
                parts = line.split(None, 4)
                if len(parts) == 5:
                    pid, ppid, comm, pcpu, pmem = parts
                    procs.append({
                        "pid": int(pid),
                        "ppid": int(ppid),
                        "command": comm,
                        "cpu": float(pcpu),
                        "mem": float(pmem),
                    })
        return procs

    def list_dir(self, path: str = ".") -> List[str]:
        p = (self.allowed_root / path).resolve()
        self._assert_within_root(p)
        if not p.exists():
            return []
        return [entry.name for entry in p.iterdir()]

    def read_file(self, path: str, max_bytes: int = 65536) -> str:
        p = (self.allowed_root / path).resolve()
        self._assert_within_root(p)
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_bytes)

    def run_command_readonly(self, command: str, timeout: int = 10) -> Tuple[int, str, str]:
        """Run a safe readonly command (e.g., 'ls', 'cat', 'uptime')."""
        safe_prefixes = (
            "ls", "cat", "head", "tail", "uptime", "whoami", "id", "uname", "df", "free", "date"
        )
        if not command.strip().startswith(safe_prefixes):
            raise PermissionError("Only read-only commands allowed in run_command_readonly")
        return self._run(command.split(), timeout=timeout)

    def network_overview(self) -> Dict[str, Any]:
        _, ss_out, _ = self._run(["ss", "-tuln"], timeout=5)
        _, ip_out, _ = self._run(["ip", "addr"], timeout=5)
        return {"listening": ss_out.strip(), "interfaces": ip_out.strip()}

    # ---------- Guarded write operations ----------
    def create_file(self, path: str, content: str = "") -> str:
        if not self.allow_destructive:
            raise PermissionError("Destructive operations are disabled. Enable allow_destructive to proceed.")
        p = (self.allowed_root / path).resolve()
        self._assert_within_root(p)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return str(p)

    def delete_path(self, path: str) -> bool:
        if not self.allow_destructive:
            raise PermissionError("Destructive operations are disabled. Enable allow_destructive to proceed.")
        p = (self.allowed_root / path).resolve()
        self._assert_within_root(p)
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
        return True

    def move_path(self, src: str, dst: str) -> str:
        if not self.allow_destructive:
            raise PermissionError("Destructive operations are disabled. Enable allow_destructive to proceed.")
        s = (self.allowed_root / src).resolve()
        d = (self.allowed_root / dst).resolve()
        self._assert_within_root(s)
        self._assert_within_root(d)
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(d))
        return str(d)

    def kill_process(self, pid: int, force: bool = False) -> bool:
        if not self.allow_destructive:
            raise PermissionError("Destructive operations are disabled. Enable allow_destructive to proceed.")
        sig = "-9" if force else "-15"
        code, _, err = self._run(["kill", sig, str(pid)], timeout=5)
        if code != 0:
            raise RuntimeError(f"Failed to kill pid {pid}: {err}")
        return True

    def schedule_task(self, command: str, delay_seconds: int = 5) -> int:
        if not self.allow_destructive:
            raise PermissionError("Destructive operations are disabled. Enable allow_destructive to proceed.")
        # Simple scheduler using 'sh -c' and sleep in background
        shell_cmd = f"(sleep {delay_seconds}; {command}) &"
        code, _, err = self._run(["sh", "-c", shell_cmd], timeout=2)
        if code != 0:
            raise RuntimeError(f"Failed to schedule task: {err}")
        return code

# ---------------- CLI ----------------

def _fmt_bytes(seconds: float) -> str:
    days, rem = divmod(int(seconds), 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m {secs}s"

def main(argv: Optional[List[str]] = None):
    import argparse
    parser = argparse.ArgumentParser(description="Safe System Manager")
    parser.add_argument("command", choices=[
        "info", "ps", "ls", "cat", "net", "mkfile", "rm", "mv", "kill", "sched"
    ])
    parser.add_argument("path", nargs="?", help="Path or target, depending on command")
    parser.add_argument("extra", nargs="?", help="Extra arg (e.g., destination path or pid)")
    parser.add_argument("--root", dest="root", default=str(SAFE_DEFAULT_ROOT), help="Allowed root path")
    parser.add_argument("--force", action="store_true", help="Enable destructive operations")
    args = parser.parse_args(argv)

    mgr = SystemManager(Path(args.root), allow_destructive=args.force)

    if args.command == "info":
        si = mgr.get_system_info()
        print({
            "hostname": si.hostname,
            "os": si.os,
            "kernel": si.kernel,
            "python": si.python,
            "uptime": _fmt_bytes(si.uptime_seconds),
            "load": si.load_avg,
            "cpu_count": si.cpu_count,
            "mem_total_mb": round(si.mem_total_mb, 1),
            "mem_free_mb": round(si.mem_free_mb, 1),
            "disk_total_gb": round(si.disk_total_gb, 2),
            "disk_used_gb": round(si.disk_used_gb, 2),
            "disk_free_gb": round(si.disk_free_gb, 2),
        })
    elif args.command == "ps":
        print(mgr.list_processes())
    elif args.command == "ls":
        path = args.path or "."
        print(mgr.list_dir(path))
    elif args.command == "cat":
        if not args.path:
            print("Missing path", file=sys.stderr); sys.exit(2)
        print(mgr.read_file(args.path))
    elif args.command == "net":
        print(mgr.network_overview())
    elif args.command == "mkfile":
        if not args.path:
            print("Missing path", file=sys.stderr); sys.exit(2)
        content = args.extra or ""
        print(mgr.create_file(args.path, content))
    elif args.command == "rm":
        if not args.path:
            print("Missing path", file=sys.stderr); sys.exit(2)
        print(mgr.delete_path(args.path))
    elif args.command == "mv":
        if not (args.path and args.extra):
            print("Missing src/dst", file=sys.stderr); sys.exit(2)
        print(mgr.move_path(args.path, args.extra))
    elif args.command == "kill":
        if not args.path:
            print("Missing pid", file=sys.stderr); sys.exit(2)
        print(mgr.kill_process(int(args.path), force=bool(args.extra)))
    elif args.command == "sched":
        if not args.path:
            print("Missing shell command", file=sys.stderr); sys.exit(2)
        delay = int(args.extra or 5)
        print(mgr.schedule_task(args.path, delay_seconds=delay))

if __name__ == "__main__":
    main()