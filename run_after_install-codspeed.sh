#!/bin/sh

set -eu

claude_codspeed_installed() {
    claude plugin list --json 2>/dev/null | awk '
        /"id": "codspeed@claude-plugins-official"/ { plugin = 1 }
        plugin && /"scope": "user"/ { found = 1 }
        plugin && /^  }[,]?$/ { plugin = 0 }
        END { exit !found }
    '
}

codex_codspeed_skills_installed() {
    test -f "$HOME/.agents/skills/codspeed-optimize/SKILL.md" &&
        test -f "$HOME/.agents/skills/codspeed-setup-harness/SKILL.md"
}

if command -v claude >/dev/null 2>&1; then
    if ! claude_codspeed_installed; then
        echo "Installing CodSpeed for Claude Code..."
        claude plugin install codspeed@claude-plugins-official --scope user
    fi
else
    echo "Skipping CodSpeed for Claude Code: claude is not installed." >&2
fi

if command -v codex >/dev/null 2>&1; then
    if codex_codspeed_skills_installed; then
        exit 0
    fi

    if command -v npx >/dev/null 2>&1; then
        echo "Installing CodSpeed skills for Codex..."
        npx skills add CodSpeedHQ/codspeed --skill codspeed-optimize --skill codspeed-setup-harness -g -a codex -y
    else
        echo "Skipping CodSpeed skills for Codex: npx is not installed." >&2
    fi
else
    echo "Skipping CodSpeed skills for Codex: codex is not installed." >&2
fi
