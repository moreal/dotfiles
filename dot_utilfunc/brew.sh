#!/usr/bin/env bash

# Add a brew/cask/tap entry to the dotfiles-managed Brewfile, commit it,
# apply it via chezmoi, then actually install it. Runnable from anywhere.
#
# Usage: brew-add <brew|cask|tap> <name>
function brew-add() {
  local kind="$1" name="$2"

  if [[ -z "$kind" || -z "$name" ]]; then
    echo "Usage: brew-add <brew|cask|tap> <name>" >&2
    return 1
  fi
  if [[ "$kind" != "brew" && "$kind" != "cask" && "$kind" != "tap" ]]; then
    echo "kind must be one of: brew, cask, tap" >&2
    return 1
  fi

  local src_dir brewfile
  src_dir="$(chezmoi source-path)" || return 1
  brewfile="$src_dir/dot_Brewfile"

  if grep -qF "${kind} \"${name}\"" "$brewfile"; then
    echo "${kind} \"${name}\" is already in Brewfile" >&2
  else
    local last_line
    last_line=$(grep -n "^${kind} \"" "$brewfile" | tail -1 | cut -d: -f1)
    if [[ -z "$last_line" ]]; then
      last_line=$(wc -l < "$brewfile")
    fi
    sed -i '' "${last_line}a\\
${kind} \"${name}\"
" "$brewfile"

    git -C "$src_dir" add dot_Brewfile
    git -C "$src_dir" commit -m "brewfile: add ${name}" || return 1
  fi

  chezmoi apply ~/.Brewfile || return 1

  case "$kind" in
    brew) brew install "$name" ;;
    cask) brew install --cask "$name" ;;
    tap) brew tap "$name" ;;
  esac
}

# Remove a brew/cask/tap entry from the dotfiles-managed Brewfile, commit it,
# apply it via chezmoi, then actually uninstall it. Runnable from anywhere.
#
# Usage: brew-remove <brew|cask|tap> <name>
function brew-remove() {
  local kind="$1" name="$2"

  if [[ -z "$kind" || -z "$name" ]]; then
    echo "Usage: brew-remove <brew|cask|tap> <name>" >&2
    return 1
  fi
  if [[ "$kind" != "brew" && "$kind" != "cask" && "$kind" != "tap" ]]; then
    echo "kind must be one of: brew, cask, tap" >&2
    return 1
  fi

  local src_dir brewfile line
  src_dir="$(chezmoi source-path)" || return 1
  brewfile="$src_dir/dot_Brewfile"
  line="${kind} \"${name}\""

  if ! grep -qxF "$line" "$brewfile"; then
    echo "${line} not found in Brewfile" >&2
    return 1
  fi

  awk -v line="$line" '$0 != line' "$brewfile" > "$brewfile.tmp" && mv "$brewfile.tmp" "$brewfile"

  git -C "$src_dir" add dot_Brewfile
  git -C "$src_dir" commit -m "brewfile: remove ${name}" || return 1

  chezmoi apply ~/.Brewfile || return 1

  case "$kind" in
    brew) brew uninstall "$name" ;;
    cask) brew uninstall --cask "$name" ;;
    tap) brew untap "$name" ;;
  esac
}
