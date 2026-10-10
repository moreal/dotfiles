#!/usr/bin/env python3
"""Consolidate legacy personal skills once, preserving originals in a backup."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil


def prepare(home):
    home = Path(home)
    agents = home / ".agents"
    marker = agents / ".migration-complete.json"
    if marker.exists():
        return Path(json.loads(marker.read_text())["backup"])

    sources = agents / "skill-sources"
    names = {p.name for p in sources.iterdir() if (p / "SKILL.md").is_file()} if sources.exists() else set()
    canonical = agents / "skills"
    claude = home / ".claude/skills"
    codex = home / ".codex/skills"
    inputs = [sources, canonical, claude]
    inputs.extend(codex / name for name in sorted(names) if (codex / name).exists())

    # Validate the complete merge before moving a single original.
    files = {}
    for root in inputs:
        if not root.exists():
            continue
        is_skill = root.parent == codex
        for path in root.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            relative = (Path(root.name) / path.relative_to(root)) if is_skill else path.relative_to(root)
            previous = files.get(relative)
            if previous is not None and previous.read_bytes() != path.read_bytes():
                raise ValueError(f"Conflicting skill file: {relative}; originals have not been moved")
            files[relative] = path

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = home / ".local/state/dotagents-migration" / stamp
    backup.mkdir(parents=True, mode=0o700)
    for relative in [".codex/config.toml", ".claude.json", ".claude/settings.json",
                     ".claude/plugins/installed_plugins.json", ".claude/plugins/known_marketplaces.json",
                     ".config/opencode/opencode.json", ".config/opencode/opencode.jsonc"]:
        original = home / relative
        if original.is_file():
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, saved)

    staging = backup / "merged-skills"
    staging.mkdir()
    for relative, original in files.items():
        destination = staging / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, destination)

    for original in [claude, canonical, *(codex / name for name in sorted(names))]:
        if not original.exists() and not original.is_symlink():
            continue
        saved = backup / original.relative_to(home)
        saved.parent.mkdir(parents=True, exist_ok=True)
        original.rename(saved)
    canonical.parent.mkdir(parents=True, exist_ok=True)
    staging.rename(canonical)
    claude.parent.mkdir(parents=True, exist_ok=True)
    claude.symlink_to(Path("../.agents/skills"), target_is_directory=True)
    marker.write_text(json.dumps({"backup": str(backup)}, indent=2) + "\n")
    return backup


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    args = parser.parse_args()
    print(f"Dotagents migration backup: {prepare(args.home)}")
