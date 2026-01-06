---
description: Load saved work context from ./docs/tasks/save/{id}
argument-hint: <save-id>
allowed-tools: Read, Glob, Bash(ls:*), Bash(mv:*), Bash(mkdir:*), AskUserQuestion, TodoWrite
---

# /load - Load Saved Work Context

## Task

Load a previously saved work context from `./docs/tasks/save/$1` and resume work.

## Steps

1. **Locate the save file**:
   - If `$1` is provided, read `./docs/tasks/save/$1/context.md`
   - If `$1` is empty or not found, list available saves and ask user to select one

2. **Read the context file**:
   - Parse the saved context.md file
   - Understand the work state, plan, and pending tasks

3. **Validate and clarify**:
   - Check if referenced files still exist
   - Check if the git branch matches or has diverged
   - Use `AskUserQuestion` to clarify any ambiguities:
     - "The branch has changed since saving. Continue on current branch?"
     - "Some referenced files have changed. Review changes before continuing?"
     - "Multiple pending tasks found. Which should we prioritize?"

4. **Resume work** (MUST use TodoWrite):
   - **MANDATORY**: Use `TodoWrite` tool to populate the todo list with ALL pending tasks from the saved context
   - This is required so the user can visually verify the loaded tasks match their expectations
   - Summarize the loaded context to the user
   - Ask for confirmation to proceed with the next pending task

5. **Archive the loaded save**:
   - Create archived directory if not exists: `mkdir -p ./docs/tasks/archived/`
   - Move the loaded save to archived: `mv ./docs/tasks/save/{id} ./docs/tasks/archived/{id}`
   - This prevents re-loading the same context and keeps save folder clean

## Output Format

```
## Loaded Context: {id}

**Saved**: {date}
**Branch**: {saved branch} → {current branch}

### Summary
{summary from saved context}

### Pending Tasks
1. {task 1}
2. {task 2}
...

### Ready to Resume
{Next recommended action}
```

## Handling Edge Cases

- **Save not found**: List available saves with `ls ./docs/tasks/save/`
- **Branch mismatch**: Warn user and ask to proceed
- **File conflicts**: List changed files and ask for guidance
- **Unclear next step**: Ask user to clarify priority

## Important

- **ALWAYS use `TodoWrite`** immediately after loading - user must see the task list to verify context was loaded correctly
- Always use `AskUserQuestion` when context is ambiguous
- Don't assume - verify the current state matches expectations
- Give user control over which task to continue with
