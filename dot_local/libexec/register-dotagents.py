#!/usr/bin/env python3
"""Preserve native client preferences when selecting local dotagents plugins."""

import argparse
import json
from pathlib import Path
import re
import tomllib


def set_plugin_flag(text, plugin, enabled):
    header = f'[plugins.{json.dumps(plugin)}]'
    pattern = re.compile(r"(?m)^" + re.escape(header) + r"\s*\n(?P<body>.*?)(?=^\[|\Z)", re.S)
    value = "true" if enabled else "false"
    match = pattern.search(text)
    if match is None:
        return text.rstrip() + f"\n\n{header}\nenabled = {value}\n"
    body = match["body"]
    if re.search(r"(?m)^enabled\s*=", body):
        body = re.sub(r"(?m)^enabled\s*=.*$", f"enabled = {value}", body)
    else:
        body = f"enabled = {value}\n" + body
    return text[:match.start()] + header + "\n" + body + text[match.end():]


def register(home, options_only=False):
    home = Path(home)
    state = json.loads((home / ".agents/client-state.json").read_text())
    claude_path = home / ".claude/settings.json"
    if state.get("claude") and claude_path.exists():
        settings = json.loads(claude_path.read_text())
        for name, preference in state["claude"].items():
            old = preference["legacy"]
            new = f"{name}@dotagents"
            if options_only and new in settings.get("enabledPlugins", {}):
                preference["enabled"] = settings["enabledPlugins"][new]
            options = settings.get("pluginConfigs", {})
            if old in options and new not in options:
                options[new] = options[old]
            if not options_only:
                enabled = settings.setdefault("enabledPlugins", {})
                enabled[old] = False
                enabled[new] = preference["enabled"]
        claude_path.write_text(json.dumps(settings, indent=2) + "\n")

    codex_path = home / ".codex/config.toml"
    if options_only:
        if codex_path.exists():
            plugins = tomllib.loads(codex_path.read_text()).get("plugins", {})
            for name, preference in state.get("codex", {}).items():
                new = f"{name}@dotagents-local"
                if new in plugins:
                    preference["enabled"] = plugins[new].get("enabled", False)
        (home / ".agents/client-state.json").write_text(json.dumps(state, indent=2) + "\n")
    if not options_only and codex_path.exists():
        text = codex_path.read_text()
        for name, preference in state.get("codex", {}).items():
            text = set_plugin_flag(text, preference["legacy"], False)
            text = set_plugin_flag(text, f"{name}@dotagents-local", preference["enabled"])
        old = str(home / ".codex/skills") + "/"
        new = str(home / ".agents/skills") + "/"
        text = re.sub(r'(?m)^(path\s*=\s*"[^"\n]+/SKILL\.md")',
                      lambda match: match[0].replace(old, new), text)
        tomllib.loads(text)
        codex_path.write_text(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--options-only", action="store_true")
    args = parser.parse_args()
    register(args.home, args.options_only)
