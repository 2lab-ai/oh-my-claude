---
name: do-work
description: "Autonomous work execution on STV-traced scenarios. Selects unfinished scenarios from trace.md, implements via stv:work, loops until done or user input needed."
---

# Do Work — STV Autonomous Execution

## Overview

**do-work automates the complete STV implementation workflow: select unfinished trace scenarios → implement via stv:work → quality gates → loop until done.**

Core principle: Scan trace.md for ready scenarios → Bundle into work chunks → Execute with stv:work → Commit → Repeat.

## Sizing Rubric (expected code change, added + deleted)

| Tier   | Lines  | Example                                    |
|--------|--------|--------------------------------------------|
| tiny   | ~5     | Config values, constants, string literals   |
| small  | ~20    | One function, one file, local refactor      |
| medium | ~50    | Multiple files, interface changes           |
| large  | ~100   | Cross-cutting concerns, schema migrations   |
| xlarge | ~500   | Architecture shift, framework replacement   |

## When to Use

Use when:
- trace.md with unfinished scenarios exists
- Ready for autonomous implementation execution
- User wants minimal interruption until work is done

Do NOT use when:
- No trace.md exists (use `stv:new-task` first)
- User asked a single specific question
- Exploring/researching without implementation

## Workflow Phases

```
Phase A: Task Selection
    ↓
Phase B: STV Work Execution (→ stv:work)
    ↓
Phase C: Context Check
    ↓
Phase D: Loop Decision
    ↓ (loop back to A or stop)
```

### Phase A: Task Selection (~5min)

**Goal**: Select unfinished scenarios from trace.md and bundle for execution.

1. **Scan trace files**
   - Glob for `docs/*/trace.md` across the project
   - Read each trace.md's Implementation Status table
   - Collect scenarios where Status != "Complete"

2. **Prioritize scenarios**
   - Respect dependency order (earlier scenarios first)
   - Group by feature if multiple features have ready scenarios
   - Estimate combined size tier

3. **Bundle scenarios** (target: xlarge)
   - Bundle related scenarios into work chunks
   - If total < large: include more related scenarios
   - If total > xlarge: split into multiple bundles, execute first bundle
   - Cap at xlarge per bundle

4. **Present bundle to user**

```markdown
## Work Bundle

### Target: {feature-name}
Trace: docs/{feature}/trace.md

### Scenarios to implement:
| # | Scenario | Size | Dependencies |
|---|----------|------|-------------|
| {n} | {title} | {tier} | {deps or "none"} |
| ... | ... | ... | ... |

Estimated total: {tier}

Proceed? (or adjust bundle)
```

### Phase B: STV Work Execution

**Goal**: Implement the bundled scenarios using stv:work.

```
Skill(skill="stv:work") invoked
```

- stv:work performs per-scenario GREEN + Trace Verify
- After completion, update trace.md Implementation Status

**After stv:work completes:**

1. **Quality Gates**
   ```bash
   # Run project-specific commands
   npm test    # or bun test / pytest / dotnet test
   npm run build   # if applicable
   npm run lint    # if applicable
   ```

2. **Commit & Push**
   - Commit with detailed message referencing trace scenarios
   - Push to remote

### Phase C: Context Check (~1min)

**Goal**: Prevent context overflow.

```
IF context > 70%:
  1. Save critical state (current trace progress)
  2. Use /compact or context compression
  3. OR end session gracefully with resume point

ELSE:
  Continue to Phase D
```

### Phase D: Loop Decision (~1min)

**Goal**: Decide whether to continue autonomous work.

**Continue to Phase A if:**
- More unfinished scenarios exist in trace.md
- All requirements understood
- No blockers
- Context budget OK

**Stop and report to user if:**
- All scenarios complete (feature done)
- Requirements unclear or ambiguous
- Architectural decision needed (switching cost >= medium, can't use generic pattern)
- Context near limit
- Major milestone reached

**Report format when stopping:**

```markdown
## Work Session Report

### Completed
- {N}/{total} scenarios GREEN + Verified
- Feature: {feature-name}

### Remaining
- {M} scenarios still pending
- Next: Scenario {n} — {title}

### Quality
- Tests: {pass}/{total} passing
- Build: clean / {N} errors
- Lint: clean / {N} warnings

### Next Step
→ Run `stv:do-work` to continue
→ Or `stv:work docs/{feature}/trace.md` for specific trace
```

## Mid-Implementation Decision Thresholds

During execution, unexpected architectural decisions may arise.

**Default thresholds**: `auto_decide <= small (~20 lines)`, `must_ask >= medium (~50 lines)`

```
for each unexpected decision:
  if switching_cost <= small:
    → Autonomous decision + record in Auto-Decision Log
    → If small tier, report result to user
  elif switching_cost >= medium:
    → Check if switching cost can be reduced via generic architecture
      → If reducible: autonomous decision + log
      → If not reducible: move to Phase D and ask the user
```

**Auto-Decision Log format:**

```markdown
### Auto-Decision Log: [Decision Title]
- **Decision**: [Selected option]
- **switching cost**: [tier] (~Y lines)
- **Rationale**: [Detailed reason]
- **Generic pattern applied**: [Pattern name if applicable / "Not needed"]
- **Impact if changed**: [Where to modify if reversing later]
```

## Integration with Other Skills

**INVOKES:**
- `stv:work` — Per-scenario implementation execution in Phase B

**CALLED BY:**
- `stv:what-we-have-to-work` — After bundle selection
- `stv:what-to-work` — After routing

**PRECONDITIONS:**
- `docs/{feature}/trace.md` must exist
- trace.md must have unfinished scenarios
- If not → guide to `stv:new-task`

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Attempting execution without trace | Check docs/*/trace.md first |
| Ignoring bundle size | Target xlarge, cap at xlarge |
| Skipping quality gates | Run test/build/lint every time |
| Context overflow | Respond at 70% threshold in Phase C |
| Stopping for trivial decisions | switching cost <= small → autonomous decision |

## NEVER

- Start implementation without trace.md
- Skip quality gates
- Ignore context management
- Skip logging autonomous decisions
