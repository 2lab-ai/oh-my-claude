# /save - Save Work Context

## Task

Save the current work context to `.claude/omc/tasks/save/{id}` where `{id}` is a timestamp-based ID.

## Steps

1. Generate ID from current timestamp: `!date '+%Y%m%d_%H%M%S'`
2. Create the save directory: `.claude/omc/tasks/save/{generated_id}/`

3. **Check for previously loaded save in this session**:
   - If a save was loaded earlier (via `/load`), note its ID
   - Ensure it's archived: check `.claude/omc/tasks/archives/{loaded_id}/context.md`
   - If the loaded save is still in `.claude/omc/tasks/save/`, move it to archives first
   - Read the loaded save's `context.md` to extract its "Previous Context History" if any

4. Create `context.md` file with the following sections:

### context.md Structure

```markdown
# Work Context Save
- **ID**: {generated_id}
- **Date**: {current datetime}
- **Branch**: {current git branch}

## Previous Context History
{List of previously linked saves in chronological order. If this is the first save, write "(First save - no previous context)"}
{If there was a loaded save, add a new line:}
- `{loaded_id}` - {loaded_save_summary} → `.claude/omc/tasks/archives/{loaded_id}/context.md`
{Copy any existing history lines from the loaded save's "Previous Context History" section ABOVE the new entry}

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

### Previous Context History Format

The history section accumulates with each save/load cycle:

**First save (no prior load):**
```markdown
## Previous Context History
(First save - no previous context)
```

**After loading save `20250126_100000` and saving again:**
```markdown
## Previous Context History
- `20250126_100000` - Initial feature implementation → `.claude/omc/tasks/archives/20250126_100000/context.md`
```

**After loading save `20250126_120000` (which had its own history) and saving again:**
```markdown
## Previous Context History
- `20250126_100000` - Initial feature implementation → `.claude/omc/tasks/archives/20250126_100000/context.md`
- `20250126_120000` - Added unit tests → `.claude/omc/tasks/archives/20250126_120000/context.md`
```

5. If there are specific plan files (e.g., in `./docs/agent_tasks/`), reference or copy relevant content.

6. Return the save ID and path to the user:
   ```
   Saved to: .claude/omc/tasks/save/{id}/context.md
   Load with: /load {id}
   ```

## Important

- Capture ALL relevant context needed to resume work
- Include specific file paths with line numbers when relevant
- Include any error messages or blockers encountered
- Be thorough - the goal is to enable seamless work resumption
- **Always preserve the Previous Context History chain** - this enables tracing back through the entire work history
