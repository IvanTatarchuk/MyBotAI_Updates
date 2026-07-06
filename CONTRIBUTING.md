# Contributing

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Adding a detection rule

Most contributions are new entries in `mcp_guard/rules/default.yaml` — see
[`mcp_guard/rules/README.md`](mcp_guard/rules/README.md) for the format. Add a
fixture that should trigger the rule and one that deliberately shouldn't, to
guard against false positives, then run `pytest`.

## Reporting a false positive / false negative

Open an issue with the tool's `name`, `description`, and `inputSchema` (redact
anything sensitive) plus which rule fired or should have fired.

## Pull requests

- Keep changes focused; one rule or one feature per PR is easiest to review.
- `pytest -q`, `ruff check .`, and `mypy mcp_guard` must all pass.
- If you touch the CLI, update `README.md`'s example output to match.

## Releasing (maintainers)

1. Bump `version` in `pyproject.toml`, update `CHANGELOG.md`.
2. Tag and push, then draft a GitHub Release from that tag.
3. Publishing that Release triggers `.github/workflows/publish.yml`, which builds
   and uploads to PyPI via Trusted Publishing (OIDC) — no token/secret involved.
   One-time setup: on the PyPI project's Settings → Publishing, add a trusted
   publisher for this repo + `publish.yml` + environment `pypi` (can be done
   before the project's first release, as a "pending publisher").
