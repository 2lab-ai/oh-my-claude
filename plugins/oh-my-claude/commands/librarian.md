---
description: "Search external docs, best practices, library APIs using Librarian agent (Opus 4.5)"
argument-hint: "QUESTION"
allowed-tools:
  - Task
  - TaskOutput
  - Read
  - Grep
  - Glob
  - Bash
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - mcp__plugin_context7_context7__resolve-library-id
  - mcp__plugin_context7_context7__query-docs
---

**Always read commands body** even if you knew it.**

@include(${CLAUDE_PLUGIN_ROOT}/.commands-body/librarian.md)
