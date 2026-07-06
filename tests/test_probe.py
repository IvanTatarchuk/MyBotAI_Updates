from mcp_guard.probe import synthesize_args


def test_synthesize_args_fills_only_required_properties():
    schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "verbose": {"type": "boolean"},
        },
        "required": ["path"],
    }

    assert synthesize_args(schema) == {"path": "mcp-guard-probe"}


def test_synthesize_args_covers_basic_json_schema_types():
    schema = {
        "type": "object",
        "properties": {
            "s": {"type": "string"},
            "i": {"type": "integer"},
            "n": {"type": "number"},
            "b": {"type": "boolean"},
            "arr": {"type": "array"},
            "obj": {"type": "object"},
        },
        "required": ["s", "i", "n", "b", "arr", "obj"],
    }

    args = synthesize_args(schema)

    assert args == {"s": "mcp-guard-probe", "i": 0, "n": 0, "b": False, "arr": [], "obj": {}}


def test_synthesize_args_prefers_enum_and_default():
    schema = {
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": ["fast", "slow"]},
            "count": {"type": "integer", "default": 5},
        },
        "required": ["mode", "count"],
    }

    assert synthesize_args(schema) == {"mode": "fast", "count": 5}


def test_synthesize_args_handles_url_format_and_nullable_union():
    schema = {
        "type": "object",
        "properties": {
            "endpoint": {"type": "string", "format": "uri"},
            "limit": {"type": ["integer", "null"]},
        },
        "required": ["endpoint", "limit"],
    }

    args = synthesize_args(schema)

    assert args["endpoint"] == "http://127.0.0.1:0/mcp-guard-probe"
    assert args["limit"] == 0
