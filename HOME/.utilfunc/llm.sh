#!/usr/bin/env bash

function link-agents-md() {
  local source_file="AGENTS.md"
  local target_files=(
    "CLAUDE.md"
    ".github/copilot-instructions.md"
    "GEMINI.md"
    ".cursorrules"
    ".windsurfrules"
    "WARP.md"
  )

  if [[ ! -f "$source_file" ]]; then
    echo "[ERROR] $source_file not found in current directory" >&2
    return 1
  fi

  for target in "${target_files[@]}"; do
    local target_dir
    target_dir=$(dirname "$target")

    if [[ "$target_dir" != "." ]]; then
      mkdir -p "$target_dir"
    fi

    if [[ -e "$target" ]]; then
      echo "[INFO] Skipping $target: file already exists" >&2
      continue
    fi

    ln -s "$source_file" "$target"
    echo "[INFO] Created symbolic link: $target -> $source_file" >&2
  done
}
