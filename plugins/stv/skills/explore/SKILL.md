---
name: explore
description: "Problem space exploration mode. Stance, not workflow. Read-only codebase investigation before committing to spec. Triggers on 'explore this', 'investigate', 'understand the problem', 'what are we dealing with', 'before we spec this'."
---

# stv:explore — Problem Space Exploration

> Stance, not workflow. Read-only investigation before committing to any plan.
> No scripts, no mandatory sequence, no required artifacts.

---

## Core Philosophy

Explore is a **mental posture**, not a step-by-step process. There is no checklist to complete, no template to fill, no phase gate to pass. You adopt the stance, investigate until understanding crystallizes, and then transition to the right next step.

The work of exploration IS the output. Understanding the problem is not preparation for real work — it is real work.

---

## The Six Stance Principles

### Curious
Question everything. Why does the code work this way? What assumptions are baked into this architecture? What would break if those assumptions changed? Follow every "that's interesting" thread.

### Open
Hold multiple hypotheses simultaneously. Do not converge prematurely. When you notice yourself favoring one explanation, deliberately strengthen the alternatives before deciding.

### Visual
ASCII diagrams actively. When structure is complex, **draw it** — don't just describe it. A dependency graph, a sequence flow, a layer map. If you can't diagram it, you don't understand it yet.

### Adaptive
Follow where the investigation leads. If a line of inquiry hits a dead end, pivot without guilt. The path through a problem space is discovered, not planned. Backtracking is progress.

### Patient
Do not rush to solutions. Sitting with ambiguity is productive. The urge to "just start building" is the signal that you haven't explored enough, not that you've explored too much.

### Grounded
Every insight must trace back to actual code, actual data, or actual behavior. If you catch yourself saying "probably" or "I assume," stop and go verify. Speculation is not exploration.

---

## What Explore Mode IS

- **Read-only investigation** of the problem space — code reading, pattern identification, dependency mapping
- **Multi-agent powered**: dispatch Explore agent for codebase search, Librarian agent for external docs and best practices
- **ASCII diagrams** to visualize discovered structures, flows, and boundaries
- **Hypothesis formation** followed by code-based validation
- **Insight accumulation** — when insights crystallize into decisions, PROPOSE artifact save (never auto-save)

## What Explore Mode is NOT

- **Not implementation** — zero code changes allowed
- **Not spec** — no structured interview, no template to fill
- **Not debug** — no specific bug to track, no AS-IS/TO-BE gap
- **Not think** — not designing a methodology or process
- No mandatory output format. No required artifacts. No time limit. No phase gates.

---

## Entry Conditions

Use explore when:

- Requirements are vague or contradictory
- The problem domain is unfamiliar
- The existing codebase is complex and poorly understood
- Multiple valid approaches exist and trade-offs need to be understood before committing
- The user says "let me think about this," "investigate this first," or "before we spec this"

## Exit Conditions

Transition out when insights crystallize:

- Understanding has solidified into actionable decisions → suggest `stv:spec`
- A bug was discovered during exploration → suggest `stv:debug`
- The problem turned out to be simple and well-understood → suggest direct implementation
- Exploration revealed ambiguity that needs user input → suggest `stv:clarify`

---

## Exploration Tactics

These are available tools, not mandatory steps. Use what the investigation calls for.

- **Callstack tracing**: follow a request through all layers, entry point to response
- **Dependency mapping**: who depends on what, what breaks if this changes
- **Pattern recognition**: find similar existing implementations in the codebase
- **Boundary identification**: where does this feature's territory start and end
- **History mining**: `git log` for relevant context — who changed this, when, why
- **External research**: Librarian agent for documentation, best practices, prior art

---

## Artifact Proposal Protocol

During exploration, insights accumulate informally. When an insight crystallizes into a clear understanding or decision:

1. **PROPOSE** saving it — e.g., "I've mapped the dependency graph. Want me to save this as `docs/{topic}/exploration.md`?"
2. **NEVER auto-save.** The user decides whether an artifact is worth keeping.
3. If the user agrees, use this format:

```markdown
# Exploration: {Topic}
> STV Explore | {date}

## Key Findings
- {finding 1}
- {finding 2}

## Discovered Structure
{ASCII diagram}

## Hypotheses
- {hypothesis 1}: {supporting evidence}
- {hypothesis 2}: {supporting evidence}

## Decisions Crystallized
- {decision}: {rationale}

## Recommended Next Step
→ {stv:spec | stv:debug | direct implementation | stv:clarify}
```

---

## Integration with STV Workflow

- Explore can be invoked **BEFORE** any STV phase — as the first step when the problem is unclear
- Explore can be invoked **FROM** any STV phase — e.g., during a spec interview, realize you need to explore more, drop into explore, then return
- Explore **NEVER modifies** existing STV artifacts (`spec.md`, `trace.md`, etc.)

---

## NEVER

- Write code or modify files — this is read-only mode
- Auto-save artifacts without user consent
- Follow a rigid script — this is a stance, not a workflow
- Rush to conclusions — patience is a core principle
- Speculate without grounding in actual code or data
- Skip ASCII diagrams when structure is complex — visualization is mandatory for complex structures
