---
name: work
description: "Use when trace scenarios need implementation to GREEN plus trace-conformance verification — invoked with a trace path and OPTIONAL scenario_ids for targeted execution. STV Phase 3."
---

# STV Work — Implementation + Trace Verify Loop

> STV Phase 3: trace.md → GREEN implementation + Trace Verify
> Write code that passes contract tests,
> then verify implementation matches the trace document.

---

## Decision Gate (MANDATORY)

**Read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` and apply it to every decision in this workflow.**

Sizing Rubric: read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` (single source — do not duplicate the table here). Sizes (tiny/small/medium/large/xlarge) refer to expected code change (added + deleted).

---

## Phase 1: Context Loading

1. **Read trace**: Read trace.md at the specified path
   - If trace doesn't exist → guide user to run `stv:trace` first
2. **Read spec**: Read the spec.md referenced in trace.md
3. **Check RED tests**: Read contract test files and check current state
   - Verify all tests are RED (FAIL)
   - Warn if any test is not RED
4. **Determine implementation order**: Scenario order in trace = implementation order
   - If dependencies exist, implement dependencies first
5. **Resolve execution scope**: if `scenario_ids` were provided (bundle contract from do-work / what-we-have-to-work), the scenario loop operates ONLY on those rows (`targetedRows[] → verifyQueue[]`); if a provided id is not found in the trace, stop with a targeted-scope mismatch error. If omitted, all unfinished scenarios are in scope.

## Phase 2: Implementation Loop (GREEN)

**Repeat for each scenario:**

```
for each scenario in scope (scenario_ids if provided, else all unfinished):
  1. Re-read the scenario's trace
  2. Implement code based on the trace's 7 sections
     - Follow Layer Flow parameter transformation rules exactly
     - Follow Side Effects exactly
     - Follow Error Paths exactly
  3. Run contract tests for this scenario
  4. if GREEN → next scenario
  5. if RED → fix based on trace, re-run (fix against trace)
```

### Implementation Rules

1. **Trace is the Source of Truth**
   - If trace says "Step 2: ValidatePartner(entity)", implement with exactly that name/signature
   - Do not add behavior not specified in trace
   - If you have a reason to implement differently → update trace first (see Artifact Backtrack below)

2. **GREEN one scenario at a time**
   - Do not implement everything at once
   - Scenario 1 GREEN → Scenario 2 GREEN → ...
   - If a previous scenario breaks, fix immediately

3. **Side-Effect accuracy**
   - DB INSERT/UPDATE only the fields specified in trace
   - If saving fields not in trace → fix trace or fix code

### Test Portfolio Strategy

```
┌─────────────────────────────────────────────┐
│          Primary Gate (fast and stable)      │
│                                             │
│  Trace-Driven Contract/Component Tests      │
│  - Happy path, Sad path, Side-effect,       │
│    Contract (parameter transformation) tests │
│  - Execution time: seconds to minutes       │
│  - Stability: high (minimal external deps)  │
│  - PR merge blocking criterion              │
│                                             │
├─────────────────────────────────────────────┤
│          Secondary Gate (minimal count)      │
│                                             │
│  E2E Tests                                  │
│  - Only test what can only be verified in   │
│    deployment env (network, permissions,     │
│    deployment config, etc.)                  │
│  - Execution time: minutes to tens of mins  │
│  - Stability: low (potentially flaky)       │
│  - Pre-deployment check, not merge blocking │
│                                             │
└─────────────────────────────────────────────┘
```

Why Contract Tests are the primary gate: E2E tests are slow, fragile, flaky, and require dedicated environments. Contract Tests are fast, stable, and run locally.

## Phase 3: Trace Conformance Verify + Gap Detection

After all scenarios are GREEN, verify alignment between trace document and actual implementation.

### Gap Self-Check (Before Trace Verify)

Before detailed trace verification, run a quick gap detection pass against the original spec:

1. **Re-read spec.md** — what was ACTUALLY requested?
2. **List every feature implemented** — does each trace back to a spec requirement?
3. **Check for 5 gap types**:
   - `assumption_injection`: Added behavior not in spec?
   - `scope_creep`: Features beyond what spec asked for?
   - `direction_drift`: Overall approach diverges from spec intent?
   - `missing_core`: Any spec requirement not implemented?
   - `over_engineering`: Abstraction disproportionate to the problem?

If gap detected:
- Log gap type, description, and correction instruction
- Fix implementation to align with spec (1st attempt — autonomous)
- If gap persists after fix → ask the user before proceeding
- Re-run affected tests after gap correction

### Trace Conformance Checklist

Verify each scenario in trace.md against the 7-section criteria:

```markdown
### Scenario {N} Verify: {title}

**Section 0 — Client Surface (only if the trace has one):**
- [ ] The documented UI event/component actually fires the documented request
- [ ] Client-side transformation rules match (UI.field → Request.field)
- [ ] Response fields are rendered per the trace's return leg (Response.field → UI state/display)
- [ ] Each Section 5 error path produces the documented user-visible display
- [ ] If the client is a separate repo: the client↔API contract is recorded as a CDC boundary, not silently skipped

**Section 1 — API Entry:**
- [ ] HTTP method + route match
- [ ] Auth/authz method matches

**Section 2 — Input:**
- [ ] Request payload fields match
- [ ] Validation rules implemented

**Section 3 — Layer Flow:**
- [ ] Controller: Request → Command transformation rules match
- [ ] Service: Command → Entity transformation rules match
  - Domain decision logic matches trace
  - Derived values (ID generation, timestamps, etc.) follow trace rules
- [ ] Repository/DB: Entity → Row mapping matches
  - Transaction boundaries match trace
  - Constraints (FK, UNIQUE, etc.) exist in schema
- [ ] Parameter transformation arrow end-to-end verification
  - Request.X → Command.Y → Entity.Z → table.col chain matches

**Section 4 — Side Effects:**
- [ ] All INSERT/UPDATE/DELETE specified in trace exist in code
- [ ] No unexpected DB changes beyond trace
- [ ] Event publishing/cache changes match trace

**Section 5 — Error Paths:**
- [ ] Each error condition → exception type matches
- [ ] Exception → HTTP status mapping matches
- [ ] DB rollback/no-change guaranteed on error

**Section 6 — Output:**
- [ ] Success status code matches
- [ ] Response DTO fields match

**Section 7 — Observability (if applicable):**
- [ ] Log fields included
- [ ] Span naming matches
```

### Mismatch Handling Protocol

When a mismatch is found, follow this protocol:

```
Mismatch found →
  1. If trace is wrong (implementation is better):
     → Update trace.md → Update related tests → Re-verify
  2. If code is wrong (trace is correct):
     → Fix code → Re-run tests → Re-verify
  3. If judgment is difficult:
     → Ask the user

★ Either way, trace and code must always be synchronized.
★ Record modification history in the Trace Deviations section of trace.md.
```

### Verify Loop

```
while (unverified scenarios remain IN SCOPE):
  1. Select next unverified in-scope scenario
  2. Read code and compare against trace using 7-section criteria
  3. Mismatch → apply Mismatch Handling Protocol
  4. After fixes, re-run related tests
  5. GREEN + trace aligned → mark as Verified
```

### File Map Verification (after scenario verify loop)

After all scenarios pass the 7-section verify:

1. Extract all file paths from Section 3c (Persisted files) and Section 4 (Side Effects) across all scenarios
2. Check each file against `git diff --name-only` to confirm modification
3. For any unmodified file:
   - Read the scenario(s) that reference it
   - Determine required change from trace
   - Implement and re-run tests
4. Report File Map coverage in Phase 4 completion report

★ Tests are a subset of the spec. File Map is the full modification surface.

## Phase 4: Completion Report

After all scenarios are GREEN + Verified:

### trace.md Update

```markdown
## Implementation Status
| Scenario | Trace | Tests | Verify | Status |
|----------|-------|-------|--------|--------|
| 1. {title} | done | GREEN | Verified | Complete |
| 2. {title} | done | GREEN | Verified | Complete |

## Trace Deviations
{Parts that deviated from trace during implementation and reasons. "None" if empty}

## Verified At
{date} — All {N} scenarios GREEN + Verified
```

### Report to user

```
## STV Work Complete: {feature}

{N}/{N} scenarios GREEN
Scope: {all | targeted: scenario_ids}
{N}/{N} scenarios Trace Verified
{N} trace deviations (documented in trace.md)

### Test Results
- Total: {N} tests
- Passed: {N}
- Failed: 0

### Files Modified
{modified file list}

### File Map Coverage
- Trace File Map: {N} files
- Modified: {N}/{N}
- Unmodified: {list or "none"}

### Next Steps
- [ ] Code review
- [ ] Commit & PR
```

### Phase 3 Checklist

- [ ] Gap self-check passed (no drift from spec)
- [ ] All Contract Tests are GREEN
- [ ] Trace Conformance verification complete (0 mismatches)
- [ ] Trace document and code are synchronized
- [ ] If trace or code was modified due to mismatches, modification history recorded in Trace Deviations
- [ ] All files listed in Section 3c and Section 4 of trace are modified (File Map 100%)
- [ ] Integration/wiring code verified beyond test coverage (spec acceptance criteria cross-check)

## Actions, Not Phases — Artifact Backtrack Protocol

During implementation, you may discover that the trace or spec contains errors, missing scenarios, or wrong assumptions. **Going back is not failure — it is the Feedback Loop invariant in action.**

### When to Backtrack

```
During implementation, if:
  1. A spec assumption is wrong (business rule doesn't hold)
     → Backtrack to SPEC: re-invoke stv:spec in update mode
  2. A trace section is wrong (transformation logic incorrect, missing error path)
     → Backtrack to TRACE: update trace.md in-place + apply Delta Protocol
  3. A new scenario is discovered (not in trace)
     → Backtrack to TRACE: add scenario via Delta Protocol (ADDED)
  4. The entire approach is wrong (architecture mismatch)
     → Backtrack to SPEC: Update vs New decision tree applies
```

### Backtrack Decision Tree

```
Is the issue in trace only (implementation detail)?
├── YES → Fix trace.md in-place
│   ├── Apply Delta Protocol (MODIFIED)
│   ├── Update contract tests
│   └── Continue implementation
└── NO → Issue is in spec (requirement/architecture level)
    ├── Is it a small correction (switching cost < medium)?
    │   ├── YES → Fix spec.md + trace.md in-place
    │   └── Continue implementation
    └── Is it a fundamental change (switching cost >= medium)?
        ├── Apply Update vs New decision tree
        ├── If UPDATE → re-invoke stv:spec, then stv:trace
        └── If NEW → stop current work, start new spec
```

### Backtrack Rules

1. **Always update upstream artifacts first** — fix spec before trace, trace before code
2. **Record every backtrack in Trace Deviations** — with reason and what changed
3. **Re-run affected contract tests** after any artifact change
4. **Never silently diverge** — if code differs from trace, either update trace or fix code. Never leave them out of sync.

## NEVER

- Add features not in trace as "improvements"
- Modify tests to make them GREEN (fix the implementation instead)
- Declare "complete" without verify
- Ignore mismatches and move on
- Leave trace and code out of sync
- Skip gap self-check before trace verify
- Ignore detected gaps — gap correction takes priority over all other fixes
- Declare "complete" with unmodified File Map files
- Treat test coverage as equivalent to spec coverage
- Execute scenarios outside the provided scenario_ids scope (scope widening)
- Mark Status=Complete while Verify is not 'Verified' (verification failure can never coexist with Complete)
