---
name: do-work
description: "Use when a trace.md with unfinished scenarios exists and the user wants autonomous implementation — 'continue the work', 'implement the traced feature', or after a bundle was selected. Accepts an explicit bundle contract (trace_path + scenario_ids); scans for ready scenarios only when no contract is given."
---

# Do Work — STV Autonomous Execution

## Overview

**do-work automates the complete STV implementation workflow: select unfinished trace scenarios → implement via stv:work → quality gates → loop until done.**

Core principle: Scan trace.md for ready scenarios → Bundle into work chunks → Execute with stv:work → Commit → Repeat.

## Decision Gate (MANDATORY)

**Read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` and apply it to every decision in this workflow.**

Sizing Rubric: read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` (single source — do not duplicate the table here). Sizes below (tiny/small/medium/large/xlarge) refer to expected code change (added + deleted).

## When to Use

Use when:
- trace.md with unfinished scenarios exists
- Ready for autonomous implementation execution
- User wants minimal interruption until work is done
- A bundle contract {trace_path, scenario_ids} was handed off from what-we-have-to-work

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

0. **Honor an explicit bundle contract** (if provided)
   - Input: `{"trace_path": "docs/{feature}/trace.md", "scenario_ids": ["1","2"], "size": "...", "rationale": "..."}`
   - Validate: `trace_path` exists; every `scenario_ids` entry is present in that trace's Implementation Status. On mismatch → stop with a targeted-scope error (do NOT widen scope to recover).
   - When the contract is valid: SKIP global trace discovery (steps 1 and the scan part of 3) — the contract IS the scope. Still extract the File Map (step 2) for the selected scenarios.
   - Rescanning the entire project despite an explicit contract is a contract violation.

1. **Scan trace files**
   - Glob for `docs/*/trace.md` across the project
   - Read each trace.md's Implementation Status table
   - Collect scenarios where Status != "Complete"

2. **Extract File Map** (MANDATORY)
   - For each trace.md, extract ALL unique file paths from:
     - Section 3c "Persisted files" — backtick-quoted paths under `- Persisted files:`
     - Section 4 "Side Effects" — paths after `UPDATE:`, `INSERT:`, `DELETE:`
   - Deduplicate across all scenarios → **File Map Checklist**
   - This is the real completion checklist. Tests are a subset; File Map is the whole.

3. **Prioritize scenarios**
   - Respect dependency order (earlier scenarios first)
   - **Integration-first tiebreaker**: among scenarios at the same dependency level, prioritize those whose File Map entries include existing files with 200+ lines. These core pipeline files are the work most likely to be deferred — do them first.
   - Group by feature if multiple features have ready scenarios
   - Estimate combined size tier

4. **Bundle scenarios** (target: xlarge)
   - Bundle related scenarios into work chunks
   - If total < large: include more related scenarios
   - If total > xlarge: split into multiple bundles, execute first bundle
   - Cap at xlarge per bundle

5. **Present bundle to user**

```markdown
## Work Bundle

### Target: {feature-name}
Trace: docs/{feature}/trace.md

### Scenarios to implement:
| # | Scenario | Size | Dependencies |
|---|----------|------|-------------|
| {n} | {title} | {tier} | {deps or "none"} |

### File Map (all files trace says to modify):
| # | File | Scenarios | Modified? |
|---|------|-----------|-----------|
| 1 | {path} | {scenario numbers} | pending |

Estimated total: {tier}

Contract: {"trace_path": "...", "scenario_ids": [...]}

Proceed? (or adjust bundle)
```

### Phase B: STV Work Execution

**Goal**: Implement the bundled scenarios using stv:work.

```
Skill(skill="stv:work") invoked
```

Pass the same targeted scope: trace_path + scenario_ids. stv:work iterates ONLY the selected scenarios.

- stv:work performs per-scenario GREEN + Trace Verify
- After completion, update trace.md Implementation Status

**After stv:work completes:**

1. **File Map Completion Gate** (MANDATORY — before quality gates)

   For each file in the File Map Checklist:
   - Check: was this file modified? (`git diff --name-only`)
   - Mark as: modified / NOT modified

   IF any File Map file is NOT modified:
   - List unmodified files with their trace scenario references
   - For each unmodified file:
     a. Re-read the trace scenario(s) that reference this file
     b. Determine what change was required
     c. Implement the missing change
     d. Re-run tests
   - Re-check File Map. Do NOT proceed until all files are modified.

   ★ Tests GREEN alone is NOT sufficient. File Map 100% = the real completion gate.

2. **Gap Detection Gate** (before quality gates)
   - Re-read spec.md for the feature
   - Compare ALL implemented code against spec requirements
   - Check 5 gap types: `assumption_injection`, `scope_creep`, `direction_drift`, `missing_core`, `over_engineering`
   - If gap detected:
     - Log gap and attempt autonomous correction (1st attempt)
     - Re-run stv:work verify after correction
     - If gap persists → stop and report to user (Phase D)

3. **Quality Gates**
   ```bash
   # Run project-specific commands
   npm test    # or bun test / pytest / dotnet test
   npm run build   # if applicable
   npm run lint    # if applicable
   ```

4. **Spec Re-verification** (MANDATORY — before commit)

   Re-read the spec.md referenced in trace.md.
   For each acceptance criterion in the spec:
   - Is it covered by a test?
   - Is it covered by trace Section 4 side effects?
   - Is it implemented in code even if no test covers it?

   IF any spec requirement is not implemented:
   → Implement it now, re-run quality gates.


5. **Finalize (environment-dependent)**
   - Commit with a detailed message referencing trace scenarios (default everywhere a git repo exists).
   - Push / open a PR only where the host environment's workflow policy allows it; pushing to protected or default branches without the host's ship gate is forbidden.
   - If no git policy is known for the environment, commit locally and report — do not invent a push step.

### Phase C: Context Check (~1min)

**Goal**: Prevent context overflow.

```
IF the harness exposes context usage AND it exceeds ~70%:
  checkpoint (update trace.md Implementation Status) and compact or end with a resume point.
OTHERWISE (no context signal available):
  checkpoint trace.md Implementation Status after EVERY bundle and prefer ending
  at bundle boundaries with a resume point.
/compact is host-specific and optional — never assume it exists.
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
- Gap detected and autonomous correction failed (2nd gap = escalate)

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

**Auto-Decision Log format:** See `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` for the full template. Minimum fields: Decision, switching cost tier, Rationale, Impact if changed.

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
| Context overflow | Checkpoint at bundle boundaries; use context signals only if the harness provides them |
| Stopping for trivial decisions | switching cost <= small → autonomous decision |
| File Map files not all modified | Run File Map Completion Gate before quality gates |
| Ignoring an explicit bundle contract and rescanning the repo | Honor {trace_path, scenario_ids}; scope widening is a contract violation |

## Anti-Patterns — Known Failure Modes

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| "Test pass = done" bias | All tests GREEN but integration code not wired, config not updated | File Map Gate + Spec Re-verification catch the gap between "tests pass" and "feature works" |
| File Map as decoration | trace lists 5 files, only 3 modified — files without tests skipped | Extract File Map in Phase A, gate on it in Phase B. Every Section 3c/4 file MUST show a diff |
| Complexity avoidance | New utility files created but 500-line core pipeline file untouched | Integration-first ordering. Large existing files get priority. The wiring IS the feature |

★ Parts assembled without wiring do not work. Assembly is not optional — it is the feature.

## NEVER

- Start implementation without trace.md
- Skip quality gates
- Skip gap detection gate (runs BEFORE quality gates)
- Ignore context management
- Skip logging autonomous decisions
- Attempt more than 1 autonomous gap correction per bundle (escalate on 2nd)
- Declare work complete when File Map has unmodified files
- Skip Spec Re-verification before commit
- Treat test coverage as equivalent to spec coverage
- Widen scope beyond a provided bundle contract (trace_path + scenario_ids)
- Push to a protected/default branch without the host environment's ship gate
