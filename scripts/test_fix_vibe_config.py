#!/usr/bin/env python3
"""Tests for fix_vibe_config. Runnable directly or via pytest."""

from __future__ import annotations

import sys
import tempfile
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fix_vibe_config import fix_config_dict, fix_file, main

SAMPLE = """
active_model = "mistral-medium-3.5"

[[mcp_servers]]
name = "myserver"
transport = "stdio"
command = "npx"
args = ["-y", "some-mcp"]
disabled_tools = ["delete"]
enabled_tools = ["search"]
agent_paths = ["./agents"]
enabled_agents = ["helper"]
disabled_agents = ["old"]
installed_agents = ["chat"]
skill_paths = ["./skills"]
tool_paths = ["./tools"]
enabled_skills = ["search-*"]
disabled_skills = ["old-skill"]
tools = { bash = { allowlist = ["ls"] } }
connectors = [{ name = "foo", disabled = true }]
enable_toolz = ["typo"]
"""


def test_misplaced_keys_are_hoisted_or_removed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.toml"
        path.write_text(SAMPLE)
        lines = fix_file(path)
        text = "\n".join(lines)
        assert "moved mcp_servers[0].enabled_tools -> enabled_tools" in text
        assert "moved mcp_servers[0].agent_paths -> agent_paths" in text
        assert "moved mcp_servers[0].enabled_agents -> enabled_agents" in text
        assert "moved mcp_servers[0].disabled_agents -> disabled_agents" in text
        assert "moved mcp_servers[0].installed_agents -> installed_agents" in text
        assert "moved mcp_servers[0].skill_paths -> skill_paths" in text
        assert "removed mcp_servers[0].enable_toolz" in text
        assert path.with_suffix(".toml.bak").is_file()

        with path.open("rb") as f:
            data = tomllib.load(f)
        server = data["mcp_servers"][0]
        assert server["name"] == "myserver"
        assert server["transport"] == "stdio"
        assert server["command"] == "npx"
        assert server["args"] == ["-y", "some-mcp"]
        assert server["disabled_tools"] == ["delete"]
        assert set(server) == {
            "name", "transport", "command", "args", "disabled_tools",
        }
        assert data["enabled_tools"] == ["search"]
        assert data["agent_paths"] == ["./agents"]
        assert data["enabled_agents"] == ["helper"]
        assert data["disabled_agents"] == ["old"]
        assert data["installed_agents"] == ["chat"]
        assert data["skill_paths"] == ["./skills"]
        assert data["tool_paths"] == ["./tools"]
        assert data["enabled_skills"] == ["search-*"]
        assert data["disabled_skills"] == ["old-skill"]
        assert data["tools"] == {"bash": {"allowlist": ["ls"]}}
        assert data["connectors"] == [{"name": "foo", "disabled": True}]
        assert "enable_toolz" not in data
        assert data["active_model"] == "mistral-medium-3.5"


def test_hoist_merges_with_existing_top_level() -> None:
    data = {
        "enabled_tools": ["read_file"],
        "mcp_servers": [
            {"name": "s", "transport": "stdio", "command": "x",
             "enabled_tools": ["grep", "read_file"]}
        ],
    }
    fixed, report = fix_config_dict(data)
    assert fixed["enabled_tools"] == ["read_file", "grep"]
    assert fixed["mcp_servers"][0] == {"name": "s", "transport": "stdio", "command": "x"}
    assert any("enabled_tools" in line for line in report)


def test_clean_config_is_untouched() -> None:
    data = {"mcp_servers": [{"name": "s", "transport": "stdio", "command": "x"}]}
    fixed, report = fix_config_dict(data)
    assert fixed == data
    assert report == []


def test_dry_run_does_not_write() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.toml"
        path.write_text(SAMPLE)
        before = path.read_bytes()
        lines = fix_file(path, dry_run=True)
        assert any("dry run" in line for line in lines)
        assert path.read_bytes() == before
        assert not path.with_suffix(".toml.bak").exists()


def test_main_with_explicit_config(tmp_path=None) -> None:
    import tempfile as tf

    with tf.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.toml"
        path.write_text(SAMPLE)
        rc = main(["--config", str(path)])
        assert rc == 0
        with path.open("rb") as f:
            data = tomllib.load(f)
        assert data["skill_paths"] == ["./skills"]
        assert "enable_toolz" not in data["mcp_servers"][0]


def main_test() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok - {t.__name__}")
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    main_test()
