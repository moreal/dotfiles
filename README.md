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

## Agent dependencies

Agent skills, MCP declarations, and locally managed plugins use dotagents
3.1.0. Shared declarations live in
`dot_agents/agents.public.toml`: Superpowers 6.4.2 and Chrome DevTools MCP
1.9.0. Their source snapshots and licenses are included under
`dot_agents/plugin-sources/` to preserve the installed versions and
compatibility adapters. `client-state.public.json` provides initial
client defaults; existing local activation preferences take precedence.

Emil Kowalski's public skills are installed directly from
[emilkowalski/skills](https://github.com/emilkowalski/skills) at the commit
pinned in `agents.public.toml`. The wildcard includes every skill under
`skills/` except `emil-design-eng`. Update its `ref` to select a newer
revision. Official versions replace local copies with the same names;
other private skills remain local.

Private dependencies remain in `~/.agents/agents.private.toml`, with
their source bundles under `~/.agents/skill-sources/` or private plugin
directories. Git and chezmoi exclude these files. The after-apply script
combines the public and private declarations into `~/.agents/agents.toml`
before installing dependencies and registering local plugin marketplaces.
The first composition preserves an existing catalog as a private overlay
after removing the now-shared declarations. Private dependencies are
optional: a fresh checkout can install the public skills and two plugins
on its own.

Run `chezmoi apply` after changing shared declarations. Use
`dotagents install` to reinstall the composed catalog, `dotagents doctor`
to check state, and `dotagents sync` to repair generated state offline.

The first migration consolidates legacy skill folders and saves their
originals and native client settings under
`~/.local/state/dotagents-migration/`. Conflicting skill contents stop
the migration before originals are moved. Account-synced skills and
Codex system skills remain available.

Claude and Codex configuration files are initial defaults: chezmoi
creates them on a new machine and preserves existing files. This lets
dotagents and the applications maintain runtime settings without
chezmoi overwriting generated MCP or plugin entries. App-bundled
plugins, connected accounts, and native-only MCP options stay with
their original application.

When installing from Homebrew, use `brew bundle add <name>` to record in Brewfile.
