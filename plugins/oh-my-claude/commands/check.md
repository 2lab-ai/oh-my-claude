---
description: Verify completion status of archived saves in .claude/omc/tasks/archives/
argument-hint: [all | archive-id]
allowed-tools: Bash(ls:*), Bash(git log:*), Bash(git diff:*), Read, Glob, Edit, Write
---

@include(${CLAUDE_PLUGIN_ROOT}/.commands-body/check.md)
