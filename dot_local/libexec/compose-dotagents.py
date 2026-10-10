#!/usr/bin/env python3
"""Combine shareable dependencies with an optional local-only catalog."""

import argparse
import json
from pathlib import Path
import tomllib


def value(item):
    if isinstance(item, bool):
        return "true" if item else "false"
    if isinstance(item, (str, int, float)):
        return json.dumps(item, ensure_ascii=False, allow_nan=False)
    if isinstance(item, list):
        return "[" + ", ".join(value(x) for x in item) + "]"
    if isinstance(item, dict):
        return "{ " + ", ".join(f"{value(k)} = {value(v)}" for k, v in item.items()) + " }"
    raise TypeError(f"Unsupported TOML value: {type(item).__name__}")


def write_catalog(path, data):
    text = "# Generated from public and local-only dependency declarations.\n"
    text += "\n".join(f"{value(k)} = {value(v)}" for k, v in data.items()) + "\n"
    tomllib.loads(text)
    path.write_text(text)
    path.chmod(0o600)


def merge(public, private):
    result = dict(public)
    for key, item in private.items():
        previous = result.get(key)
        if isinstance(item, dict) and isinstance(previous, dict):
            result[key] = merge(previous, item)
        elif isinstance(item, list) and isinstance(previous, list):
            combined = list(previous)
            for entry in item:
                if entry in combined:
                    continue
                if isinstance(entry, dict) and "name" in entry:
                    if any(isinstance(x, dict) and x.get("name") == entry["name"] for x in combined):
                        raise ValueError(f"Conflicting {key} declaration: {entry['name']}")
                combined.append(entry)
            result[key] = combined
        else:
            if key == "version" and previous is not None and previous != item:
                raise ValueError("Conflicting schema versions")
            result[key] = item
    return result


def compose(root):
    root = Path(root)
    public_path = root / "agents.public.toml"
    if not public_path.exists():
        return
    public = tomllib.loads(public_path.read_text())
    private_path = root / "agents.private.toml"
    generated = root / "agents.toml"
    if not private_path.exists() and generated.exists():
        private = tomllib.loads(generated.read_text())
        for field in ["skills", "plugins", "mcp", "subagents"]:
            names = {x["name"] for x in public.get(field, [])}
            private[field] = [x for x in private.get(field, []) if x["name"] not in names]
        write_catalog(private_path, private)
    private = tomllib.loads(private_path.read_text()) if private_path.exists() else {}
    combined = merge(public, private)
    write_catalog(generated, combined)

    public_state = root / "client-state.public.json"
    if public_state.exists():
        defaults = json.loads(public_state.read_text())
        state_path = root / "client-state.json"
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
        for runtime, plugins in defaults.items():
            current = state.setdefault(runtime, {})
            for name, preference in plugins.items():
                current.setdefault(name, preference)
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        state_path.chmod(0o600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.home() / ".agents")
    compose(parser.parse_args().root)
