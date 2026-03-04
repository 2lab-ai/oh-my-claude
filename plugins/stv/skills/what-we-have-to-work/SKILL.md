---
name: what-we-have-to-work
description: "Bundle unfinished trace scenarios into up to three candidate work chunks, present options with rationale, and get user confirmation before starting do-work execution."
---

# What We Have To Work

## Goal

Turn unfinished scenarios from `docs/*/trace.md` into up to three clear work bundles and get a fast user selection.

## Sizing Rubric (expected code change, added + deleted)

| Tier   | Lines  | Example                                    |
|--------|--------|--------------------------------------------|
| tiny   | ~5     | Config values, constants, string literals   |
| small  | ~20    | One function, one file, local refactor      |
| medium | ~50    | Multiple files, interface changes           |
| large  | ~100   | Cross-cutting concerns, schema migrations   |
| xlarge | ~500   | Architecture shift, framework replacement   |

## Workflow

1. **Survey trace scenarios**
   - Glob for `docs/*/trace.md` in the project
   - Read Implementation Status table from each trace.md
   - Collect unfinished scenarios with their feature, dependencies, and size estimate
   - Note which features have specs (docs/{feature}/spec.md)

2. **Check bundle viability**
   - Bundle-worthy means you can form at least one large or xlarge bundle
   - Target xlarge (~500 lines) and do not exceed xlarge
   - If only tiny/medium scenarios remain, or total expected change is below large, stop and switch to `stv:plan-new-task`

3. **Build bundles**
   - Create one to three bundles, not more
   - Do not force three bundles if the backlog is small
   - Aim for xlarge bundles; large is acceptable if xlarge would require unrelated work
   - Do not exceed xlarge
   - Prefer grouping by: feature (same trace.md), dependency chain, shared code area
   - Include tiny leftover scenarios only as add-ons, not as standalone bundles
   - Do not mix unrelated features just to hit size targets

4. **Present options**

```text
I found {N} unfinished scenarios across {M} features. Here are the bundles:

1) {Bundle title} ({size tier})
   Feature: {feature-name} (docs/{feature}/trace.md)
   - Scenario {n}: {title}
   - Scenario {m}: {title}
   Rationale: {short reason}

2) ...
3) ...

Reply with 1, 2, or 3 and any extra context.
If you want a different bundle, say what to include.
```

5. **After user selection**
   - Confirm the selected bundle
   - Invoke `Skill(skill="stv:do-work")` with the selected trace and scenarios

6. **Empty or tiny backlog**
   - If you cannot form a large/xlarge bundle, stop and invoke `Skill(skill="stv:plan-new-task")`

## Integration

- Use `stv:what-to-work` for routing decisions (it calls this skill)
- Use `stv:plan-new-task` if all scenarios are complete or remaining work is too small
- Use `stv:do-work` after the user picks a bundle
