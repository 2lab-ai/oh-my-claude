---
name: what-we-have-to-work
description: "Use when unfinished trace scenarios exist and the next execution scope must be chosen. Bundles leftovers of ANY size into 1-3 options and hands the selected bundle contract (trace_path + scenario_ids) to do-work."
---

# What We Have To Work

## Goal

Turn unfinished scenarios from `docs/*/trace.md` into up to three clear work bundles and get a fast user selection.

## Decision Gate (MANDATORY)

**Read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` and apply it to every decision in this workflow.**

Sizing Rubric: read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` (single source — do not duplicate the table here). Sizes below (tiny/small/medium/large/xlarge) refer to expected code change (added + deleted).

## Workflow

1. **Survey trace scenarios**
   - Glob for `docs/*/trace.md` in the project
   - Read Implementation Status table from each trace.md
   - Collect unfinished scenarios with their feature, dependencies, and size estimate
   - Note which features have specs (docs/{feature}/spec.md)

2. **Shape the backlog into bundles**
   - Every unfinished scenario is execution-eligible — small and medium tails included. Do NOT reroute to plan-new-task just because the backlog is small.
   - Target large/xlarge bundles when the backlog allows; a single small/medium leftover is still a valid bundle on its own.
   - Never exceed xlarge per bundle.

3. **Build bundles**
   - Create one to three bundles, not more
   - Do not force three bundles if the backlog is small
   - Aim for xlarge bundles; large is acceptable if xlarge would require unrelated work
   - Do not exceed xlarge
   - Prefer grouping by: feature (same trace.md), dependency chain, shared code area
   - Attach tiny leftovers as add-ons to related bundles when possible; if nothing related exists, a leftover-sweep bundle of small scenarios is valid
   - Do not mix unrelated features just to hit size targets

4. **Present options**

```text
I found {N} unfinished scenarios across {M} features. Here are the bundles:

1) {Bundle title} ({size tier})
   Feature: {feature-name} (docs/{feature}/trace.md)
   - Scenario {n}: {title}
   - Scenario {m}: {title}
   Rationale: {short reason}
   Contract: {"trace_path": "docs/{feature}/trace.md", "scenario_ids": ["n", "m"], "size": "{tier}", "rationale": "{short reason}"}

2) ...
3) ...

Reply with 1, 2, or 3 and any extra context.
If you want a different bundle, say what to include.
```

5. **After user selection**
   - Confirm the selected bundle
   - Invoke `Skill(skill="stv:do-work")` passing the selected bundle contract verbatim — `trace_path` and `scenario_ids` MUST survive the handoff unchanged; do-work must not rescan the project when this contract is provided.
   - Validate before handoff: `trace_path` resolves to an existing trace file and every `scenario_ids` entry exists in that trace's Implementation Status; on mismatch, stop with a targeted-scope error instead of handing off.

6. **Empty backlog**
   - Only if ZERO unfinished scenarios exist, stop and invoke `Skill(skill="stv:plan-new-task")`.

## Integration

- Use `stv:what-to-work` for routing decisions (it calls this skill)
- Use `stv:plan-new-task` only when zero unfinished scenarios remain
- Use `stv:do-work` after the user picks a bundle
