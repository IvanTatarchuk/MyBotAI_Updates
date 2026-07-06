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
- `pytest -q` must pass.
- If you touch the CLI, update `README.md`'s example output to match.
