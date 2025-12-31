#!/usr/bin/env bash
function fetch-script-data() {
  url="$1"
  hostname=$(echo "$url" | sed -E 's|https?://([^/]+).*|\1|')

  deno run --allow-net="$hostname" ./.deno-scripts/fetch-script-data.ts "$1" "$2"
}
