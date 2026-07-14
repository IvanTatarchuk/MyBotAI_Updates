# MCP Security Observatory

A recurring, reproducible security scan of **real, public MCP servers**, powered by
`mcp-guard`'s own public rule set. The output is the repo's data drop:

- [`OBSERVATORY.md`](../OBSERVATORY.md) — aggregate stats + per-server table.
- [`docs/index.html`](../docs/index.html) — a static leaderboard (served via GitHub Pages).

The whole point is that it's **honest and reproducible**: every verdict is something
`mcp-guard scan` produces on its own, and anyone can re-run the exact pipeline.

## How it works

| File | Role |
|---|---|
| `servers.yaml` | The catalogue — one entry per public server (package, ecosystem, stdio launch command). |
| `scan.py` | Enumerates each server's tools via `mcp_guard.client` and applies `mcp_guard.rules_engine`, writing `results.json`. |
| `results.json` | Machine-readable output: per-server tool count, resolved version, and findings. Committed so the data is auditable. |
| `generate.py` | Renders `results.json` into `OBSERVATORY.md` and `docs/index.html`. No hand-written verdicts. |

## Reproduce a scan

```bash
pip install -e .                 # from the repo root

# Install the servers you want to scan (see the `install:` field in servers.yaml).
# npm servers into a scratch dir, pip servers into the environment:
mkdir -p /tmp/mcpscan && cd /tmp/mcpscan && npm init -y
npm i @modelcontextprotocol/server-filesystem mcp-server-commands   # …etc
pip install mcp-server-fetch mcp-server-git

# Run the scan from where the npm packages are installed (so ./node_modules resolves):
python /path/to/repo/observatory/scan.py \
    --servers /path/to/repo/observatory/servers.yaml \
    --out     /path/to/repo/observatory/results.json

# Render the report + leaderboard:
python /path/to/repo/observatory/generate.py
```

## Adding a server

1. Append an entry to `servers.yaml` (see the existing ones for the shape).
2. Install it and re-run `scan.py` + `generate.py`.
3. Open a PR with the updated `results.json`, `OBSERVATORY.md`, and `docs/index.html`.

**Not currently scannable unattended:** servers that refuse to list their tools without a
live API credential (Slack, GitLab, Google Maps, Brave Search), and servers that write
non-JSON-RPC output to stdout and break a strict MCP stdio client (e.g.
`@wonderwhy-er/desktop-commander`). These are noted inline in `servers.yaml`.

## Caveat

A clean result is **not** a safety guarantee. `mcp-guard scan` reads advertised tool
metadata; a server can behave differently from what it advertises. See
[`THREAT_MODEL.md`](../THREAT_MODEL.md), and use `mcp-guard probe` for sandboxed dynamic
verification.
