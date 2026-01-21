---
description: Use when user provides a SPEC file, feature description, or URL and wants to clarify requirements through interviewing. Triggers on "interview me about", "spec interview", "refine this spec", "create coding plan", "feature planning", or when user shares a specification file and wants detailed discussion.
argument-hint: <spec-file-path | feature-description>
allowed-tools: Read, Write, Edit, Glob, AskUserQuestion, TodoWrite, WebFetch
---

@include(${CLAUDE_PLUGIN_ROOT}/.commands-body/spec-interview.md)
