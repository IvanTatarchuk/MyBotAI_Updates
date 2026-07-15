# mcp-guard v0.2.0 — Launch plan

Goal: ship v0.2.0 to PyPI and get it in front of the MCP / AI-agent-security
audience, so it collects the real external feedback that unblocks the
`IDEAS_BACKLOG.md` revisit condition.

Release-readiness verified 2026-07-15: `pytest` 28/28 pass, `ruff check .` clean,
`mypy mcp_guard` clean, `pyproject.toml` at 0.2.0, `CHANGELOG.md` 0.2.0 section
written. Blockers below are packaging/positioning, not code.

---

## The hook (this is the whole pitch)

**"I scanned the official MCP reference servers for security issues — here's what
I found."** `docs/AUDIT_NOTES.md` documents real findings on real, published
servers — most notably a genuine prompt-injection payload living in the official
`mcp-server-fetch` tool description ("you did not have internet access... this
tool now grants you internet access..."). That is a concrete, verifiable, "wait,
what?" story on a server thousands of people already run. Lead every channel with
it. Positioning: **"Socket.dev, but for MCP servers."**

---

## Phase 0 — Pre-flight (do before tagging)

- [ ] **Fix README status line** — it still says `Early / v0.1`. Update to v0.2,
      keep the honest "static heuristic" caveat.
- [ ] **Pull the audit hook up-front in README** — a short "Found in the wild"
      block near the top linking `AUDIT_NOTES.md`. This is the reason people star.
- [ ] **PyPI one-time Trusted Publishing setup** (human, Ivan's PyPI account):
      pypi.org → create/claim project `mcp-guard` → Settings → Publishing → add
      pending publisher: repo `IvanTatarchuk/MyBotAI_Updates`, workflow
      `publish.yml`, environment `pypi`. Can be registered before first upload.
- [ ] **Confirm the name `mcp-guard` is free on PyPI** — if taken, decide fallback
      (`mcpguard`, `mcp-guardian`) and update `pyproject.toml` + README + docs
      *before* tagging.
- [ ] **Local build dry-run**: `python -m build && twine check dist/*` — catches
      metadata/README-render errors before the Release fires the real publish.

## Phase 1 — Ship the release

- [ ] Merge Phase-0 changes to the default branch.
- [ ] Tag and push:
      ```
      git tag v0.2.0
      git push origin v0.2.0
      ```
- [ ] GitHub → Releases → Draft new release from tag `v0.2.0`. Title `v0.2.0`,
      body = the 0.2.0 section of `CHANGELOG.md`. **Publish** → this fires
      `.github/workflows/publish.yml` (OIDC, no token).
- [ ] Watch the `Publish to PyPI` action go green.
- [ ] **Verify from a clean env**: `pipx run mcp-guard --help` (or fresh venv
      `pip install mcp-guard`), then a real smoke test:
      `mcp-guard scan --manifest examples/...` and confirm the fetch-server
      prompt-injection example still fires.

## Phase 2 — Launch assets (build before posting anywhere)

- [ ] **30-second demo GIF / asciinema**: `mcp-guard scan` flagging the real
      `mcp-server-fetch` prompt-injection payload. This single asset does most of
      the selling — embed it in README top and every post.
- [ ] **Blog / Dev.to post**: "I scanned the official MCP reference servers —
      here's what I found." Walk through `AUDIT_NOTES.md`, end with install line.
      This is the evergreen artifact all social links point to.
- [ ] **One-liner positioning** locked: "Open-source security scanner for MCP
      servers — Socket.dev for the tools you wire into your agent."

## Phase 3 — Distribution (the actual launch, staggered — not all at once)

Ranked by audience fit:

1. **Show HN** — best fit. Title e.g. *"Show HN: mcp-guard – I scanned the
   official MCP servers and found a live prompt injection"*. Post Tue–Thu ~8–10am
   ET. First comment = the AUDIT_NOTES story + honest THREAT_MODEL caveat.
2. **Reddit**: r/mcp, r/LocalLLaMA, r/netsec, r/programming. Tailor each title;
   don't cross-post identically the same hour.
3. **MCP community**: `modelcontextprotocol` GitHub Discussions; official
   Discord #showcase; open a PR adding mcp-guard to `awesome-mcp-servers` /
   awesome-mcp-security lists (durable discovery channel).
4. **X/Twitter + LinkedIn**: the demo GIF + the one finding. Tag MCP/agent-sec
   voices. Thread format, screenshot of the flagged payload.

## Phase 4 — First 48 hours (this is where it's won or lost)

- [ ] Be present and fast on every HN/Reddit comment — response speed on launch
      day directly drives ranking and trust.
- [ ] Triage incoming issues / false-positive reports same-day. A fast
      "fixed in v0.2.1" turnaround is the strongest possible trust signal for a
      *security* tool.
- [ ] Log every "does it catch X?" question — each is a candidate new rule and a
      reason for someone to come back.

## Phase 5 — Measure & decide next step

Success = the `IDEAS_BACKLOG.md` revisit condition is met: real external signal
(issues, PRs, or usage), not internal testing. Concrete targets for first 2 weeks:

- [ ] ≥1 external issue or PR from someone who isn't you.
- [ ] ≥1 unsolicited "I put this in my CI" / star from a real MCP user.
- [ ] PyPI downloads trending, not flat, after the HN spike.

If those hit → the security/trust-layer direction (see `MARKET_ANALYSIS.md`
thinking: runtime monitoring, policy enforcement, verified-server registry) is
validated to build on. If the audit-hook post lands but the tool doesn't retain →
the interest is in the *findings*, not the scanner: pivot toward the registry /
"verified MCP servers" angle rather than more static rules.

---

## Sequencing summary

Phase 0 (packaging + PyPI setup) → Phase 1 (tag → Release → auto-publish → verify)
→ Phase 2 (demo GIF + blog) → Phase 3 (Show HN first, then stagger) →
Phase 4 (48h presence) → Phase 5 (measure).

Do **not** post to any channel before `pip install mcp-guard` works from a clean
machine and the demo GIF exists — a broken install link on launch day is
unrecoverable.
