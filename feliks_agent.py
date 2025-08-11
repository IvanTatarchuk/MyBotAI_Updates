#!/usr/bin/env python3
"""
FeliksAgent - Orchestrator agent for local automation (safe by default)
- Uses SystemManager and Security Guard
- Can deploy/start the Feliks web portal locally
- Supports bulk invites/tenders, auto-bids, backups, and security scan

IMPORTANT: Destructive/system‑wide actions require --force and an explicit --root path.
"""
from __future__ import annotations
import os
import sys
import json
import csv
import time
import tarfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

# Local modules
from system_manager import SystemManager

ROOT_DEFAULT = Path(os.environ.get("FELIKS_ROOT", "/workspace")).resolve()

class FeliksAgent:
    def __init__(self, allowed_root: Path = ROOT_DEFAULT, allow_destructive: bool = False):
        self.allowed_root = allowed_root.resolve()
        self.allow_destructive = allow_destructive
        self.sm = SystemManager(self.allowed_root, allow_destructive=allow_destructive)

    # ---------- INFO ----------
    def info(self) -> Dict[str, Any]:
        sysinfo = self.sm.get_system_info()
        return {
            "hostname": sysinfo.hostname,
            "os": sysinfo.os,
            "kernel": sysinfo.kernel,
            "python": sysinfo.python,
            "uptime_seconds": sysinfo.uptime_seconds,
            "disk_free_gb": sysinfo.disk_free_gb,
            "root": str(self.allowed_root),
            "allow_destructive": self.allow_destructive,
        }

    # ---------- SECURITY ----------
    def security_scan_once(self) -> Dict[str, Any]:
        code, out, err = self.sm.run_command_readonly(f"python3 security_guard.py once --root {self.allowed_root}")
        return {"code": code, "out": out, "err": err}

    # ---------- BACKUP ----------
    def backup_workspace(self, archive_path: str = "feliks_workspace_backup.tar.gz") -> str:
        if not self.allow_destructive:
            raise PermissionError("Backups require --force to access full filesystem features.")
        archive = (self.allowed_root / archive_path).resolve()
        with tarfile.open(archive, mode="w:gz") as tar:
            tar.add(str(self.allowed_root), arcname=self.allowed_root.name, recursive=True)
        return str(archive)

    # ---------- PORTAL CONTROL ----------
    def start_portal(self, background: bool = True) -> Dict[str, Any]:
        app = self.allowed_root / "web_portal" / "app.py"
        if not app.exists():
            raise FileNotFoundError("web_portal/app.py not found")
        cmd = ["python3", str(app)]
        if background:
            proc = subprocess.Popen(cmd, cwd=str(self.allowed_root))
            return {"pid": proc.pid, "status": "started"}
        else:
            code = subprocess.call(cmd, cwd=str(self.allowed_root))
            return {"code": code}

    def stop_portal(self) -> Dict[str, Any]:
        code, out, err = self.sm._run(["pkill", "-f", "web_portal/app.py"], timeout=3)
        return {"code": code, "out": out, "err": err}

    # ---------- BULK OPS ----------
    def bulk_invite(self, base_url: str, csv_path: str) -> Dict[str, Any]:
        """Send OTP invitations from a CSV (email,role). Safe network call (read-only op)."""
        import urllib.request
        invited, errors = 0, 0
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                payload = json.dumps({"email": row.get("email"), "role": row.get("role", "seller")}).encode()
                req = urllib.request.Request(f"{base_url}/api/auth/request_otp", data=payload, headers={"Content-Type": "application/json"})
                try:
                    with urllib.request.urlopen(req, timeout=10) as r:
                        _ = r.read()
                        invited += 1
                except Exception:
                    errors += 1
        return {"invited": invited, "errors": errors}

    def bulk_create_tenders(self, base_url: str, count: int = 10, profession: str = "Software Developer") -> Dict[str, Any]:
        import urllib.request
        created, errors = 0, 0
        for i in range(count):
            payload = {
                "title": f"Projekt #{int(time.time())}-{i}",
                "profession": profession,
                "budget": 3000 + i,
                "deadline": "2025-12-31",
                "contact_email": f"client{i}@example.com",
                "description": "Auto utworzony przetarg",
                "consent": True,
            }
            req = urllib.request.Request(f"{base_url}/api/tenders", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=10) as r:
                    _ = r.read()
                    created += 1
            except Exception:
                errors += 1
        return {"created": created, "errors": errors}

    def auto_bid_all(self, base_url: str, professions: Optional[List[str]] = None) -> Dict[str, Any]:
        import urllib.request
        professions = professions or ["Software Developer", "Designer", "Engineer", "Marketer", "Data Scientist"]
        # pull tenders
        tenders = []
        try:
            with urllib.request.urlopen(f"{base_url}/api/tenders", timeout=10) as r:
                store = json.loads(r.read().decode())
                tenders = store.get("tenders", [])
        except Exception:
            pass
        placed = 0
        for t in tenders:
            for p in professions:
                payload = json.dumps({"tender_id": t.get("id"), "profession": p}).encode()
                req = urllib.request.Request(f"{base_url}/api/auto_bid", data=payload, headers={"Content-Type": "application/json"})
                try:
                    with urllib.request.urlopen(req, timeout=10) as r:
                        _ = r.read()
                        placed += 1
                except Exception:
                    continue
        return {"auto_bids": placed}


def main(argv: Optional[List[str]] = None):
    import argparse
    parser = argparse.ArgumentParser(description="FeliksAgent — local automation agent (safe by default)")
    parser.add_argument("command", choices=[
        "info", "scan", "backup", "start", "stop", "invite", "seed_tenders", "auto_bid"
    ])
    parser.add_argument("--root", dest="root", default=str(ROOT_DEFAULT), help="Allowed root path (default /workspace)")
    parser.add_argument("--force", action="store_true", help="Enable destructive/system actions")
    parser.add_argument("--base", dest="base", default="http://localhost:8000", help="Base URL of portal")
    parser.add_argument("--csv", dest="csv", help="CSV path for invites")
    parser.add_argument("--count", dest="count", type=int, default=10, help="How many tenders to create")
    args = parser.parse_args(argv)

    agent = FeliksAgent(Path(args.root), allow_destructive=args.force)

    if args.command == "info":
        print(json.dumps(agent.info(), indent=2))
    elif args.command == "scan":
        print(json.dumps(agent.security_scan_once(), indent=2))
    elif args.command == "backup":
        print(json.dumps({"archive": agent.backup_workspace()}, indent=2))
    elif args.command == "start":
        print(json.dumps(agent.start_portal(background=True), indent=2))
    elif args.command == "stop":
        print(json.dumps(agent.stop_portal(), indent=2))
    elif args.command == "invite":
        if not args.csv:
            print("--csv required", file=sys.stderr); sys.exit(2)
        print(json.dumps(agent.bulk_invite(args.base, args.csv), indent=2))
    elif args.command == "seed_tenders":
        print(json.dumps(agent.bulk_create_tenders(args.base, count=args.count), indent=2))
    elif args.command == "auto_bid":
        print(json.dumps(agent.auto_bid_all(args.base), indent=2))

if __name__ == "__main__":
    main()