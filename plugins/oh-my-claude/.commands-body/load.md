# /load - Load Saved Work Context

## Task

Load a previously saved work context from `.claude/omc/tasks/save/$1` and resume work.

## Steps

1. **Locate the save file**:
   - If `$1` is provided, read `.claude/omc/tasks/save/$1/context.md`
   - If `$1` is empty, **automatically load the most recent save** (by timestamp in directory name)
   - If no saves exist, inform the user

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
   - Create archived directory if not exists: `mkdir -p .claude/omc/tasks/archives/`
   - Move the loaded save to archived: `mv .claude/omc/tasks/save/{id} .claude/omc/tasks/archives/{id}`
   - This prevents re-loading the same context and keeps save folder clean

6. **Track loaded save for context chaining**:
   - Remember the loaded save ID (`{id}`) for this session
   - When `/save` is called later, the loaded save ID will be referenced in "Previous Context History"
   - Also note any existing "Previous Context History" from the loaded save to carry forward

## Output Format

```
## Loaded Context: {id}

**Saved**: {date}
**Branch**: {saved branch} → {current branch}
**Archived to**: `.claude/omc/tasks/archives/{id}/context.md`

### Context Chain
{If the loaded save had previous context history, show the chain:}
- Previous saves in this work chain: {count}
- Original save: `{oldest_id}` ({oldest_summary})
{If no previous context:}
- This was the first save in this work chain

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

- **No argument provided**: Automatically load the most recent save (sorted by directory name descending)
- **Save not found**: List available saves with `ls .claude/omc/tasks/save/`
- **No saves exist**: Inform user "No saved contexts found"
- **Branch mismatch**: Warn user and ask to proceed
- **File conflicts**: List changed files and ask for guidance
- **Unclear next step**: Ask user to clarify priority

## Important

- **ALWAYS use `TodoWrite`** immediately after loading - user must see the task list to verify context was loaded correctly
- Always use `AskUserQuestion` when context is ambiguous
- Don't assume - verify the current state matches expectations
- Give user control over which task to continue with
