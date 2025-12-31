# moreal's dotfiles

Here are my setting files to stay in consistent environment even if I reset my machines.

Managed with [chezmoi](https://www.chezmoi.io/).

## Installation

```bash
# Install chezmoi
brew install chezmoi

# Initialize and apply dotfiles
chezmoi init --apply moreal
```

> `--apply` flag automatically applies the dotfiles after initialization, combining `chezmoi init` and `chezmoi apply` into a single command.

## Usage

```bash
# See what changes would be made
chezmoi diff

# Apply changes
chezmoi apply

# Add a new file to be managed
chezmoi add ~/.some-config

# Edit a managed file
chezmoi edit ~/.bashrc

# Update from remote and apply
chezmoi update
```

## Note

Install Git hooks (e.g., pre-commit):

```bash
git config core.hooksPath hooks
```

When installing from Homebrew, use `brew bundle add <name>` to record in Brewfile.
