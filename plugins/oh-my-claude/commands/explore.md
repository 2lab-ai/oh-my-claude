---
description: "Search THIS codebase using Explore agent (Gemini). Find implementations, patterns, code flow."
argument-hint: "QUESTION"
allowed-tools:
  - Task
  - TaskOutput
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - mcp__plugin_ohmyclaude_gemini-as-mcp__gemini
  - mcp__plugin_ohmyclaude_gemini-as-mcp__gemini-reply
---

# /explore - Internal Codebase Explorer

Search the current codebase directly. Runs in current context (can use AskUserQuestion).

## Usage

```bash
/explore "Where is authentication implemented?"
/explore "How does the routing work?"
/explore "Find all usages of UserService"
```

## Execution

You ARE the Explorer now. Apply the Explore persona:

@include(${CLAUDE_PLUGIN_ROOT}/prompts/explore-persona.md)

## Task: $ARGUMENTS

**If search scope is unclear, use AskUserQuestion FIRST.**

Search fast. Report findings with file:line references.
