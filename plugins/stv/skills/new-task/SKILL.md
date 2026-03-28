---
name: new-task
description: Trigger when 유저가 뭔가 일을 시키거나, 하이 레벨 컨셉을 이야기 할 경우, 유저의 지시에 여러 가지 암묵지가 느껴질 경우.
---

> Desc: Transform vague user requirements into STV-structured feature specs with traced scenarios. Orchestrates stv:spec and stv:trace to produce implementable work.

# New Task — STV Feature Decomposition

## Overview


**new-task transforms vague user requirements into structured STV artifacts (spec.md + trace.md) with traced scenarios as the task list.**

Core principle: Understand intent deeply → Create spec via stv:spec → Create trace via stv:trace → trace.md scenarios = task list.

## When to Use

Use when:
- User describes feature/idea in vague or high-level terms
- Need to decompose work into implementable scenarios
- Architectural decisions required before implementation
- Multiple implementation approaches possible
- Work requires structured spec + trace before coding

Do NOT use when:
- User request is already specific (1-2 file changes)
- Fixing obvious bug with clear solution
- Quick clarification or simple question
- Spec and trace already exist (use `stv:do-work` directly)

## Sizing Rubric

| Tier   | Lines  | Example                                    |
|--------|--------|--------------------------------------------|
| tiny   | ~5     | Config values, constants, string literals   |
| small  | ~20    | One function, one file, local refactor      |
| medium | ~50    | Multiple files, interface changes           |
| large  | ~100   | Cross-cutting concerns, schema migrations   |
| xlarge | ~500   | Architecture shift, framework replacement   |

## Workflow Phases

```
Phase 1: Intent Understanding
    ↓
Phase 2: Spec Creation (→ stv:spec)
    ↓
Phase 3: Trace Creation (→ stv:trace)
    ↓
Phase 4: Summary & Next Steps
```

### Phase 1: Intent Understanding (~5min)

**Goal**: Ground the vague request in actual project context.

1. **Analyze user request**
   - Identify core intent
   - Extract implicit requirements
   - Estimate scope

2. **Explore codebase** (Agent:Explore)
   - Identify related existing code
   - Understand existing patterns, conventions, architecture
   - Check if similar features already exist
   - Map affected areas

3. **Summarize context**
   - Organize discovered code/patterns
   - Identify integration points with existing architecture
   - Prepare information for spec interview in Phase 2

### Phase 2: Spec Creation → Invoke stv:spec

**Goal**: Generate a structured spec.md.

```
Skill(skill="stv:spec") invoked
```

- Conduct spec interview based on context collected in Phase 1
- Apply Decision Gate: switching cost < small → autonomous judgment, >= medium → ask user
- **Output**: `docs/{feature}/spec.md`

### Phase 3: Trace Creation → Invoke stv:trace

**Goal**: Decompose spec into per-scenario vertical traces + RED contract tests.

```
Skill(skill="stv:trace") invoked
```

- Trace per-scenario call stacks using spec.md as input
- Derive contract tests for each scenario
- **Output**: `docs/{feature}/trace.md` + RED tests

### Phase 4: Summary & Next Steps (~2min)

**Goal**: Present overall results to the user + execution guidance.

1. **trace.md scenario list = task list**
   - Each scenario in the Implementation Status table is one work unit

2. **Present summary to user**

```markdown
## Feature Ready: {feature-name}

### Artifacts Created
- `docs/{feature}/spec.md` — PRD + Architecture
- `docs/{feature}/trace.md` — {N} scenarios traced
- {N} RED contract tests created

### Scenario Task List
| # | Scenario | Size | Status |
|---|----------|------|--------|
| 1 | {title} | {tier} | Ready |
| 2 | {title} | {tier} | Ready |
| ... | ... | ... | ... |

### Auto-Decisions Made
{Summary of items autonomously decided via Decision Gate}

### Next Step
→ Start per-scenario implementation with `stv:do-work`
→ Or implement directly with `stv:work docs/{feature}/trace.md`
```

## Integration with Other Skills

**INVOKES:**
- `stv:spec` — Spec creation in Phase 2
- `stv:trace` — Trace creation in Phase 3

**SEQUENTIAL:**
After new-task completes → Use `stv:do-work` for execution

**CALLED BY:**
- `stv:plan-new-task` — Called after proposing a new feature and user selects an idea

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping Phase 1 | Always explore codebase first — plans grounded in reality |
| Starting trace without spec | Must follow stv:spec → stv:trace order |
| Not treating trace scenarios as tasks | trace.md Implementation Status = task list |
| Asking user about trivial things | Apply Decision Gate: switching cost < small → autonomous judgment |

## NEVER

- Skip or abbreviate stv:spec or stv:trace workflows
- Guide implementation without a trace
- Declare "complete" without a scenario list
