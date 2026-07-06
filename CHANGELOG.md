# Changelog

## Unreleased

### Added
- New rules: `sql-unrestricted`, `process-spawn`, `ssrf-risk`, `cloud-admin-access`,
  `credential-persistence`, `package-install-arbitrary`.
- `examples/sample_server.py` — a real MCP server (via the official SDK) used to
  exercise the `--stdio` scan path end-to-end in tests, not just the static
  `--manifest` path.
- Issue templates (bug report, false positive/negative, new rule proposal) and a
  pull request template.

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
