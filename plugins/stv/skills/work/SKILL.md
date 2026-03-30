---
name: work
description: "STV Phase 3: Implementation (GREEN) + Trace Verify loop. Implements code to pass contract tests, then verifies implementation matches trace document."
---

# STV Work — Implementation + Trace Verify Loop

> STV Phase 3: trace.md → GREEN implementation + Trace Verify
> Write code that passes contract tests,
> then verify implementation matches the trace document.

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

## Phase 2: Implementation Loop (GREEN)

**Repeat for each scenario:**

```
for each scenario in trace.md:
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
   - If you have a reason to implement differently → update trace first

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
while (unverified scenarios exist):
  1. Select next unverified scenario
  2. Read code and compare against trace using 7-section criteria
  3. Mismatch → apply Mismatch Handling Protocol
  4. After fixes, re-run related tests
  5. GREEN + trace aligned → mark as Verified
```

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
{N}/{N} scenarios Trace Verified
{N} trace deviations (documented in trace.md)

### Test Results
- Total: {N} tests
- Passed: {N}
- Failed: 0

### Files Modified
{modified file list}

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

## NEVER

- Add features not in trace as "improvements"
- Modify tests to make them GREEN (fix the implementation instead)
- Declare "complete" without verify
- Ignore mismatches and move on
- Leave trace and code out of sync
- Skip gap self-check before trace verify
- Ignore detected gaps — gap correction takes priority over all other fixes
