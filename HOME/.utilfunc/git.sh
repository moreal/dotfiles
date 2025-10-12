#!/usr/bin/env bash
function gi() {
  local IFS=','
  curl -sLw "\n" "https://www.toptal.com/developers/gitignore/api/$*"
}

alias vim=nvim
alias gvim=nvim
alias gs="git status"
