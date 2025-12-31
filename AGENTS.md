# AGENTS.md

This file provides guidelines for LLM-assistants such as Claude Code.

## Dotfiles Management

This repository uses [chezmoi](https://www.chezmoi.io/) to manage dotfiles.

### File Naming Conventions
- `dot_` prefix → hidden files (e.g., `dot_zshrc` → `~/.zshrc`)
- `private_dot_` prefix → private hidden files/directories
- `.tmpl` suffix → Go template files

### Common Commands
- `chezmoi diff` - Preview changes
- `chezmoi apply` - Apply changes
- `chezmoi add <file>` - Add a file to be managed

## Commit Message Conventions

### Brewfile-related commits
When committing changes related to `dot_Brewfile`, use the `brewfile:` prefix in the commit message.

Examples:
- `brewfile: add new cask`
- `brewfile: update dependencies`
