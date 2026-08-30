#!/bin/sh

set -eu

project_root=$(cd -- "$(dirname "$0")/.." && pwd)
test_root=$(mktemp -d)
trap 'rm -rf "$test_root"' EXIT

test_home="$test_root/home"
test_bin="$test_root/bin"
call_log="$test_root/calls"

mkdir -p \
    "$test_home/.agents/skills/codspeed-optimize" \
    "$test_home/.agents/skills/codspeed-setup-harness" \
    "$test_bin"
: >"$test_home/.agents/skills/codspeed-optimize/SKILL.md"
: >"$test_home/.agents/skills/codspeed-setup-harness/SKILL.md"
: >"$call_log"

printf '%s\n' \
    '#!/bin/sh' \
    'printf '\''[\n  {\n    "id": "codspeed@claude-plugins-official",\n    "scope": "user"\n  }\n]\n'\''' \
    >"$test_bin/claude"

printf '%s\n' \
    '#!/bin/sh' \
    'exit 0' \
    >"$test_bin/codex"

# These variables belong to the generated stub.
# shellcheck disable=SC2016
printf '%s\n' \
    '#!/bin/sh' \
    'printf '\''%s\n'\'' "$*" >>"$CALL_LOG"' \
    >"$test_bin/npx"

chmod +x "$test_bin/claude" "$test_bin/codex" "$test_bin/npx"

env -u CODEX_HOME \
    HOME="$test_home" \
    PATH="$test_bin:/usr/bin:/bin" \
    CALL_LOG="$call_log" \
    "$project_root/run_after_install-codspeed.sh"

if test -s "$call_log"; then
    echo "CodSpeed installer reran even though both Codex skills were installed." >&2
    exit 1
fi
