from __future__ import annotations

import shutil


class SandboxUnavailable(RuntimeError):
    """Raised when no sandboxing mechanism is available on this host."""


SANDBOX_DESCRIPTION = (
    "network-isolated (`unshare --net`, no outbound access) and filesystem-isolated "
    "(rootfs + every submount bind-remounted read-only, tmpfs scratch at /tmp) — "
    "see THREAT_MODEL.md for exact scope"
)

# Runs inside the new mount namespace, before exec'ing the real command:
#   1. break mount propagation to the host (so nothing below can leak back)
#   2. bind-mount / onto itself so it becomes remountable
#   3. remount that bind as read-only — the entire real filesystem, read-only
#   4. give the process a writable tmpfs scratch space at /tmp
#   5. remount every *other* real mountpoint read-only too (a non-recursive bind
#      of / doesn't cover separately-mounted filesystems — a second disk, a
#      Docker volume, a network share — those would otherwise stay writable).
#      Parses /proc/self/mountinfo via the " - " separator rather than a fixed
#      field number, since the field before it is a variable-length list of
#      optional tags (see `man 5 proc_pid_mountinfo`).
#   6. exec the real command, replacing this shell (no extra process, stdio untouched)
_FS_ISOLATION_SCRIPT = r"""
set -e
mount --make-rprivate /
mount --bind / /
mount -o remount,bind,ro /
mount -t tmpfs tmpfs /tmp
awk -F' - ' '{split($1,a," "); split($2,b," "); print a[5], b[1]}' /proc/self/mountinfo |
while read -r mp fstype; do
  case "$fstype" in
    proc|sysfs|devpts|cgroup2|cgroup|devtmpfs|mqueue|tracefs|debugfs|securityfs) continue ;;
    pstore|bpf|autofs|hugetlbfs|fusectl|configfs|binfmt_misc) continue ;;
  esac
  [ "$mp" = "/tmp" ] && continue
  mount -o remount,bind,ro "$mp" 2>/dev/null || true
done
exec "$@"
"""


def build_sandboxed_command(command: list[str]) -> list[str]:
    """Wrap `command` so it runs network-isolated and with a read-only filesystem.

    Built entirely on `unshare` (util-linux) — no Docker or bubblewrap dependency:

    - `--net`: fresh, empty network namespace. No outbound access at all.
    - `--mount` + a bind-remount of `/` (and every other mountpoint) as
      read-only: the process sees the real filesystem (so it behaves like it
      would in production) but any write outside of `/tmp` fails at the kernel
      level — including on separately-mounted filesystems, not just whatever's
      mounted at `/`.
    - `/tmp` is a fresh tmpfs: the process gets real, writable scratch space
      that vanishes with the sandboxed process.
    - `--pid` + `--mount-proc`: separate process namespace, so the sandboxed
      process can't see or signal unrelated processes on the host.

    Raises SandboxUnavailable if `unshare` isn't on PATH — probing must refuse
    rather than silently fall back to running the command unsandboxed.
    """
    if shutil.which("unshare") is None:
        raise SandboxUnavailable(
            "`unshare` (from util-linux) was not found on PATH. It's required to sandbox "
            "the server before probing. Install util-linux, or don't use `mcp-guard probe`."
        )

    return [
        "unshare",
        "--mount",
        "--net",
        "--pid",
        "--mount-proc",
        "--fork",
        "--",
        "sh",
        "-c",
        _FS_ISOLATION_SCRIPT,
        "sh",
    ] + command


def describe_sandbox() -> str:
    return SANDBOX_DESCRIPTION
