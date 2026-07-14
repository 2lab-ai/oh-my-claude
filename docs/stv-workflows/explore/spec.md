# stv:explore — Workflow Spec

> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/explore/SKILL.md

## 1. Overview (Proposal) — "Stance, not workflow"

Explore is a **mental posture**, not a step-by-step process: no checklist, no template,
no phase gate (SKILL.md "Core Philosophy"). You adopt the read-only stance, investigate
until understanding crystallizes, then transition to the right next step. The work of
exploration IS the output — understanding the problem is real work, not preparation for it.

## 2. Trigger Contract

Entry conditions (any):
- Requirements are vague or contradictory; the problem domain is unfamiliar.
- Existing codebase is complex and poorly understood.
- Multiple valid approaches exist; trade-offs must be understood before committing.
- User says "investigate this first" / "before we spec this" / "let me think about this."

Exit conditions (transition when insight crystallizes):
- Understanding solidifies into actionable decisions → **stv:spec**
- A bug is discovered during exploration → **stv:debug**
- Exploration reveals ambiguity needing user input → **stv:clarify**
- Problem turns out simple and well-understood → **direct implementation**

## 3. Workflow Trace

Six stance principles (not steps):
- **Curious** — question every assumption; follow every "that's interesting" thread.
- **Open** — hold multiple hypotheses; strengthen alternatives before converging.
- **Visual** — draw ASCII diagrams; if you can't diagram it, you don't understand it yet.
- **Adaptive** — follow where inquiry leads; backtracking is progress.
- **Patient** — sit with ambiguity; the urge to "just start building" = under-explored.
- **Grounded** — every insight traces to actual code/data/behavior; no "probably".

Tactics (available tools, not mandatory steps):
- Callstack tracing (entry point → response, all layers)
- Dependency mapping (who depends on what, what breaks on change)
- Pattern recognition (similar existing implementations)
- Boundary identification (where the feature's territory starts/ends)
- History mining (`git log` — who/when/why)
- External research — external-docs agent if harness provides one (e.g. Librarian), else web tools

Artifact Proposal Protocol:
- **PROPOSE** saving crystallized insight (e.g. "save as `docs/{topic}/exploration.md`?").
- **NEVER auto-save** — the user decides. On consent, use the SKILL.md exploration.md
  template (Key Findings / Discovered Structure / Hypotheses / Decisions / Next Step).

Note: this stance is now also embedded as **stv:spec Step 0.5** (mandatory unknowns map).

## 4. Artifacts & Side Effects

- **None mandatory** — no required output format, no phase gates, no time limit.
- Proposed `docs/{topic}/exploration.md` only on explicit user consent.
- **NEVER modifies** existing STV artifacts (`spec.md`, `trace.md`, etc.) — read-only.

## 5. Error Paths & NEVER

- NEVER write code or modify files — read-only mode.
- NEVER auto-save artifacts without user consent.
- NEVER follow a rigid script — this is a stance, not a workflow.
- NEVER rush to conclusions — patience is a core principle.
- NEVER speculate without grounding in actual code/data.
- NEVER skip ASCII diagrams when structure is complex — visualization is mandatory there.

## 6. Acceptance Checklist

- [ ] No files written or code changed during the session (read-only honored).
- [ ] Insights traced to concrete code/data, not speculation.
- [ ] Complex structures visualized with ASCII diagrams.
- [ ] Any artifact save was proposed and user-consented, in the exploration.md format.
- [ ] Session exits with a recommended next step (spec / debug / clarify / direct impl).

## 7. Improvement Delta (2026-07-14)

- Description rewritten from mode-restatement to **trigger-based** (when-to-use conditions
  + explicit read-only stance and exit targets).
- **Librarian hard-dependency generalized** to a harness-conditional external-docs agent
  (both §What Explore Mode IS and §Exploration Tactics): use one if the harness provides
  it (e.g. Librarian), otherwise fall back to web/document tools.
