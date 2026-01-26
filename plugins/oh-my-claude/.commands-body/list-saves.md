# /list-saves - List Saved Work Contexts

## Task

Display all saved work contexts from `.claude/omc/tasks/save/` with summary info, filtered by current branch, and provide interactive selection.

## Steps

1. Get current git branch: `git rev-parse --abbrev-ref HEAD`
2. List all directories in `.claude/omc/tasks/save/`
3. For each save, read the first few lines of `context.md` to extract:
   - Save ID (directory name)
   - Date
   - Summary
   - Branch
4. Filter and categorize:
   - **Current branch saves**: Saves matching current branch (primary display)
   - **Other branch saves**: Saves from different branches (show with warning)
5. Display in a formatted table with branch match indicator
6. Use `AskUserQuestion` to let user select a save to load:
   - Options: List of save IDs (current branch saves first)
   - Include "Cancel" option

## Output Format

```
## Saved Work Contexts

**Current Branch**: {current_branch}

### Matching Saves (same branch)
| ID | Date | Summary |
|----|------|---------|
| 20241230_191500 | 2024-12-30 19:15 | Refactoring crypto options |

### Other Branches
| ID | Date | Branch | Summary |
|----|------|--------|---------|
| 20241229_143000 | 2024-12-29 14:30 | main | Bug fix for withdrawal |

Total: {count} saves ({matching} on current branch)
```

## Interactive Selection

After displaying the list, use `AskUserQuestion`:
- Question: "Which save would you like to load?"
- Options: List save IDs (current branch saves prioritized)
- If user selects a save, automatically run `/load {id}`

## If No Saves Found

```
No saved work contexts found.

Use `/save` to save your current work context.
```
