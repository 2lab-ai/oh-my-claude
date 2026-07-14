# stv:new-task — Workflow Spec

> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/new-task/SKILL.md

## 1. Overview (Proposal) — why this workflow exists + what it does

Vague or high-level feature requests ('~만들어줘' with implicit requirements, ideas with multiple
possible approaches) cannot be implemented directly — they lack a spec, a decomposition, and tests.
new-task exists to close that gap: it **transforms vague user requirements into structured STV
artifacts (spec.md + trace.md) with traced scenarios as the task list** (SKILL.md:13). Core
principle: Understand intent deeply → create spec via stv:spec → create trace via stv:trace →
trace.md scenarios = task list (SKILL.md:15). It is an orchestrator, not an implementer.

## 2. Trigger Contract — Use-when / NOT-when (faithful to frontmatter + body)

**Use when** (SKILL.md:3, 19-24): user gives a vague/high-level feature request needing
decomposition — new ideas, '~만들어줘' with implicit requirements, features with multiple possible
approaches; work needs decomposition into implementable scenarios; architectural decisions required
before implementation; work requires structured spec + trace before coding.

**NOT when** (SKILL.md:3, 26-30): specific 1-2 file changes; obvious bug fix with clear solution;
quick clarification / simple question; spec and trace already exist (use `stv:do-work` directly).

## 3. Workflow Trace — input → phases → skills → artifacts

```
vague/high-level request
  → [if ambiguous, not merely high-level: stv:clarify → Context Brief] → feeds Phase 1
  → Phase 1 Intent Understanding (~5min): analyze request + Agent:Explore codebase → context summary
  → Phase 2 Spec Creation: Skill(stv:spec) interview on Phase-1 context → docs/{feature}/spec.md
  → Phase 3 Trace Creation: Skill(stv:trace) per-scenario call-stack trace of spec.md
        → docs/{feature}/trace.md + RED contract tests
  → Phase 4 Summary (~2min): trace.md Implementation Status table = scenario task list
        → user summary (Artifacts / Scenario Task List / Auto-Decisions / Next Step)
```

**Decision Gate (MANDATORY, SKILL.md:32-36):** every decision reads `${CLAUDE_PLUGIN_ROOT}/
prompts/decision-gate.md`; sizing rubric single-sourced there. switching cost < small → autonomous
judgment; >= medium → ask user (SKILL.md:79).

**Exit / handoffs (SKILL.md:121-137):** Next Step → `stv:do-work` per-scenario, OR `stv:work
docs/{feature}/trace.md` direct. INVOKES stv:spec + stv:trace. CALLED BY `stv:plan-new-task` (after
user selects a proposed idea).

## 4. Artifacts & Side Effects

- `docs/{feature}/spec.md` — PRD + Architecture (Phase 2, SKILL.md:80).
- `docs/{feature}/trace.md` — {N} scenarios traced, Implementation Status table (Phase 3, :92).
- {N} RED contract tests — one per scenario (Phase 3, :92).
- User-facing summary block (Phase 4) — not a file; report only.

## 5. Error Paths & NEVER — contract violations (SKILL.md:139-153)

- Skipping Phase 1 → always explore codebase first (plans must be grounded in reality).
- Starting trace without spec → must follow stv:spec → stv:trace order.
- Not treating trace scenarios as tasks → trace.md Implementation Status IS the task list.
- Asking user about trivial things → apply Decision Gate (switching cost < small = autonomous).
- **NEVER** skip/abbreviate stv:spec or stv:trace.
- **NEVER** guide implementation without a trace.
- **NEVER** declare "complete" without a scenario list.

## 6. Acceptance Checklist — a conformant RUN

- [ ] Phase 1 ran Agent:Explore and produced a grounded context summary before any spec.
- [ ] stv:spec was invoked and `docs/{feature}/spec.md` exists.
- [ ] stv:trace was invoked (after spec, in order) → `docs/{feature}/trace.md` + one RED test/scenario.
- [ ] trace.md Implementation Status table is presented as the scenario task list.
- [ ] Every non-trivial decision applied the Decision Gate (autonomous < small, ask >= medium).
- [ ] Final summary names artifacts, scenario list, auto-decisions, and a Next Step handoff.
- [ ] No "complete" claim without a scenario list; no implementation guidance without a trace.

## 7. Improvement Delta (2026-07-14)

- Trigger description narrowed to explicit 'Use when… NOT for…' form (SKILL.md:3) — replacing an
  over-broad Korean matcher that matched almost any instruction; NOT-when now excludes 1-2 file
  changes, obvious bug fixes, quick questions, and already-spec'd work (→ stv:do-work).
- stv:clarify integration added (SKILL.md:134): when a request is *ambiguous* (contradictory goals,
  unclear scope owner) rather than merely high-level, run stv:clarify first and feed its Context
  Brief into Phase 1.
