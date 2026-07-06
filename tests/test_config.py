from pathlib import Path

from mcp_guard.config import load_config


def test_missing_default_config_returns_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert load_config(None) == {}


def test_explicit_config_is_loaded_and_rule_paths_resolved(tmp_path):
    (tmp_path / "extra.yaml").write_text("- id: x\n  name: X\n  severity: low\n  pattern: 'x'\n  message: 'x'\n")
    config_path = tmp_path / "mcp-guard.json"
    config_path.write_text('{"fail_on": "high", "ignore": ["a", "b"], "rules": ["extra.yaml"]}')

    config = load_config(config_path)

    assert config["fail_on"] == "high"
    assert config["ignore"] == ["a", "b"]
    assert config["rules"] == [str(tmp_path / "extra.yaml")]


def test_default_config_discovered_in_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("mcp-guard.json").write_text('{"fail_on": "medium"}')

    config = load_config(None)

    assert config["fail_on"] == "medium"
