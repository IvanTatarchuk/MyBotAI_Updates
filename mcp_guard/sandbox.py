from __future__ import annotations

import shutil


class SandboxUnavailable(RuntimeError):
    """Raised when no sandboxing mechanism is available on this host."""


SANDBOX_DESCRIPTION = (
    "network-isolated via `unshare --net` (outbound network access blocked); "
    "filesystem access is NOT isolated — see THREAT_MODEL.md"
)


def build_sandboxed_command(command: list[str]) -> list[str]:
    """Wrap `command` so the process it launches has no outbound network access.

    Uses Linux network namespaces (`unshare --net`), which is the one isolation
    primitive we can rely on being available (util-linux) without adding a
    dependency on Docker or bubblewrap. This does NOT isolate the filesystem —
    a probed tool can still read and write real files. Callers must treat probe
    results accordingly (see THREAT_MODEL.md).

    Raises SandboxUnavailable if `unshare` isn't on PATH, or isn't usable in
    this environment — probing must refuse rather than silently fall back to
    running the command unsandboxed.
    """
    if shutil.which("unshare") is None:
        raise SandboxUnavailable(
            "`unshare` (from util-linux) was not found on PATH. It's required to isolate "
            "network access before probing. Install util-linux, or don't use `mcp-guard probe`."
        )

    return ["unshare", "--net", "--pid", "--mount-proc", "--fork", "--"] + command


def describe_sandbox() -> str:
    return SANDBOX_DESCRIPTION
