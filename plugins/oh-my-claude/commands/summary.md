---
description: "Advanced summarization"
argument-hint: "CONTENT_PATH [--output=executive|action|role] [--role=engineer|marketer|founder] [--depth=quick|deep]"
allowed-tools:
  - Task
  - TaskOutput
  - TodoWrite
  - AskUserQuestion
  - Read
  - Grep
  - Glob
  - Write
  - Bash
  - mcp__plugin_ohmyclaude_claude-as-mcp__chat
  - mcp__plugin_ohmyclaude_claude-as-mcp__chat-reply
  - mcp__plugin_ohmyclaude_gemini-as-mcp__gemini
  - mcp__plugin_ohmyclaude_gemini-as-mcp__gemini-reply
  - mcp__plugin_ohmyclaude_gpt-as-mcp__codex
  - mcp__plugin_ohmyclaude_gpt-as-mcp__codex-reply
---

@include(${CLAUDE_PLUGIN_ROOT}/.commands-body/summary.md)
