# stv:plan-new-task — Workflow Spec

> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/plan-new-task/SKILL.md

## 1. Overview (Proposal)

When the trace backlog holds ZERO unfinished scenarios — or the user explicitly bypasses remaining
work — the project has nothing left to execute but still needs a next move. plan-new-task exists to
**proactively propose new feature work grounded in completed features + project context, then hand
the chosen idea to `stv:new-task` for spec + trace** (SKILL.md:10). It is a proposer/router, not an
implementer: it surfaces 2-4 sized candidates and delegates decomposition.

## 2. Trigger Contract — PRECONDITION zero unfinished scenarios (or explicit user bypass)

Enter only when every `docs/*/trace.md` Implementation Status shows zero unfinished scenarios
(SKILL.md:3, 20-23), OR the user explicitly asks for new feature ideas / instructs to plan anyway
despite leftovers (SKILL.md:3, 24). `stv:what-to-work` routes here only under this condition
(SKILL.md:70). Any unfinished scenario of any size without an explicit bypass = do NOT enter.

## 3. Workflow Trace

```
backlog confirm (Glob docs/*/trace.md → read Impl Status → PRECONDITION: zero unfinished, SKILL.md:20-23)
  → [ANY unfinished scenario, no bypass] → route back to stv:what-we-have-to-work (leftovers = executable work)
  → completed-work review (scan docs/*/ spec.md+trace.md summaries + patterns + git log context, :26-30)
  → propose 2-4 candidates (tied to recent work / visible gaps / project goals, each size-tiered, :32-38)
  → present options block (numbered ideas + tiers; Bypassed-leftovers list only under explicit bypass, :40-59)
  → user picks a number / describes a different feature
  → Skill(stv:new-task): intent → stv:spec → stv:trace → scenario task list (:61-63)
  → hand off: suggest stv:do-work to execute (:65-66)
```

**Decision Gate (MANDATORY, SKILL.md:12-16):** every decision reads `${CLAUDE_PLUGIN_ROOT}/prompts/
decision-gate.md`; sizing rubric (tiny/small/medium/large/xlarge over added+deleted) single-sourced there.

## 4. Artifacts & Side Effects

- No files written by plan-new-task itself — it only reads (`docs/*/trace.md`, `docs/*/spec.md`, git log).
- User-facing proposal block (Section-4 template, SKILL.md:42-59) — report only, not a file.
- Downstream side effects (`docs/{feature}/spec.md` + `trace.md` + RED tests) are produced by the
  delegated `stv:new-task`, not here.

## 5. Error Paths & NEVER

- **NEVER** enter planning while executable leftovers exist without an explicit user bypass — leftovers
  are executable work, not carryover to be planned over; stop and route back to `stv:what-we-have-to-work`
  (SKILL.md:23).
- Proceeding despite leftovers requires an explicit user instruction; when bypassed, list the bypassed
  leftovers at the top of the proposal output (SKILL.md:24, 54-56).
- Proposing without grounding → each candidate must tie to recent work or a visible gap (SKILL.md:37).

## 6. Acceptance Checklist

- [ ] Globbed `docs/*/trace.md` and confirmed zero unfinished scenarios before proposing.
- [ ] If any unfinished scenario existed, either routed back to `stv:what-we-have-to-work` or recorded an explicit user bypass.
- [ ] Reviewed completed work (docs/*/ summaries + git log) before candidates.
- [ ] Presented 2-4 candidates, each with a size tier and a reason tied to recent work / gaps.
- [ ] Bypassed-leftovers block present ONLY when an explicit bypass occurred.
- [ ] After user pick, invoked `stv:new-task`; suggested `stv:do-work` handoff.

## 7. Improvement Delta (2026-07-14)

- Precondition tightened from "no meaningful unfinished work" to **ZERO unfinished scenarios** of any
  size (SKILL.md:3, 23) — removing the subjective "meaningful" escape hatch.
- Leftovers now route back to `stv:what-we-have-to-work` as executable work instead of being planned
  over (SKILL.md:23).
- Carryover block renamed to **"Bypassed leftovers (explicit user bypass only)"** (SKILL.md:54) —
  making the bypass an explicit, user-owned exception rather than an implicit carryover.
