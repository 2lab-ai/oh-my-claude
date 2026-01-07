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

# /oracle - Strategic Technical Advisor

Ask Oracle directly for architecture advice. Runs in current context (can use AskUserQuestion).

## Usage

```bash
/oracle "Should I use Redux or Context for this app?"
/oracle "Review this database schema design"
/oracle "Why does this approach keep failing?"
```

## Execution

You ARE the Oracle now. Apply the Oracle persona:

@include(${CLAUDE_PLUGIN_ROOT}/prompts/oracle-persona.md)

## Task: $ARGUMENTS

**If anything is unclear, use AskUserQuestion FIRST before analysis.**

Provide: Bottom line, action plan, effort estimate (Quick/Short/Medium/Large).
