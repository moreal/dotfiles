#!/bin/sh
set -eu

python3 "$HOME/.local/libexec/compose-dotagents.py"

# Private declarations are optional; public-only installations work too.
if [ ! -f "$HOME/.agents/agents.toml" ]; then
    echo "No public or private agent catalog is available."
    exit 0
fi

python3 "$HOME/.local/libexec/prepare-dotagents.py"
npx --yes --package=@sentry/dotagents@3.1.0 dotagents install
if [ ! -f "$HOME/.agents/client-state.json" ]; then
    exit 0
fi
python3 "$HOME/.local/libexec/register-dotagents.py" --options-only

if command -v claude >/dev/null 2>&1; then
    claude plugin marketplace add "$HOME/.agents"
    python3 -c 'import json,pathlib; print("\n".join(json.loads((pathlib.Path.home()/".agents/client-state.json").read_text()).get("claude", {})))' |
    while IFS= read -r plugin; do
        claude plugin install "$plugin@dotagents" --scope user
    done
fi

if command -v codex >/dev/null 2>&1; then
    codex plugin marketplace add "$HOME"
    python3 -c 'import json,pathlib; print("\n".join(json.loads((pathlib.Path.home()/".agents/client-state.json").read_text()).get("codex", {})))' |
    while IFS= read -r plugin; do
        codex plugin add "$plugin@dotagents-local"
    done
fi

python3 "$HOME/.local/libexec/register-dotagents.py"
