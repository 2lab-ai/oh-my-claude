# stv:what-to-work — Workflow Spec
> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/what-to-work/SKILL.md

## 1. Overview (Proposal)
A router that answers "what should I work on next" without doing work itself. It scans the STV
backlog (`docs/*/trace.md`) for unfinished scenarios and hands off to exactly one downstream skill.
Goal: give the user clear, confirmable next-work options while never abandoning leftover work.

## 2. Trigger Contract
Fires when: the user does not know what to work on next, asks "what should I work on" / "뭐하지",
or a session starts over an existing STV backlog. The description is trigger-based (WHEN + routing
outcome), not a capability blurb.

## 3. Workflow Trace
`docs/*/trace.md rows → unfinishedInventory[] → routeDecision`
1. **Scan** — Glob `docs/*/trace.md`; read each Implementation Status table; collect scenarios
   with Status != "Complete"; estimate size per scenario (tiny…xlarge, per the decision-gate
   sizing rubric — single source in `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md`).
2. **Decide** — `unfinishedInventory` non-empty (ANY size, including tiny/medium tails) =
   execution-eligible; zero scenarios OR explicit user bypass = empty backlog.
3. **Route** — execution-eligible → `Skill(stv:what-we-have-to-work)` (propose 1-3 bundles);
   empty/bypass → `Skill(stv:plan-new-task)` (propose new features).
4. **Present** — state the chosen route and why; ask for missing context only if it blocks routing.

Error Handling branches (each halts routing — never silently fall through to planning):
- Missing/malformed Implementation Status table → report "trace format mismatch: {file}" and stop.
- Inconsistent status labels across traces → instruct maintainer to normalize to the
  `Scenario | Trace | Tests | Verify | Status` schema before routing.
- Empty glob result → verify `docs/` was actually scanned; a glob/tooling failure is NOT an
  empty backlog.

## 4. Artifacts & Side Effects
None created. This skill is routing-only: it reads trace files and emits a route decision plus an
output-template summary. No files written, no backlog mutated, no downstream execution performed here.

## 5. Error Paths & NEVER
- NEVER route to `plan-new-task` while any unfinished scenario exists (leftover tails are not
  abandoned behind new-feature planning).
- NEVER treat a glob/tooling failure or an unscanned `docs/` as an empty backlog.
- NEVER silently fall through on a malformed or inconsistently-labeled trace table — report and stop.
- NEVER duplicate the sizing rubric; defer to `prompts/decision-gate.md`.

## 6. Acceptance Checklist
- [ ] Globs `docs/*/trace.md` and reads every Implementation Status table.
- [ ] Any unfinished scenario (any size) → `stv:what-we-have-to-work`.
- [ ] Empty backlog or explicit bypass → `stv:plan-new-task`.
- [ ] Chosen route and reason stated to the user; blocking-only clarification.
- [ ] All three Error Handling branches halt instead of defaulting to planning.
- [ ] No files created or backlog mutated (routing-only).

## 7. Improvement Delta (2026-07-14)
- Routing rule changed from "large/xlarge bundle-worthy else plan-new-task" to "ANY unfinished
  scenario routes to execution" — leftover tails are never abandoned behind new planning.
- Error Handling section added (trace format mismatch, inconsistent labels, glob failure ≠ empty).
- Description made trigger-based (WHEN + routing outcome) rather than capability-descriptive.
