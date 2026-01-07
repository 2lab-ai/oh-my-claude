# /status - Ralph Loop Status

Check if a Ralph loop is active and show its status.

## Steps

1. Check if `.claude/ralph-loop.local.md` exists:
   ```bash
   test -f .claude/ralph-loop.local.md && echo "ACTIVE" || echo "INACTIVE"
   ```

2. **If INACTIVE**: Say "No active Ralph loop."

3. **If ACTIVE**: Read `.claude/ralph-loop.local.md` and display:

### Output Format

```
Ralph Loop Status
═════════════════════════════════════════
State:      ACTIVE
Iteration:  {iteration} / {max_iterations or "unlimited"}
Started:    {started_at} ({time elapsed})
Promise:    {completion_promise or "none"}
═════════════════════════════════════════

To cancel: /cancel-work
```

### Field Extraction

From the YAML frontmatter:
- `iteration:` → Current iteration number
- `max_iterations:` → Max iterations (0 = unlimited)
- `started_at:` → Start timestamp
- `completion_promise:` → Promise text (or "null")

Calculate elapsed time from `started_at` to now.
