#!/bin/sh

set -eu

project_root=$(cd -- "$(dirname "$0")/.." && pwd)
test_root=$(mktemp -d)
trap 'rm -rf "$test_root"' EXIT

mkdir -p "$test_root/codex"
cp "$project_root/dot_codex/private_config.toml" "$test_root/codex/config.toml"

config=$(CODEX_HOME="$test_root/codex" codex mcp get codspeed --json)

case "$config" in
    *'"type": "stdio"'*) ;;
    *)
        echo "CodSpeed must use a stdio bridge while its OAuth metadata is incompatible with Codex." >&2
        exit 1
        ;;
esac

case "$config" in
    *'"mcp-remote@0.8.2"'*'"https://mcp.codspeed.io/mcp"'*) ;;
    *)
        echo "CodSpeed must use the pinned mcp-remote bridge." >&2
        exit 1
        ;;
esac
