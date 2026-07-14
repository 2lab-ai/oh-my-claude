---
name: what-to-work
description: "Use when you do not know what to work on next, the user asks 'what should I work on' / '뭐하지', or a session starts over an existing STV backlog. Routes to what-we-have-to-work when ANY unfinished scenario exists, or plan-new-task when the backlog is empty."
---

# What To Work

## Goal

Provide clear, user-confirmable next work options. Scan `docs/*/trace.md` for unfinished scenarios. If ANY unfinished scenario exists, route to `stv:what-we-have-to-work`. Only when the backlog is empty (or the user explicitly asks for new-feature planning) route to `stv:plan-new-task`.

## Decision Gate (MANDATORY)

**Read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` and apply it to every decision in this workflow.**

Sizing Rubric: read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` (single source — do not duplicate the table here). Sizes below (tiny/small/medium/large/xlarge) refer to expected code change (added + deleted).

## Workflow

1. **Scan trace files**
   - Glob for `docs/*/trace.md` in the project
   - Read each trace.md's Implementation Status table
   - Collect scenarios where Status != "Complete"
   - Estimate size for each unfinished scenario

2. **Decide if work exists**
   - **Execution-eligible**: at least one unfinished scenario exists — ANY size, including tiny/medium tails. Leftover work is never abandoned behind new-feature planning.
   - **Empty backlog**: zero unfinished scenarios, or the user explicitly bypassed the backlog.

3. **Route**
   - If execution-eligible → `Skill(skill="stv:what-we-have-to-work")` to propose 1-3 bundles
   - If empty backlog (or explicit bypass) → `Skill(skill="stv:plan-new-task")` to propose new features

4. **Present next action**
   - State which route you are using and why
   - Ask for any missing context only if it blocks routing

## Error Handling

- Missing or malformed Implementation Status table → report "trace format mismatch: {file}" and stop; never silently fall through to planning.
- Inconsistent status labels across traces → instruct the maintainer to normalize to the `Scenario | Trace | Tests | Verify | Status` schema before routing.
- Empty glob result → verify `docs/` was actually scanned before concluding the backlog is empty; a glob/tooling failure is not an empty backlog.

## Output Template

### Route: what-we-have-to-work

```text
Trace scan complete: {N} features found, {M} unfinished scenarios
Unfinished: {M} scenarios ({sizes})
Total estimated work: {tier}
Route: what-we-have-to-work
Next step: I'll bundle scenarios into up to three options for you to pick.
```

### Route: plan-new-task

```text
Trace scan complete: {summary}
Backlog empty: 0 unfinished scenarios.
Route: plan-new-task
Next step: I'll propose new features based on completed work and project context.
```

## Integration

- Use `stv:what-we-have-to-work` whenever at least one unfinished scenario exists (any size)
- Use `stv:plan-new-task` only when all scenarios are complete or the user explicitly requests new-feature planning
- After user selection, follow `stv:do-work` for execution
