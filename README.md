# oh-my-claude

```
   ____  _    _       __  ____     __      _____ _                 _
  / __ \| |  | |     |  \/  \ \   / /     / ____| |               | |
 | |  | | |__| |_____| \  / |\ \_/ /_____| |    | | __ _ _   _  __| | ___
 | |  | |  __  |_____| |\/| | \   /______| |    | |/ _` | | | |/ _` |/ _ \
 | |__| | |  | |     | |  | |  | |       | |____| | (_| | |_| | (_| |  __/
  \____/|_|  |_|     |_|  |_|  |_|        \_____|_|\__,_|\__,_|\__,_|\___|

```

> [!CAUTION]
> **EXPERIMENTAL PROJECT** - This plugin runs autonomous AI loops that can consume significant tokens.
> Mind your token usage! `/ultrawork` and `/deepwork` will iterate until completion.
> Use `--max-iterations` to set limits. You have been warned.

[![Korean](https://img.shields.io/badge/lang-한국어-blue.svg)](README.ko.md)

Claude Code plugin for AI-powered iterative development loops.

Inspired by [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) and [Ralph Wiggum](https://ghuntley.com/ralph/).

## Installation

```bash
/plugin marketplace add 2lab-ai/oh-my-claude
/plugin install oh-my-claude@oh-my-claude
/plugin install powertoy@oh-my-claude
```

> **Required**: Run `/oh-my-claude:setup` after installation.

### Authentication

oh-my-claude uses your **Gemini CLI** and **Codex CLI** subscriptions (not API keys).

```bash
# 1. Run setup to check dependencies
/oh-my-claude:setup

# 2. Login to each service
gemini auth login    # Opens browser for Google auth
codex auth           # Opens browser for OpenAI auth

# 3. Verify everything works
/oh-my-claude:setup
```

Once authenticated, agents use your existing subscriptions:
- **Explore agent** → Your Gemini subscription
- **Oracle agent** → Your OpenAI/Codex subscription
- **Librarian agent** → Your Claude subscription (already authenticated via Claude Code)

---

## Main Features

### /ultrawork - Multi-Agent Work Loop

Ralph loop with 3 specialized AI agents for autonomous development.

```bash
/ultrawork "Build REST API for users"
```

**Agents:**
- **Oracle** (Codex GPT-5.2): Architecture decisions, failure analysis (blocking)
- **Explore** (Gemini): Internal codebase search (parallel)
- **Librarian** (Opus 4.5): External docs, GitHub source analysis (parallel)

Loop exits when task is genuinely complete.

### /deepwork - Reviewed Work Loop

Same as ultrawork, but requires **9.5+ score** from all three reviewers (GPT-5.2, Gemini-3, Opus-4.5) before completion.

```bash
/deepwork "Critical security fix" --max-iterations 50
```

### /save & /load - Cross-Tool Context Management

Save work context in one tool and resume in another.

```bash
# In Claude Code: save your work
/save

# In Gemini CLI or Codex: resume the work
/load
```

**Cross-tool workflow example:**
1. Start work in Claude Code, `/save` when done
2. Open Gemini CLI or Codex, `/load` to continue
3. Work across tools seamlessly - they share `./docs/tasks/save/`

**To enable cross-tool commands:**
```bash
./install-cross-session-commands.sh
```

This installs `/save`, `/load`, `/list-saves`, `/check` to:
- `~/.gemini/commands/` (Gemini CLI)
- `~/.codex/prompts/` (Codex)

---

## Commands Reference

### oh-my-claude

| Command | Description |
|---------|-------------|
| `/ultrawork` | Multi-agent autonomous work loop |
| `/deepwork` | Work loop with triple AI review gate (GPT-5.2 + Gemini-3 + Opus-4.5, all ≥9.5) |
| `/save` | Save work context |
| `/load <id>` | Load saved context |
| `/list-saves` | List all saved contexts |
| `/check [all\|id]` | Verify archived saves completion |
| `/cancel-work` | Cancel active loop |
| `/setup` | Verify dependencies |

### powertoy

| Hook | Description |
|------|-------------|
| **auto-title.sh** | Auto-generate session titles (Claude Haiku) |
| **play-sound.sh** | Play sound on session end (macOS) |

---

## MCP Servers

Bundled MCP servers:

| Server | Package |
|--------|---------|
| gemini | @2lab.ai/gemini-mcp-server |
| claude | @2lab.ai/claude-mcp-server |
| codex | codex mcp-server |

---

## Credits

- **oh-my-opencode**: [code-yeongyu](https://github.com/code-yeongyu/oh-my-opencode)
- **Ralpy Wiggum plugin**: https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum
- **Ralph Wiggum technique**: [Geoffrey Huntley](https://ghuntley.com/ralph/)

## FAQ

**Q: Will this burn my tokens?**

A: Yes. That's the feature, not a bug.

```
     /\_/\
    ( o.o )  "I'm helping!"
     > ^ <   - Your AI, iteration 47
```

## TODO

- [ ] LSP support

## License

MIT
