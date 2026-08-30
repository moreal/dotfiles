#!/bin/sh

set -eu

claude_superpowers_installed() {
    claude plugin list --json 2>/dev/null | awk '
        /"id": "superpowers@claude-plugins-official"/ { plugin = 1 }
        plugin && /"scope": "user"/ { found = 1 }
        plugin && /^  }[,]?$/ { plugin = 0 }
        END { exit !found }
    '
}

codex_superpowers_installed() {
    codex plugin list --json 2>/dev/null |
        grep -Fq '"pluginId": "superpowers@openai-curated"'
}

if command -v claude >/dev/null 2>&1; then
    if ! claude_superpowers_installed; then
        echo "Installing Superpowers for Claude Code..."
        claude plugin install superpowers@claude-plugins-official --scope user
    fi
else
    echo "Skipping Superpowers for Claude Code: claude is not installed." >&2
fi

if command -v codex >/dev/null 2>&1; then
    if ! codex_superpowers_installed; then
        echo "Installing Superpowers for Codex..."
        codex plugin add superpowers@openai-curated
    fi
else
    echo "Skipping Superpowers for Codex: codex is not installed." >&2
fi
