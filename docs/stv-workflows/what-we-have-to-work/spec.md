# stv:what-we-have-to-work — Workflow Spec
> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/what-we-have-to-work/SKILL.md

## 1. Overview (Proposal)
Turn unfinished trace scenarios into up to three clear work bundles and get a fast user selection, then hand the chosen bundle contract to `stv:do-work`. Scope selection only — no code is written here. Called by `stv:what-to-work` for routing.

## 2. Trigger Contract
Fires when unfinished trace scenarios exist and the next execution scope must be chosen. Input surface = `docs/*/trace.md` (Implementation Status tables). No caller-supplied contract; this skill produces one. Sizing rubric is the single source in `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` (tiny/small/medium/large/xlarge = expected added+deleted code change); do not duplicate it.

## 3. Workflow Trace
`unfinished scenarios → 1-3 bundles → user selection → bundle contract {"trace_path","scenario_ids","size","rationale"} → validation (trace_path resolves, every id exists) → stv:do-work handoff (contract survives verbatim)`

Steps: (1) Glob `docs/*/trace.md`, read each Implementation Status table, collect unfinished scenarios with feature, dependencies, size estimate; note which have `docs/{feature}/spec.md`. (2) Shape backlog into bundles. (3) Build 1-3 bundles. (4) Present options. (5) On selection, confirm and hand off. (6) Empty backlog → plan-new-task.

Bundling rules:
- Every unfinished scenario is execution-eligible — any size, small/medium tails included; do NOT reroute to plan-new-task just because the backlog is small.
- Target large/xlarge when the backlog allows; a lone small/medium leftover is still a valid bundle.
- Never exceed xlarge per bundle; large is acceptable if xlarge would require unrelated work.
- One bundle = one trace.md (the contract carries a single `trace_path`; bundles never span features — coupled cross-feature work becomes two ordered bundles). Within a trace, group by dependency chain or shared code area.
- Attach tiny leftovers as add-ons to related bundles; if nothing related exists, a leftover-sweep bundle of small scenarios is valid. Do not mix unrelated features just to hit a size target.

## 4. Artifacts & Side Effects
No files written or mutated. Output = an options message (1-3 numbered bundles) with per-bundle title, size tier, feature+trace path, scenario list, rationale, and a machine-readable `Contract: {...}` line. Terminal side effect = `Skill(skill="stv:do-work")` with the selected contract verbatim, OR `Skill(skill="stv:plan-new-task")` on empty backlog.

## 5. Error Paths & NEVER
- Validate before handoff: `trace_path` must resolve to an existing trace file AND every `scenario_ids` entry must exist in that trace's Implementation Status. On mismatch → stop with a targeted-scope error, NOT a handoff.
- NEVER hand off an unvalidated/invalid contract; NEVER let do-work rescan when a contract is provided (`trace_path`/`scenario_ids` MUST survive unchanged).
- NEVER route to plan-new-task while any unfinished scenario remains — plan-new-task only on ZERO unfinished.
- NEVER force three bundles on a small backlog; NEVER exceed xlarge.

## 6. Acceptance Checklist
- [ ] All `docs/*/trace.md` surveyed; unfinished scenarios collected with size + deps.
- [ ] 1-3 bundles produced, none exceeding xlarge, grouped by the preferred axes.
- [ ] Options message includes a valid machine-readable `Contract` line per bundle.
- [ ] Selected contract validated (trace_path resolves, every id exists) before handoff.
- [ ] Valid path → do-work with verbatim contract; invalid → targeted-scope error; zero unfinished → plan-new-task.

## 7. Improvement Delta (2026-07-14)
- large/xlarge viability requirement dropped — small/medium tails are valid bundles; leftover-sweep bundle of small scenarios allowed.
- Machine-readable `Contract` line added to the options template.
- Validate-before-handoff rule added (trace_path resolves + every scenario id exists, else targeted-scope error).
- plan-new-task reroute restricted to ZERO unfinished scenarios only.
