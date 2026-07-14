#!/usr/bin/env python3
"""Turn observatory/results.json into the human-facing report + leaderboard.

Outputs:
  OBSERVATORY.md   — the "data drop": aggregate stats + a per-server table.
  docs/index.html  — a static, self-contained leaderboard (GitHub Pages).

Everything here is derived from results.json; there are no hand-written
verdicts. Re-run after observatory/scan.py:

    python observatory/generate.py
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "observatory" / "results.json"
MD_OUT = ROOT / "OBSERVATORY.md"
HTML_OUT = ROOT / "docs" / "index.html"

# results.json stores severity as the enum value (int); normalise to names.
SEV = {"1": "low", "2": "medium", "3": "high", "low": "low", "medium": "medium", "high": "high"}
SEV_RANK = {"high": 3, "medium": 2, "low": 1}


def _sev(f: dict) -> str:
    return SEV[str(f["severity"])]


def _load() -> dict:
    return json.loads(RESULTS.read_text())


def _server_rank(r: dict) -> tuple:
    worst = max((SEV_RANK[_sev(f)] for f in r["findings"]), default=0)
    return (-worst, -len(r["findings"]), r["name"])


def _totals(results: list[dict]) -> dict[str, int]:
    t = {"high": 0, "medium": 0, "low": 0}
    for r in results:
        for f in r["findings"]:
            t[_sev(f)] += 1
    return t


def _date(iso: str) -> str:
    return datetime.fromisoformat(iso).strftime("%Y-%m-%d")


def render_markdown(data: dict) -> str:
    scanned = [r for r in data["results"] if r["status"] == "ok"]
    scanned.sort(key=_server_rank)
    totals = _totals(scanned)
    with_findings = [r for r in scanned if r["findings"]]
    tools_total = sum(r["tool_count"] for r in scanned)
    date = _date(data["generated_at"])

    lines: list[str] = []
    lines.append("# MCP Security Observatory")
    lines.append("")
    lines.append(
        "A recurring, reproducible scan of **real, public MCP servers** with "
        "[`mcp-guard`](README.md). Every row below is produced by the tool's public "
        "rule set — no hand-written verdicts. Regenerate with `observatory/scan.py` + "
        "`observatory/generate.py`."
    )
    lines.append("")
    lines.append(f"**Last scan:** {date} · **Servers scanned:** {len(scanned)} · "
                 f"**Tools inspected:** {tools_total}")
    lines.append("")
    lines.append("## Headline")
    lines.append("")
    lines.append(
        f"- **{len(scanned) - len(with_findings)} of {len(scanned)} servers scanned clean.** "
        "That's the point — a scanner that flags everything is useless. Most well-maintained "
        "servers scope their tools narrowly and say so."
    )
    lines.append(
        f"- **{len(with_findings)} servers had at least one finding** "
        f"({totals['high']} high, {totals['medium']} medium, {totals['low']} low)."
    )
    off_hits = [r for r in with_findings if r["official"]]
    if off_hits:
        names = ", ".join(f"`{r['name']}`" for r in off_hits)
        lines.append(
            f"- **An _official_ reference server has a finding:** {names}. Provenance is not safety."
        )
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| Server | Source | Tools | Worst | Findings |")
    lines.append("|---|---|---:|---|---|")
    for r in scanned:
        src = "official" if r["official"] else "community"
        if r["findings"]:
            worst = max(r["findings"], key=lambda f: SEV_RANK[_sev(f)])
            worst_sev = _sev(worst).upper()
            fbits = ", ".join(f"`{f['tool']}` → {f['rule_id']} ({_sev(f)})" for f in r["findings"])
        else:
            worst_sev = "—"
            fbits = "clean"
        ver = f" `{r['version']}`" if r.get("version") else ""
        lines.append(f"| **{r['name']}**{ver} | {src} | {r['tool_count']} | {worst_sev} | {fbits} |")
    lines.append("")
    lines.append("## What the findings mean")
    lines.append("")
    lines.append(
        "- **`llm-capability-override` (high)** — the tool's description speaks to the calling "
        "LLM to overturn its prior instructions (a genuine prompt-injection pattern baked into the "
        "tool metadata, not user input)."
    )
    lines.append(
        "- **`shell-exec` (high)** — the tool runs arbitrary shell commands. Sometimes that's the "
        "whole point of the server; the finding exists so you _decide_ that consciously before "
        "handing an agent the keys, rather than discovering it later."
    )
    lines.append(
        "- **`secret-handling` (medium)** — a tool's schema looks like it moves credentials/secrets "
        "with no sign of redaction."
    )
    lines.append("")
    lines.append(
        "A clean result is **not** a safety guarantee — `mcp-guard` reads tool metadata, and a "
        "server can behave differently from what it advertises. See "
        "[`THREAT_MODEL.md`](THREAT_MODEL.md). For servers that gate tool enumeration behind a live "
        "API credential (Slack, GitLab, …), see the note in "
        "[`observatory/servers.yaml`](observatory/servers.yaml)."
    )
    lines.append("")
    lines.append("## Reproduce it")
    lines.append("")
    lines.append("```bash")
    lines.append("pip install -e .")
    lines.append("# install the servers listed in observatory/servers.yaml (npm i … / pip install …)")
    lines.append("python observatory/scan.py       # -> observatory/results.json")
    lines.append("python observatory/generate.py   # -> OBSERVATORY.md + docs/index.html")
    lines.append("```")
    lines.append("")
    lines.append(f"<sub>Generated from `observatory/results.json` ({data['generated_at']}). "
                 "Want your server added or re-scanned? Open a PR against "
                 "`observatory/servers.yaml`.</sub>")
    lines.append("")
    return "\n".join(lines)


def render_html(data: dict) -> str:
    scanned = [r for r in data["results"] if r["status"] == "ok"]
    scanned.sort(key=_server_rank)
    totals = _totals(scanned)
    with_findings = [r for r in scanned if r["findings"]]
    tools_total = sum(r["tool_count"] for r in scanned)
    date = _date(data["generated_at"])

    rows = []
    for r in scanned:
        src = "official" if r["official"] else "community"
        if r["findings"]:
            worst = _sev(max(r["findings"], key=lambda f: SEV_RANK[_sev(f)]))
            chips = "".join(
                f'<span class="chip {_sev(f)}">{f["tool"]} · {f["rule_id"]}</span>'
                for f in r["findings"]
            )
        else:
            worst = "clean"
            chips = '<span class="chip clean">clean</span>'
        ver = f'<span class="ver">{r["version"]}</span>' if r.get("version") else ""
        rows.append(
            f'<tr class="r-{worst}"><td class="name">{r["name"]}{ver}</td>'
            f'<td><span class="src {src}">{src}</span></td>'
            f'<td class="num">{r["tool_count"]}</td>'
            f'<td class="findings">{chips}</td></tr>'
        )
    rows_html = "\n".join(rows)
    clean_n = len(scanned) - len(with_findings)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MCP Security Observatory</title>
<style>
:root {{
  --bg:#0d1117; --card:#161b22; --line:#30363d; --fg:#e6edf3; --muted:#8b949e;
  --high:#f85149; --medium:#d29922; --low:#58a6ff; --clean:#3fb950;
}}
@media (prefers-color-scheme: light) {{
  :root {{ --bg:#ffffff; --card:#f6f8fa; --line:#d0d7de; --fg:#1f2328; --muted:#636c76; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }}
.wrap {{ max-width:920px; margin:0 auto; padding:40px 20px 80px; }}
h1 {{ font-size:1.9rem; margin:0 0 6px; }}
.sub {{ color:var(--muted); margin:0 0 28px; }}
.stats {{ display:flex; flex-wrap:wrap; gap:12px; margin:0 0 28px; }}
.stat {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
  padding:14px 18px; flex:1; min-width:120px; }}
.stat b {{ display:block; font-size:1.7rem; line-height:1.1; }}
.stat span {{ color:var(--muted); font-size:.82rem; }}
.stat.high b {{ color:var(--high); }} .stat.clean b {{ color:var(--clean); }}
.tablewrap {{ overflow-x:auto; border:1px solid var(--line); border-radius:10px; }}
table {{ width:100%; border-collapse:collapse; min-width:600px; }}
th,td {{ text-align:left; padding:11px 14px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ color:var(--muted); font-weight:600; font-size:.78rem; text-transform:uppercase; letter-spacing:.04em; }}
tr:last-child td {{ border-bottom:none; }}
td.num {{ text-align:right; color:var(--muted); font-variant-numeric:tabular-nums; }}
.name {{ font-weight:600; }}
.ver {{ color:var(--muted); font-weight:400; font-size:.8rem; margin-left:7px; }}
.chip {{ display:inline-block; font-size:.76rem; padding:2px 8px; border-radius:20px;
  margin:2px 4px 2px 0; border:1px solid var(--line); white-space:nowrap; }}
.chip.high {{ background:color-mix(in srgb,var(--high) 18%,transparent); border-color:var(--high); }}
.chip.medium {{ background:color-mix(in srgb,var(--medium) 18%,transparent); border-color:var(--medium); }}
.chip.low {{ background:color-mix(in srgb,var(--low) 18%,transparent); border-color:var(--low); }}
.chip.clean {{ color:var(--clean); border-color:color-mix(in srgb,var(--clean) 50%,var(--line)); }}
.src {{ font-size:.76rem; padding:2px 8px; border-radius:6px; background:var(--bg);
  border:1px solid var(--line); color:var(--muted); }}
.foot {{ color:var(--muted); font-size:.85rem; margin-top:26px; }}
a {{ color:var(--low); }}
code {{ background:var(--card); padding:1px 5px; border-radius:5px; font-size:.85em; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>MCP Security Observatory</h1>
  <p class="sub">Reproducible security scans of real, public MCP servers, powered by
    <a href="https://github.com/IvanTatarchuk/MyBotAI_Updates">mcp-guard</a>.
    Last scan {date}.</p>

  <div class="stats">
    <div class="stat"><b>{len(scanned)}</b><span>servers scanned</span></div>
    <div class="stat"><b>{tools_total}</b><span>tools inspected</span></div>
    <div class="stat clean"><b>{clean_n}</b><span>scanned clean</span></div>
    <div class="stat high"><b>{totals['high']}</b><span>high findings</span></div>
    <div class="stat"><b>{totals['medium']}</b><span>medium findings</span></div>
  </div>

  <div class="tablewrap">
  <table>
    <thead><tr><th>Server</th><th>Source</th><th>Tools</th><th>Findings</th></tr></thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
  </div>

  <p class="foot">Findings come from <code>mcp-guard</code>'s public rule set applied to each
    server's advertised tool metadata. A clean result is not a safety guarantee — see the project's
    <code>THREAT_MODEL.md</code>. Regenerate with <code>observatory/scan.py</code> +
    <code>observatory/generate.py</code>.</p>
</div>
</body>
</html>
"""


def main() -> int:
    data = _load()
    MD_OUT.write_text(render_markdown(data))
    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(render_html(data))
    print(f"wrote {MD_OUT.relative_to(ROOT)} and {HTML_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
