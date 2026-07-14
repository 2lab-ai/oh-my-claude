---
name: plan-new-task
description: "Use when the trace backlog has ZERO unfinished scenarios (or the user explicitly asks for new feature ideas) and the project needs its next feature proposed. Hands the chosen idea to new-task for spec + trace."
---

# Plan New Task

## Goal

When the backlog is empty (zero unfinished scenarios) — or the user explicitly bypasses remaining work — proactively propose new feature work based on completed features and project context, then create structured STV artifacts using `stv:new-task`.

## Decision Gate (MANDATORY)

**Read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` and apply it to every decision in this workflow.**

Sizing Rubric: read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` (single source — do not duplicate the table here). Sizes below (tiny/small/medium/large/xlarge) refer to expected code change (added + deleted).

## Workflow

1. **Confirm backlog status**
   - Glob for `docs/*/trace.md` in the project
   - Read Implementation Status from each trace.md
   - PRECONDITION: zero unfinished scenarios. If ANY unfinished scenario exists (any size), stop and route back to `stv:what-we-have-to-work` — leftovers are executable work, not carryover to be planned over.
   - Exception: proceed despite leftovers ONLY on an explicit user instruction to plan new work anyway; in that case list the bypassed leftovers at the top of the proposal output.

2. **Review completed work**
   - Scan `docs/*/` directories for completed features
   - Read spec.md and trace.md summaries
   - Identify patterns: what was built, what's missing, what's the natural next step
   - Check git log for recent work context

3. **Propose next work**
   - Suggest two to four candidate features based on:
     - Completed feature history (natural follow-ups)
     - Visible gaps in the codebase
     - User context and project goals
   - Tie each idea to recent work or visible gaps
   - Estimate size tier for each proposal

4. **Present options**

```text
All trace scenarios are complete. Based on project history, here are good next features:

1) {Idea A} ({estimated tier})
   - {one line reason, tied to recent work}

2) {Idea B} ({estimated tier})
   - {one line reason}

3) {Idea C} ({estimated tier})
   - {one line reason}

Bypassed leftovers (explicit user bypass only):
- docs/{feature}/trace.md — Scenario {n}: {title}

Pick a number or describe a different feature.
I will then break it down with stv:new-task.
```

5. **Plan with stv:new-task**
   - After user picks an idea, invoke `Skill(skill="stv:new-task")`
   - stv:new-task handles: intent understanding → stv:spec → stv:trace → scenario task list

6. **Hand off**
   - After spec + trace are created, suggest using `stv:do-work` to execute

## Integration

- `stv:what-to-work` routes here only when the backlog is empty (or the user explicitly bypassed it)
- Use `stv:new-task` for feature decomposition into spec + trace
- Use `stv:do-work` after trace scenarios exist
