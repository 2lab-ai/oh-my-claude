# oh-my-claude

[![Korean](https://img.shields.io/badge/lang-한국어-blue.svg)](README.ko.md)

Claude Code plugin marketplace by [2lab.ai](https://2lab.ai)

Heavily inspired by [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)

Ralph Loop from [ralph wiggum plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-wiggum)

## Installation

```bash
# Add marketplace
/plugin marketplace add 2lab-ai/oh-my-claude
/plugin install oh-my-claude@oh-my-claude
/plugin install powertoy@oh-my-claude
```

---

## Workflow

### Ultra Work Loop

```bash
/ultrawork "your task"
```

Ralph Loop with agent orchestration. Auto-completes when both Codex and Gemini reviews score 9.5+.

### Cross-Session & Cross-Tool Workflow

```bash
# Save context during work
/save

# Resume in a new session
/load
```

**Use Cases:**

1. **Session Continuity** - Work in Claude Code, `/save`, then `/load` in a new session to continue seamlessly

2. **Cross-Tool Migration** - `/save` in Claude Code, then `/load` in [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) to continue (or vice versa)

Saved content: Current plan, TODO list, work context

---

## oh-my-claude

Task management and Ralph Wiggum loops.

### Task Management Commands

| Command | Description |
|---------|-------------|
| `/ohmyclaude:save` | Save current work context to `./docs/tasks/save/{id}` |
| `/ohmyclaude:load <id>` | Load saved work context and resume |
| `/ohmyclaude:list-saves` | List all saved contexts with branch filtering |
| `/ohmyclaude:check [all\|id]` | Verify completion status of archived saves |

### Ralph Wiggum Loop

Self-referential AI development loops for iterative task completion.

| Command | Description |
|---------|-------------|
| `/ohmyclaude:ralph-loop` | Start a Ralph loop with your prompt |
| `/ohmyclaude:ultrawork` | Ultra work loop with Codex + Gemini review (9.5+ to complete) |
| `/ohmyclaude:cancel-ralph` | Cancel active Ralph loop |
| `/ohmyclaude:ralph-help` | Ralph Wiggum usage guide |

**Quick Start:**
```bash
/ohmyclaude:ralph-loop "Build a REST API for todos. Output <promise>COMPLETE</promise> when done." --completion-promise "COMPLETE" --max-iterations 50
```

### MCP Servers (included)

- `gemini` - @2lab.ai/gemini-mcp-server
- `claude` - @2lab.ai/claude-mcp-server
- `codex` - codex mcp-server

---

## powertoy

Power utilities for Claude Code sessions.

### Hooks

| Hook | Description |
|------|-------------|
| **auto-title.sh** | Auto-generates titles for untitled sessions using Claude Haiku |
| **play-sound.sh** | Plays notification sound when session ends (macOS) |

---

## Ralph Wiggum Technique

```json
{
  "credits": [
    {
      "name": "Geoffrey Huntley",
      "contribution": "Ralph Wiggum technique",
      "url": "https://ghuntley.com/ralph/"
    },
    {
      "name": "Daisy Hollman",
      "email": "daisy@anthropic.com",
      "contribution": "Original ralph-wiggum plugin implementation"
    }
  ]
}
```

Ralph is a development methodology based on continuous AI agent loops. The technique is named after Ralph Wiggum from The Simpsons, embodying the philosophy of persistent iteration despite setbacks.

### How It Works

```bash
# You run ONCE:
/ohmyclaude:ralph-loop "Your task description" --completion-promise "DONE"

# Then Claude Code automatically:
# 1. Works on the task
# 2. Tries to exit
# 3. Stop hook blocks exit
# 4. Stop hook feeds the SAME prompt back
# 5. Repeat until completion
```

### Best Practices

1. **Clear completion criteria** - Always specify when the task is "done"
2. **Incremental goals** - Break large tasks into phases
3. **Self-correction** - Include TDD/verification steps
4. **Safety limits** - Always use `--max-iterations` as escape hatch

### When to Use

**Good for:**
- Well-defined tasks with clear success criteria
- Tasks requiring iteration (e.g., getting tests to pass)
- Greenfield projects where you can walk away
- Tasks with automatic verification

**Not good for:**
- Tasks requiring human judgment
- One-shot operations
- Unclear success criteria

---

## Credits

- **Ralph Wiggum technique**: [Geoffrey Huntley](https://ghuntley.com/ralph/)
- **Original ralph-wiggum plugin**: Daisy Hollman (daisy@anthropic.com, Anthropic)

## Learn More

- Ralph Wiggum: https://ghuntley.com/ralph/
- Ralph Orchestrator: https://github.com/mikeyobrien/ralph-orchestrator

## License

MIT
