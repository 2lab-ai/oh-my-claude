# /check - Verify Archived Save Completion

## Task

Review archived work contexts from `.claude/omc/tasks/archives/` and verify whether the planned tasks were actually completed.

## Arguments

- **No argument**: Check only the **most recent** archive (sorted by directory name, newest first)
- **`all`**: Check **all** archives in chronological order
- **`{archive-id}`**: Check specific archive: `.claude/omc/tasks/archives/{archive-id}/context.md`

## Steps

1. **Determine target archives**:
   ```bash
   # List all archives sorted by name (newest first)
   ls -1 .claude/omc/tasks/archives/ | sort -r
   ```
   - If `$1` is empty: select only the **first** (most recent) archive
   - If `$1` is `all`: select all archives
   - Otherwise: select `.claude/omc/tasks/archives/$1/context.md`

2. **For each archive, read the context**:
   - Parse the context.md file
   - Extract: Summary, Current Plan, Pending Tasks, Files Modified

3. **Verify completion**:
   - Check git log for commits related to the plan
   - Check if mentioned files exist and were modified
   - Compare planned tasks vs actual implementation

4. **Generate report** and display to user

5. **Update the archive's context.md**:
   - Append `## Verification` section at the end
   - Include task completion status table
   - Add **signature with date** when all tasks are verified

## Output Format (display to user)

```
## Archive Verification: {id}

**Archived Date**: {date}
**Branch**: {branch}
**Summary**: {summary}

### Task Completion Status

| Task | Status | Evidence |
|------|--------|----------|
| Task 1 description | Completed | Commit abc123, file modified |
| Task 2 description | Incomplete | No matching commits found |
| Task 3 description | Partial | File exists but missing feature X |

### Verification Summary
- **Completed**: {n}/{total} tasks
- **Incomplete**: {list of incomplete tasks}

### Recommended Actions
- {action 1 if incomplete tasks exist}
- {action 2}
```

## Update context.md Format

After verification, append this section to the archive's `context.md`:

```markdown
---

## Verification

**Verified**: {YYYY-MM-DD HH:MM:SS KST}
**Status**: {Completed | Partial | Incomplete}
**Completed**: {n}/{total} tasks

### Task Verification

| Task | Status | Evidence |
|------|--------|----------|
| Task 1 | Completed | Commit abc123 |
| Task 2 | Incomplete | File not found |

### Incomplete Items
- {list if any}

### Signature
Verified by Claude Code on {YYYY-MM-DD}.
All planned tasks have been {confirmed complete | partially implemented - see incomplete items above}.
```

## Verification Methods

1. **Git log check**: Search for commits mentioning task keywords
   ```bash
   git log --oneline --since="{archive_date}" --grep="{keyword}"
   ```

2. **File existence**: Verify planned files were created/modified
   ```bash
   ls -la {file_path}
   git diff --stat {commit_range} -- {file_path}
   ```

3. **Content verification**: Read files to confirm implementation matches plan

## Status Definitions

- **Completed**: All pending tasks from the archive have been implemented and verified
- **Partial**: Some tasks completed, some remain incomplete
- **Incomplete**: Most or all tasks remain unimplemented

## If No Archives Found

```
No archived work contexts found.

Archives are created when you load a saved context using `/load`.
```

## Examples

```bash
/check          # Check most recent archive only
/check all      # Check all archives
/check 20260102_172621  # Check specific archive
```
