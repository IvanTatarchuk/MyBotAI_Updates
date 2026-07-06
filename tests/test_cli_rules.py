import subprocess


def test_rules_command_lists_built_in_rule_count():
    result = subprocess.run(["mcp-guard", "rules"], capture_output=True, text=True, timeout=10)

    assert result.returncode == 0
    assert "shell-exec" in result.stdout
    assert "rules loaded" in result.stdout


def test_rules_command_marks_ignored_rules_from_config(tmp_path):
    config_path = tmp_path / "mcp-guard.json"
    config_path.write_text('{"ignore": ["prompt-injection-cue"]}')

    result = subprocess.run(
        ["mcp-guard", "rules", "--config", str(config_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0
    assert "ignored" in result.stdout
    assert "1 ignored by policy" in result.stdout
