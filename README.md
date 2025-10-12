# moreal's dotfiles

Here are my setting files to stay in consistent environment even if I reset my machines.

## Installation

```bash
brew tap dahlia/dojang https://github.com/dahlia/dojang.git
brew install --cask dahlia/dojang/dojang

dojang apply
```

## Note

Install Git hooks (e.g., pre-commit):

```
git config core.hooksPath hooks
```

Reflect files:

```
dojang reflect -f <PATH>
# dojang reflect -f $HOME/.bashrc
```

