#!/bin/bash

# Read JSON input from stdin
input=$(cat)

# Extract current directory
cwd=$(echo "$input" | jq -r '.workspace.current_dir // "."')

# Get ccusage statusline output
ccusage_output=$(echo "$input" | ccusage statusline)

# Output: blue directory + ccusage info
printf '\033[01;34m%s\033[00m | %s' "$cwd" "$ccusage_output"
