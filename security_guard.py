#!/usr/bin/env python3
"""
🛡️ Security Guard - Lightweight intrusion/secrets monitoring (stdlib only)
- One-off scan or continuous monitoring
- Tracks listening ports, high-CPU processes, and secrets in files
- Writes alerts to security_alerts.log and stdout
"""
import os
import re
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

ALERT_LOG = Path("security_alerts.log")
ROOT = Path(os.environ.get("SECURITY_GUARD_ROOT", "/workspace")).resolve()

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),                    # AWS Access Key
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"-----BEGIN (RSA|EC|DSA) PRIVATE KEY-----"),
    re.compile(r"(?i)password\s*[:=]\s*['\"]?.{6,}"),
]

SAFE_IGNORE_DIRS = {".git", "__pycache__", "node_modules", "venv", ".venv"}
SAFE_IGNORE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".zip", ".gz", ".tar", ".ico", ".pdf"}


def log_alert(level: str, message: str, data: Optional[Dict[str, Any]] = None):
    entry = {
        "ts": int(time.time()),
        "level": level,
        "message": message,
        "data": data or {},
    }
    with ALERT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[{level}] {message}")


def run_cmd(cmd: List[str], timeout: int = 5) -> Tuple[int, str, str]:
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        return 124, out, err
    return proc.returncode, out, err


def list_listening_ports() -> List[str]:
    # Try 'ss', fallback to 'netstat'
    code, out, _ = run_cmd(["ss", "-tuln"], timeout=5)
    if code != 0:
        code, out, _ = run_cmd(["netstat", "-tuln"], timeout=5)
        if code != 0:
            return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def list_top_processes(limit: int = 10) -> List[Dict[str, Any]]:
    code, out, _ = run_cmd(["ps", "-eo", "pid,ppid,comm,pcpu,pmem", "--sort=-pcpu"], timeout=5)
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


def scan_secrets(root: Path, max_files: int = 500) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # prune dirs
        dirnames[:] = [d for d in dirnames if d not in SAFE_IGNORE_DIRS]
        for filename in filenames:
            if count >= max_files:
                return findings
            count += 1
            p = Path(dirpath) / filename
            if p.suffix.lower() in SAFE_IGNORE_EXTS:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for pat in SECRET_PATTERNS:
                m = pat.search(text)
                if m:
                    findings.append({"file": str(p), "match": pat.pattern})
                    break
    return findings


def one_off_scan(threshold_cpu: float = 80.0):
    ports = list_listening_ports()
    if len(ports) > 0:
        log_alert("INFO", f"Listening ports detected: {len(ports)}")
    procs = list_top_processes()
    hot = [p for p in procs if p["cpu"] >= threshold_cpu]
    if hot:
        for p in hot:
            log_alert("WARN", f"High CPU process: pid={p['pid']} cpu={p['cpu']} cmd={p['command']}")
    secrets = scan_secrets(ROOT)
    if secrets:
        for s in secrets:
            log_alert("ALERT", "Secret-like pattern detected", s)
    if not (hot or secrets):
        log_alert("OK", "No anomalies detected")


def monitor(interval: int = 30, threshold_cpu: float = 80.0):
    prev_ports = set(list_listening_ports())
    log_alert("INFO", f"Security monitor started (root={ROOT})")
    while True:
        try:
            time.sleep(interval)
            # Ports diff
            ports = set(list_listening_ports())
            opened = ports - prev_ports
            closed = prev_ports - ports
            if opened:
                log_alert("WARN", f"New listening ports: {len(opened)}", {"opened": list(opened)[:5]})
            if closed:
                log_alert("INFO", f"Closed ports: {len(closed)}")
            prev_ports = ports
            # CPU spike
            hot = [p for p in list_top_processes() if p["cpu"] >= threshold_cpu]
            for p in hot:
                log_alert("WARN", f"CPU spike pid={p['pid']} {p['cpu']}%", p)
            # Periodic secrets scan (sampled)
            if int(time.time()) % (interval * 4) < interval:
                secrets = scan_secrets(ROOT, max_files=200)
                for s in secrets:
                    log_alert("ALERT", "Secret-like pattern detected", s)
        except KeyboardInterrupt:
            log_alert("INFO", "Security monitor stopped by user")
            break
        except Exception as e:
            log_alert("ERROR", f"Monitor error: {e}")


def main(argv: Optional[List[str]] = None):
    global ROOT
    import argparse
    parser = argparse.ArgumentParser(description="Security Guard")
    parser.add_argument("mode", choices=["once", "monitor"]) 
    parser.add_argument("--root", dest="root", default=str(ROOT), help="Root to scan (default /workspace)")
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--cpu", type=float, default=80.0, help="CPU threshold for alerts")
    args = parser.parse_args(argv)

    ROOT = Path(args.root).resolve()

    if args.mode == "once":
        one_off_scan(threshold_cpu=args.cpu)
    else:
        monitor(interval=args.interval, threshold_cpu=args.cpu)

if __name__ == "__main__":
    main()