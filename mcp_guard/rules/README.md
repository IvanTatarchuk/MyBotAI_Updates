# Rules

`default.yaml` is a flat list of rules, loaded and applied to every scanned tool.

## Format

```yaml
- id: shell-exec          # stable id, referenced in findings and CI policy files
  name: Unrestricted shell execution
  severity: high           # low | medium | high
  pattern: '\bsubprocess\b|\bos\.system\b'   # case-insensitive regex
  message: "Unrestricted shell execution"
```

The `pattern` is matched against the tool's name, description, and JSON-serialized
input schema, concatenated together. This is deliberately a coarse static heuristic —
it flags *language that suggests* a risky capability, not a proof that the tool is
exploitable. Treat findings as a triage signal, not a verdict.

## Adding a rule

1. Add an entry to `default.yaml` (or a new `*.yaml` file — all files in this
   directory are loaded).
2. Add a fixture in `tests/fixtures/` that should trigger it, and one that
   deliberately should not, to guard against false positives.
3. Run `pytest`.
