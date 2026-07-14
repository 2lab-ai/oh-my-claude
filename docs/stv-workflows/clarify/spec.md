# stv:clarify — Workflow Spec

> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/clarify/SKILL.md

## 1. Overview (Proposal)

clarify resolves ambiguity BEFORE any feature is committed to. It runs a two-track loop — a
sequential, adaptive user Q&A on one track and a parallel codebase-exploration subagent on the
other — and converges on a single **Context Brief**. The Brief captures Goal, Scope, Technical
Context, Constraints, Success Criteria, Open Questions, and a Complexity Assessment, and becomes
the SSOT for whatever work follows (implementation, planning, stv:debug, stv:new-task).

## 2. Trigger Contract — and the boundary vs stv:spec interview (sequential-adaptive vs bundled)

- **Trigger:** the user's request is ambiguous — vague asks, polysemous instructions, or unclear
  scope — and no feature commitment has been made yet.
- **Boundary vs stv:spec:** clarify asks **one question at a time** because it runs BEFORE the
  problem is known — each answer can invalidate the next question, so questions must be sequential
  and adaptive. stv:spec instead **bundles 2-4 related questions** into one AskUserQuestion because
  it runs AFTER clarity exists and optimizes for user time.
- **Hand-off signal:** if you catch yourself wanting to bundle questions in clarify, you already
  have enough clarity — stop and hand off to stv:spec or stv:new-task.

## 3. Workflow Trace

```
vague request
  → ambiguity assessment (what's ambiguous?)
  → [Track1: ONE question → answer]  ∥  [Track2: Explore subagent → findings]
  → synthesize (cross-validate answers against findings)
  → loop until resolved (pick next question by scope impact; launch more subagents as needed)
  → Context Brief
       Goal / Scope / Technical Context / Constraints / Success Criteria / Open Questions
       Complexity Assessment: 5-signal score (scope breadth, file impact, interface boundaries,
         dependency depth, risk surface) → Simple (5-8) | Complex (9-15)
  → confirmation
  → handoff (implementation / planning / stv:debug / stv:new-task)
```

Track 2 runs in parallel: a subagent is launched immediately after each user question; its findings
merge into the current or next synthesis cycle.

## 4. Artifacts & Side Effects

- **Context Brief** — the skill's only deliverable, presented inline to the user.
- The confirmed Brief is saved as `docs/{feature}/clarification.md` (CWD-relative) **by the
  follow-up work**, not by clarify itself — same artifact home as spec.md / trace.md.
- No other side effects: clarify does not write code or touch git.

## 5. Error Paths & NEVER

- If an answer **contradicts** a previous one, flag it immediately and realign — never silently
  overwrite the earlier answer.
- Ask **"which case?"** (concrete scenarios), NEVER **"why?"** (abstract intent).
- NEVER bundle multiple questions into one message in clarify — that belongs to stv:spec.
- Subagents report key findings concisely; NEVER dump entire file contents.

## 6. Acceptance Checklist

- [ ] Trigger fires only on ambiguous, pre-commitment requests.
- [ ] Questions are sequential (one per message) and adapt to each prior answer.
- [ ] A parallel Explore subagent is dispatched and its findings cross-validated.
- [ ] Contradictions are flagged on the spot.
- [ ] The Context Brief includes all 7 sections plus a 5-signal complexity score with Simple/Complex verdict.
- [ ] The Brief is confirmed by the user before handoff.

## 7. Improvement Delta (2026-07-14)

- Description made trigger-based English (was Korean "유저의 요구가 불명확할때 트리거…").
- Question-policy boundary vs stv:spec documented: sequential-adaptive (clarify) vs bundled (spec).
- Brief save location fixed to `docs/{feature}/clarification.md`; final section unified to English
  ("After the Brief").
