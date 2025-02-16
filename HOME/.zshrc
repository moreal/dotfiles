autoload -Uz compinit && compinit

export LDFLAGS="-L/opt/homebrew/opt/node@22/lib"
export CPPFLAGS="-I/opt/homebrew/opt/node@22/include"

export PATH="/opt/homebrew/opt/curl/bin:$PATH"
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

function fetch-next-data() {
  url="$1"
  hostname=$(echo "$url" | sed -E 's|https?://([^/]+).*|\1|')

  echo 'import { DOMParser } from "jsr:@b-fuze/deno-dom@^0.1.49";
import { Command } from "jsr:@cliffy/command@^1.0.0-rc.7";

await new Command()
  .name("fetch-next-data")
  .description("A CLI to fetch __NEXT_DATA__ data.")
  .version("v0.0.0")
  .arguments("<url>")
  .action(async ({}, url) => {
    const resp = await fetch(url);
    const respText = await resp.text();

    const doc = new DOMParser().parseFromString(respText, "text/html");

    const nextData = doc.querySelector("script[id=__NEXT_DATA__]")!;
    console.log(nextData.innerText);
  })
  .parse();
' | deno run --allow-net="$hostname" - "$1"
}

function urldecode() {
  python3 -c "import sys; from urllib.parse import unquote; print(unquote(sys.stdin.read()));"
}
