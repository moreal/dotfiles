#!/usr/bin/env bash

function replace-all() {
  old="$1"
  if [[ "$2" = "" ]]; then
    new=''
  else
    new="$2"
  fi

  set -e
  
  python3 -c '
import sys;

old=sys.argv[1]
new=sys.argv[2]

lines=sys.stdin.readlines()
replaced_lines=[x.replace(old, new) for x in lines]

sys.stdout.write("".join(replaced_lines))
' "$old" "$new"
}


function urldecode() {
  python3 -c "import sys; from urllib.parse import unquote; print(unquote(sys.stdin.read()));"
}
