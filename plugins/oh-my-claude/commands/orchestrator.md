---
description: "Multi-agent work coordinator. Delegates to Oracle/Explore/Librarian. Runs in current context (can use AskUserQuestion)."
argument-hint: "TASK"
allowed-tools:
  - Task
  - TaskOutput
  - TodoWrite
  - AskUserQuestion
  - Read
  - Grep
  - Glob
  - Edit
  - Write
  - Bash
  - mcp__plugin_ohmyclaude_claude-as-mcp__chat
  - mcp__plugin_ohmyclaude_claude-as-mcp__chat-reply
  - mcp__plugin_ohmyclaude_gemini-as-mcp__gemini
  - mcp__plugin_ohmyclaude_gemini-as-mcp__gemini-reply
  - mcp__plugin_ohmyclaude_gpt-as-mcp__codex
  - mcp__plugin_ohmyclaude_gpt-as-mcp__codex-reply
---

# /orchestrator - Multi-Agent Work Coordinator

Coordinate specialized AI agents for complex tasks. Runs in current context (can use AskUserQuestion).

## Usage

```bash
/orchestrator "Build REST API for users"
/orchestrator "Refactor the auth module"
/orchestrator "Fix the failing tests"
```

## Key Difference from /ultrawork

- **`/orchestrator`**: Runs in current context, can interact with user via `AskUserQuestion`
- **`/ultrawork`**: Runs in Ralph loop, autonomous, no user interaction

## Execution

You ARE the Orchestrator now. Apply the workflow:

@include(${CLAUDE_PLUGIN_ROOT}/prompts/orchestrator-workflow.md)

## Task: $ARGUMENTS

Begin:
1. **AskUserQuestion** if anything unclear
2. **TodoWrite** to plan all steps
3. Work, delegating to agents as needed
