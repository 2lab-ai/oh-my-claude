---
description: "Ask Oracle (GPT-5.2) for architecture advice, design decisions, or failure analysis"
argument-hint: "QUESTION"
allowed-tools:
  - Task
  - TaskOutput
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - mcp__plugin_ohmyclaude_gpt-as-mcp__codex
  - mcp__plugin_ohmyclaude_gpt-as-mcp__codex-reply
---

@include(${CLAUDE_PLUGIN_ROOT}/.commands-body/oracle.md)
