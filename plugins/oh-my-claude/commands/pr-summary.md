---
description: "Generate multi-perspective PR Executive Summary for stakeholders"
argument-hint: "PR_NUMBER_OR_URL [--stakeholders=auto|all] [--format=markdown|slack]"
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Task
  - TaskOutput
  - TodoWrite
  - AskUserQuestion
  - mcp__plugin_ohmyclaude_gpt-as-mcp__codex
  - mcp__plugin_ohmyclaude_gpt-as-mcp__codex-reply
  - mcp__plugin_ohmyclaude_gemini-as-mcp__gemini
  - mcp__plugin_ohmyclaude_gemini-as-mcp__gemini-reply
---

@include(${CLAUDE_PLUGIN_ROOT}/.commands-body/pr-summary.md)
