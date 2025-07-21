autoload -Uz compinit && compinit

export LDFLAGS="-L/opt/homebrew/opt/node@22/lib"
export CPPFLAGS="-I/opt/homebrew/opt/node@22/include"

export PATH="/opt/homebrew/opt/curl/bin:$PATH"
export PATH="/opt/homebrew/bin:$PATH"
export PATH="/usr/local/smlnj/bin:$PATH"
export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
export PATH="${ASDF_DATA_DIR:-$HOME/.asdf}/shims:$PATH"

export CPPFLAGS="-I/opt/homebrew/opt/openjdk@21/include"

export GPG_TTY=$(tty)

# BEGIN opam configuration
# This is useful if you're using opam as it adds:
#   - the correct directories to the PATH
#   - auto-completion for the opam binary
# This section can be safely removed at any time if needed.
[[ ! -r '/Users/moreal/.opam/opam-init/init.zsh' ]] || source '/Users/moreal/.opam/opam-init/init.zsh' > /dev/null 2> /dev/null
# END opam configuration

export PATH="$HOME/.cabal/bin:$HOME/.ghcup/bin:$PATH"

source ./.utilfunc/python.sh
source ./.utilfunc/deno.sh
source ./.utilfunc/git.sh
