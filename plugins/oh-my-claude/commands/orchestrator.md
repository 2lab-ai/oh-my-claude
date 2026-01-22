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

**Always read commands body** even if you knew it.**

@include(${CLAUDE_PLUGIN_ROOT}/.commands-body/orchestrator.md)
