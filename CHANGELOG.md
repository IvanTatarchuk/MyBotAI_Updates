# Changelog

## Unreleased

## 0.2.0 - 2026-07-06

### Added
- `mcp-guard probe --stdio ... --yes` (experimental): actually launches the server
  and calls every tool once with synthesized arguments, inside a sandbox built
  entirely on `unshare` (no Docker/bubblewrap dependency) that blocks both outbound
  network access and filesystem writes outside a throwaway tmpfs scratch space.
  Requires explicit `--yes` since it executes real code. The read-only remount
  walks `/proc/self/mountinfo` and covers every real mountpoint, not just `/` —
  a separately-mounted filesystem (second disk, Docker volume, network share)
  is covered too, not only whatever's mounted at the target's working directory.
  See THREAT_MODEL.md for exact isolation boundaries (reads aren't blocked).
- `mcp-guard rules`: lists every active detection rule.
- `ruff` + `mypy`, wired into a CI lint job.
- New rules: `sql-unrestricted`, `process-spawn`, `ssrf-risk`, `cloud-admin-access`,
  `credential-persistence`, `package-install-arbitrary`.
- `examples/sample_server.py` — a real MCP server (via the official SDK) used to
  exercise the `--stdio` scan path end-to-end in tests, not just the static
  `--manifest` path. Its `check_internet_access` and `write_outside_tmp` tools make
  genuine network/filesystem attempts, used to prove `probe`'s sandbox actually
  blocks both rather than just claiming to.
- Issue templates (bug report, false positive/negative, new rule proposal) and a
  pull request template.
- `THREAT_MODEL.md`.
- New rule `llm-capability-override`: catches descriptions that address the calling
  LLM directly to override its prior beliefs about its own capabilities.
- `.github/workflows/publish.yml`: publishes to PyPI on GitHub Release via Trusted
  Publishing (OIDC) — no token/secret required. See CONTRIBUTING.md for the release
  steps and one-time PyPI-side setup.
- `docs/AUDIT_NOTES.md`: findings from scanning the official `mcp-server-fetch`,
  `mcp-server-git`, `mcp-server-time`, `mcp-server-filesystem`,
  `mcp-server-sqlite`, and `server-everything` reference servers.

### Fixed
- `net-any` missed the generic "fetches a URL from the internet" phrasing (as
  opposed to "fetch *any* URL"). Found by scanning the real, published
  `mcp-server-fetch` reference server, which scanned clean before this fix despite
  doing unrestricted URL fetching.
- That same real server's `fetch` tool description contains a genuine
  prompt-injection payload aimed at the calling LLM ("you did not have internet
  access... this tool now grants you internet access...") that `prompt-injection-cue`
  didn't catch — this is what `llm-capability-override` (above) was added for.
- `scan`/`probe` had no timeout: a server launched via `npx` (extremely common in
  MCP server docs) could hang forever instead of erroring, because npx can
  delay/swallow the initialize handshake. Added a `--timeout` option (default 30s)
  to both commands, plus a `StdioTimeout` error that unwraps the ExceptionGroup
  anyio/MCP wraps a plain `TimeoutError` in, so the failure is a clear one-line
  message instead of a raw traceback.

## 0.1.0 - 2026-07-06

### Added
- Initial release: rule-based scanner for MCP tool definitions.
- `mcp-guard scan` CLI with `--stdio` (live server) and `--manifest` (static
  JSON) input modes, `table`/`json` output.
- Built-in rules: `shell-exec`, `fs-read-any`, `fs-write-any`, `net-any`,
  `secret-handling`, `prompt-injection-cue`, `eval-sink`.
- `mcp-guard.json` policy file (`fail_on`, `ignore`, `rules`) for CI gating.
- Reusable GitHub Action (`action.yml`).
- CI workflow running the test suite across Python 3.10-3.12.
