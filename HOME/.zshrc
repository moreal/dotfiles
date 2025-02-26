autoload -Uz compinit && compinit

export LDFLAGS="-L/opt/homebrew/opt/node@22/lib"
export CPPFLAGS="-I/opt/homebrew/opt/node@22/include"

export PATH="/opt/homebrew/opt/curl/bin:$PATH"
export PATH="/opt/homebrew/bin:$PATH"
export PATH="/usr/local/smlnj/bin:$PATH"
export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"

alias vim=nvim
alias gvim=nvim
alias gs="git status"

export CPPFLAGS="-I/opt/homebrew/opt/openjdk@21/include"

export GPG_TTY=$(tty)

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

function fetch-script-data() {
  url="$1"
  hostname=$(echo "$url" | sed -E 's|https?://([^/]+).*|\1|')

  deno run --allow-net="$hostname" ./fetch-script-data.ts "$1" "$2"
}

function urldecode() {
  python3 -c "import sys; from urllib.parse import unquote; print(unquote(sys.stdin.read()));"
}
