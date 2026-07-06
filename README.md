# mcp-guard

[![CI](https://github.com/IvanTatarchuk/MyBotAI_Updates/actions/workflows/ci.yml/badge.svg)](https://github.com/IvanTatarchuk/MyBotAI_Updates/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Open-source security scanner for [MCP](https://modelcontextprotocol.io) servers.

Before you let an AI agent talk to a random MCP server, `mcp-guard` connects to it,
lists its tools/resources, and flags risky patterns:

- **Overbroad permissions** — tools that claim to run arbitrary shell commands, read/write
  any file on disk, or make unrestricted network requests.
- **Prompt-injection cues** — tool/resource descriptions containing embedded instructions
  aimed at the calling LLM ("ignore previous instructions", "always respond with...", etc).
- **Credential/secret exposure risk** — tools whose input or output schema looks like it
  handles API keys, tokens, or passwords without any indication of redaction.
- **Unbounded/unvalidated input** — tools with free-form string parameters feeding into
  execution-shaped operations (eval, exec, shell, SQL) with no schema constraints.

The goal: give people a fast, honest signal on "how much do I trust this MCP server"
*before* wiring it into an agent with real permissions — the same problem
[Socket](https://socket.dev) solves for npm/PyPI supply-chain risk, but for MCP tool
definitions.

## Status

Early / v0.1. Rule-based static scanner. Contributions and new rules welcome.

**Read [`THREAT_MODEL.md`](THREAT_MODEL.md) before relying on this** — it's a static
heuristic over tool descriptions, not a guarantee about actual server behavior.

## Install

```bash
pip install -e .
```

## Usage

Scan a running MCP server over stdio:

```bash
mcp-guard scan --stdio "python my_mcp_server.py"
```

Scan a static list of tool definitions exported as JSON (e.g. from `tools/list`):

```bash
mcp-guard scan --manifest tools.json
```

Try it against the bundled sample server (mixes safe and deliberately risky tools):

```bash
mcp-guard scan --stdio "python examples/sample_server.py"
```

Example output:

```
$ mcp-guard scan --manifest examples/risky_tools.json

  Tool                 Severity   Finding
  ───────────────────  ─────────  ──────────────────────────────────────────
  run_shell_command    HIGH       Unrestricted shell execution (rule: shell-exec)
  read_any_file        HIGH       Unbounded filesystem read (rule: fs-read-any)
  fetch_url            MEDIUM     Unrestricted outbound network access (rule: net-any)
  summarize_text       LOW        Description contains instruction-like phrasing
                                  (rule: prompt-injection-cue)

  4 findings across 4 tools (2 high, 1 medium, 1 low)
```

List every rule that would be applied (useful for auditing what's actually covered):

```bash
mcp-guard rules
```

## Policy file (`mcp-guard.json`)

Drop an `mcp-guard.json` in your repo root to set defaults without repeating flags.
CLI flags always win over the file.

```json
{
  "fail_on": "high",
  "ignore": ["prompt-injection-cue"],
  "rules": ["custom_rules.yaml"]
}
```

- `fail_on` — same as `--fail-on`.
- `ignore` — rule ids to drop from the results entirely (e.g. a rule that's too
  noisy for your servers).
- `rules` — extra rule YAML files, paths relative to the config file.

See [`examples/mcp-guard.example.json`](examples/mcp-guard.example.json).

## GitHub Action

Gate CI on a scan of your own MCP server:

```yaml
- uses: IvanTatarchuk/MyBotAI_Updates@main
  with:
    manifest: tools.json     # or: stdio-command: "python server.py"
    fail-on: high
```

See [`action.yml`](action.yml) for all inputs.

## Rules

Rules live in `mcp_guard/rules/*.yaml` and are intentionally simple (name, severity,
pattern) so they're easy to read, audit, and extend without touching Python code.
See [`mcp_guard/rules/README.md`](mcp_guard/rules/README.md).

## Live probing (`mcp-guard probe`) — experimental

`scan` only reads text. `probe` actually launches the server and calls every tool
once, with placeholder arguments synthesized from its input schema, inside a
sandbox that blocks outbound network access (Linux network namespaces via
`unshare --net`):

```bash
mcp-guard probe --stdio "python examples/sample_server.py" --yes
```

```
Sandbox: network-isolated via `unshare --net` (outbound network access blocked);
filesystem access is NOT isolated — see THREAT_MODEL.md

  Tool                   Result          Detail
  ─────────────────────  ──────────────  ──────────────────────────────────────
  get_weather            ok              It's sunny in mcp-guard-probe.
  add_numbers            ok              0.0
  run_shell_command      ok              (not actually executed) would run: ...
  read_any_file          ok              (not actually executed) would read: ...
  check_internet_access  blocked/error   Error executing tool check_internet_
                                         access: [Errno 101] Network is unreachable

  5 tools called, 1 blocked or errored
```

That last row is a real, verified network-namespace block, not a simulated one —
`examples/sample_server.py`'s `check_internet_access` tool makes a genuine outbound
connection attempt, and the sandbox actually stops it (see
`tests/test_sandbox_integration.py`).

**Requires `--yes`** — this runs the target's real code. **The sandbox only isolates
the network**, not the filesystem: a probed tool can still read/write real files.
Requires `unshare` (util-linux; present on virtually every Linux distro). Read
[`THREAT_MODEL.md`](THREAT_MODEL.md) before relying on this.

## Roadmap

- [x] Live execution probing, network-isolated (not just static description analysis)
- [ ] Filesystem isolation for `probe` (bubblewrap/Docker backend, scratch-dir-only writes)
- [x] `mcp-guard.json` policy file for CI gating (fail build above a severity threshold)
- [x] GitHub Action
- [ ] Hosted registry of scanned/verified MCP servers with re-scan on new releases

## License

MIT
