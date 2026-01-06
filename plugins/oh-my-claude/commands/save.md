---
description: Save current work context, plan, and todos to ./docs/tasks/save/{id}
allowed-tools: Read, Write, Bash(date:*), Bash(mkdir:*)
---

# /save - Save Work Context

## Task

Save the current work context to `./docs/tasks/save/{id}` where `{id}` is a timestamp-based ID.

## Steps

1. Generate ID from current timestamp: `!date '+%Y%m%d_%H%M%S'`
2. Create the save directory: `./docs/tasks/save/{generated_id}/`
3. Create `context.md` file with the following sections:

### context.md Structure

```markdown
# Work Context Save
- **ID**: {generated_id}
- **Date**: {current datetime}
- **Branch**: {current git branch}

## Summary
{Brief 1-2 sentence description of current work}

## Current Plan
{Copy the current plan from conversation if available}

## In Progress Tasks
{List tasks currently being worked on}

## Completed Tasks
{List tasks that have been completed in this session}

## Pending Tasks
{List tasks that still need to be done}

## Key Context
{Important files, decisions, or context needed to continue}

## Files Modified
{List of files created or modified in this session}

## Notes
{Any additional notes or considerations}
```

4. If there are specific plan files (e.g., in `./docs/agent_tasks/`), reference or copy relevant content.

5. Return the save ID and path to the user:
   ```
   Saved to: ./docs/tasks/save/{id}/context.md
   Load with: /load {id}
   ```

## Important

- Capture ALL relevant context needed to resume work
- Include specific file paths with line numbers when relevant
- Include any error messages or blockers encountered
- Be thorough - the goal is to enable seamless work resumption
