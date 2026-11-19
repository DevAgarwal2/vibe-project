#!/usr/bin/env python3
"""Fix a Vibe config.toml that contains settings Vibe ignores.

Misplaced keys inside ``[[mcp_servers]]`` entries (e.g. ``enabled_tools``,
``agent_paths``, ``enabled_agents``, ``disabled_agents``, ``installed_agents``,
``skill_paths``) are not valid per-server settings and are silently ignored by
Vibe. This script moves keys that are valid top-level settings to the top
level and removes keys that are not Vibe settings at all, writing a backup to
``<file>.bak`` first.

Usage:
    python3 scripts/fix_vibe_config.py                 # fix default locations
    python3 scripts/fix_vibe_config.py --config PATH   # fix specific file(s)
    python3 scripts/fix_vibe_config.py --dry-run       # report only, no writes
"""

from __future__ import annotations

import argparse
import os
import sys
import tomllib
from pathlib import Path
from typing import Any

try:
    import tomli_w
except ImportError:
    tomli_w = None

MCP_SERVER_KEYS = {
    "name",
    "transport",
    "prompt",
    "startup_timeout_sec",
    "tool_timeout_sec",
    "sampling_enabled",
    "disabled",
    "disabled_tools",
    "url",
    "headers",
    "api_key_env",
    "api_key_header",
    "api_key_format",
    "command",
    "args",
    "env",
    "cwd",
}

FALLBACK_TOP_LEVEL_KEYS = {
    "active_model",
    "active_transcribe_model",
    "active_tts_model",
    "agent_paths",
    "api_timeout",
    "auto_compact_threshold",
    "autocopy_to_clipboard",
    "bypass_tool_permissions",
    "connectors",
    "context_warnings",
    "disable_welcome_banner_animation",
    "disabled_agents",
    "disabled_skills",
    "disabled_tools",
    "displayed_workdir",
    "enable_auto_update",
    "enable_notifications",
    "enable_telemetry",
    "enable_update_checks",
    "enabled_agents",
    "enabled_skills",
    "enabled_tools",
    "file_watcher_for_autocomplete",
    "include_commit_signature",
    "include_model_info",
    "include_project_context",
    "include_prompt_detail",
    "installed_agents",
    "models",
    "narrator_enabled",
    "project_context",
    "providers",
    "session_logging",
    "skill_paths",
    "system_prompt_id",
    "tool_paths",
    "tools",
    "transcribe_models",
    "transcribe_providers",
    "tts_models",
    "tts_providers",
    "vim_keybindings",
    "voice_mode_enabled",
}


def top_level_keys() -> set[str]:
    try:
        from vibe.core.config._settings import VibeConfig

        return set(VibeConfig.model_fields) - {"mcp_servers"}
    except Exception:
        return set(FALLBACK_TOP_LEVEL_KEYS)


def _merge_value(existing: Any, incoming: Any) -> Any:
    if isinstance(existing, list) and isinstance(incoming, list):
        merged = list(existing)
        for item in incoming:
            if item not in merged:
                merged.append(item)
        return merged
    if isinstance(existing, dict) and isinstance(incoming, dict):
        merged = dict(incoming)
        merged.update(existing)
        return merged
    return existing if existing is not None else incoming


def fix_config_dict(data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    report: list[str] = []
    valid_top = top_level_keys()
    servers = data.get("mcp_servers")
    if not isinstance(servers, list):
        if servers is not None:
            report.append(
                "mcp_servers is not a list of tables; left unchanged "
                "(expected [[mcp_servers]] entries)"
            )
        return data, report

    for index, server in enumerate(servers):
        if not isinstance(server, dict):
            continue
        for key in [k for k in server if k not in MCP_SERVER_KEYS]:
            value = server.pop(key)
            path = f"mcp_servers[{index}].{key}"
            if key in valid_top:
                data[key] = _merge_value(data.get(key), value)
                report.append(f"moved {path} -> {key} (valid top-level setting)")
            else:
                report.append(f"removed {path} (not a Vibe setting)")
    return data, report


def default_config_paths() -> list[Path]:
    paths: list[Path] = []
    vibe_home = os.getenv("VIBE_HOME")
    home = Path(vibe_home).expanduser() if vibe_home else Path.home() / ".vibe"
    paths.append(home / "config.toml")
    paths.append(Path.cwd() / ".vibe" / "config.toml")
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in paths:
        resolved = p.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(p)
    return unique


def fix_file(path: Path, *, dry_run: bool = False) -> list[str]:
    with path.open("rb") as f:
        data = tomllib.load(f)
    fixed, report = fix_config_dict(data)
    if not report:
        return [f"{path}: no invalid mcp_servers settings found"]
    if dry_run:
        return [f"{path} (dry run):"] + [f"  {line}" for line in report]
    if tomli_w is None:
        raise RuntimeError("tomli_w is required to write TOML (pip install tomli-w)")
    backup = path.with_suffix(path.suffix + ".bak")
    backup.write_bytes(path.read_bytes())
    with path.open("wb") as f:
        tomli_w.dump(fixed, f)
    return [f"{path} (backup at {backup}):"] + [f"  {line}" for line in report]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--config",
        action="append",
        type=Path,
        default=None,
        help="config.toml to fix (repeatable); defaults to ~/.vibe/config.toml and ./.vibe/config.toml",
    )
    parser.add_argument("--dry-run", action="store_true", help="report changes without writing")
    args = parser.parse_args(argv)

    paths = args.config if args.config else default_config_paths()
    missing = [p for p in paths if not p.is_file()]
    for p in missing:
        print(f"{p}: not found, skipped")
    targets = [p for p in paths if p.is_file()]
    if not targets:
        print("no config.toml found; pass --config PATH", file=sys.stderr)
        return 1
    rc = 0
    for path in targets:
        try:
            for line in fix_file(path, dry_run=args.dry_run):
                print(line)
        except Exception as e:
            print(f"{path}: error: {e}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
