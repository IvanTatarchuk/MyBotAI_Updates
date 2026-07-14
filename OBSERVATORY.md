# MCP Security Observatory

A recurring, reproducible scan of **real, public MCP servers** with [`mcp-guard`](README.md). Every row below is produced by the tool's public rule set — no hand-written verdicts. Regenerate with `observatory/scan.py` + `observatory/generate.py`.

**Last scan:** 2026-07-14 · **Servers scanned:** 17 · **Tools inspected:** 166

## Headline

- **13 of 17 servers scanned clean.** That's the point — a scanner that flags everything is useless. Most well-maintained servers scope their tools narrowly and say so.
- **4 servers had at least one finding** (3 high, 2 medium, 0 low).
- **An _official_ reference server has a finding:** `mcp-server-fetch`. Provenance is not safety.

## Results

| Server | Source | Tools | Worst | Findings |
|---|---|---:|---|---|
| **mcp-server-fetch** `2026.7.10` | official | 1 | HIGH | `fetch` → net-any (medium), `fetch` → llm-capability-override (high) |
| **mcp-server-commands** `0.8.2` | community | 1 | HIGH | `run_process` → shell-exec (high) |
| **mcp-shell** `0.1.3` | community | 1 | HIGH | `run_command` → shell-exec (high) |
| **mcp-server-kubernetes** `4.0.2` | community | 23 | MEDIUM | `kubectl_create` → secret-handling (medium) |
| **code-runner** | community | 1 | — | clean |
| **cyanheads-git-mcp-server** | community | 28 | — | clean |
| **mcp-server-git** `2026.7.10` | official | 12 | — | clean |
| **mcp-server-sqlite** `2025.4.25` | official | 6 | — | clean |
| **mcp-server-time** `2026.7.10` | official | 2 | — | clean |
| **server-everything** `2026.7.4` | official | 13 | — | clean |
| **server-filesystem** `2026.7.10` | official | 14 | — | clean |
| **server-github** `2025.4.8` | official | 26 | — | clean |
| **server-memory** `2026.7.4` | official | 9 | — | clean |
| **server-postgres** `0.6.2` | official | 1 | — | clean |
| **server-puppeteer** `2025.5.12` | official | 7 | — | clean |
| **server-sequential-thinking** `2026.7.4` | official | 1 | — | clean |
| **shell-mcp** `0.4.17` | community | 20 | — | clean |

## What the findings mean

- **`llm-capability-override` (high)** — the tool's description speaks to the calling LLM to overturn its prior instructions (a genuine prompt-injection pattern baked into the tool metadata, not user input).
- **`shell-exec` (high)** — the tool runs arbitrary shell commands. Sometimes that's the whole point of the server; the finding exists so you _decide_ that consciously before handing an agent the keys, rather than discovering it later.
- **`secret-handling` (medium)** — a tool's schema looks like it moves credentials/secrets with no sign of redaction.

A clean result is **not** a safety guarantee — `mcp-guard` reads tool metadata, and a server can behave differently from what it advertises. See [`THREAT_MODEL.md`](THREAT_MODEL.md). For servers that gate tool enumeration behind a live API credential (Slack, GitLab, …), see the note in [`observatory/servers.yaml`](observatory/servers.yaml).

## Reproduce it

```bash
pip install -e .
# install the servers listed in observatory/servers.yaml (npm i … / pip install …)
python observatory/scan.py       # -> observatory/results.json
python observatory/generate.py   # -> OBSERVATORY.md + docs/index.html
```

<sub>Generated from `observatory/results.json` (2026-07-14T11:30:21+00:00). Want your server added or re-scanned? Open a PR against `observatory/servers.yaml`.</sub>
