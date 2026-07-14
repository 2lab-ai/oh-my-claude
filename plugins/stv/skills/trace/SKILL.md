---
name: trace
description: "Use when a spec.md exists and per-scenario vertical traces + RED contract tests must be derived — or an existing trace.md needs Delta Protocol updates. STV Phase 2: spec.md -> docs/{feature}/trace.md, 7+1-section format with parameter transformation arrows."
---

# STV Trace — Vertical Trace + Contract Tests

> STV Phase 2: spec.md → `docs/{feature}/trace.md` + RED contract tests
> Traces each scenario from API entry → Handler → Service → DB at parameter-level granularity,
> then derives contract tests from the trace.

---

## Decision Gate (MANDATORY)

**Read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` and apply it to every decision in this workflow.**

**Apply this gate to every decision. switching cost < small → autonomous judgment, == small → autonomous decision + report, >= medium → ask the user.**

---

## Phase 1: Spec Loading

1. **Read spec**: Read spec.md at the specified path
   - If spec doesn't exist → guide user to run `stv:spec` first
2. **Explore codebase** (Agent:Explore):
   - Locate existing code corresponding to spec's API endpoints
   - Analyze implementation patterns of similar existing features
   - Map related types: DB entities, DTOs, enums, etc.
3. **Extract scenario list**: Derive traceable scenario list from spec's User Stories + Acceptance Criteria

## Phase 2: Trace Interview

Interview to confirm the concrete flow for each scenario.
**Apply Decision Gate: tiny/small → autonomous judgment, medium+ only → ask.**

### Update Mode (existing trace detected)

If a trace.md already exists for this feature:
1. Read existing trace.md
2. Diff against updated spec.md to identify changed requirements
3. Apply Delta Protocol: classify changes as ADDED/MODIFIED/REMOVED/RENAMED
4. Interview focuses only on changed/new scenarios (existing verified scenarios are preserved)
5. Update trace body in-place + append Delta Log entry

### Question targets (medium+ switching cost)

- Specific field values stored in DB and transformation rules
- Business rules for error paths (which condition triggers which error?)
- Call ordering and transaction boundaries across multiple services
- Dependencies between side-effects (if A fails, what happens to B?)

### Autonomous judgment targets (small or below)

- Validation flows identical to existing patterns
- Auth checks identical to existing patterns
- Error mappings identical to existing patterns (e.g., ArgumentException → BadRequest)
- Parameter names, response shapes following conventions

### Phase 2 Checklist

- [ ] Vertical Trace document written for every scenario (FULL or COMPACT per the Granularity Rule)
- [ ] Scenarios with a UI/client surface include Section 0 (client leg + return leg)
- [ ] Each FULL trace includes all 7 sections (API Entry, Input, Layer Flow, Side Effects, Error Paths, Output, Observability); a COMPACT trace (Granularity Rule) includes Sections 1, 2, 6 + a one-line Layer Flow + a mandatory `Files:` list (File Map source) and opens with the marker line `> Compact trace — granularity rule applied`
- [ ] Parameter transformation arrows specified in Layer Flow (Request.X → Command.Y → Entity.Z → table.column)
- [ ] All 4 categories of Contract Tests written
- [ ] All Contract Tests confirmed RED (compile but fail)
- [ ] If microservices, inter-service CDC defined separately

## Phase 3: Vertical Trace Writing

Document the complete call stack per scenario in **7-Section Vertical Trace Minimum Field Spec** format.

### 7-Section Vertical Trace Format

**Format is flexible (Markdown, YAML, JSON, etc.), but if any of the following fields are missing, bugs can hide in the gaps. All sections must be included.**

```markdown
## Trace: [Scenario Name]

### 0. Client Surface [Conditional — MANDATORY when the feature has a UI/client]
- Entry: [screen/component + user action that fires the request]
- Client transformation: UI.fieldA → Request.fieldA (client-side formatting/validation)
- Response rendering: Response.field → UI state/display (the return leg of the round trip)
- Error display: each Section 5 error path → what the user sees
- Boundary: if the client lives in a separate repo, record client↔API as a CDC boundary
  (contract defined here; the client repo owns its own trace)

### 1. API Entry
- HTTP Method: [GET/POST/PUT/DELETE/PATCH]
- Path: [/api/resource]
- Auth/AuthZ: [Required permissions or auth method]

### 2. Input (Request)
- Request payload:
  ```json
  {
    "field1": "type (required/optional) - description",
    "field2": "type (required/optional) - description"
  }
  ```
- Validation rules:
  - field1: [min/max length, allowed characters, format, etc.]
  - field2: [range, enum values, regex, etc.]

### 3. Layer Flow (Per-layer execution) ★Core★

#### 3a. Controller/Handler
- Extracted parameters: [Request → Command/DTO transformation]
- Derived values: [auto-generated IDs, timestamps, etc.]
- Transformation rules:
  - Request.FieldA → Command.PropertyA (transformation logic description)
  - Request.FieldB → Command.PropertyB (transformation logic description)

#### 3b. Service
- Domain decisions: [business rules, conditional branches]
- Other service calls: [sync/async, target, parameters]
- Transformation rules:
  - Command.PropertyA → Entity.AttributeA (transformation logic description)
  - Computed/derived: [Entity.ComputedField = f(PropertyA, PropertyB)]

#### 3c. Repository/DB
- Transaction boundary: [start and end points]
- Persisted entities/rows:
  - Table: [table name]
  - Column mapping: Entity.AttributeA → column_a
  - ID generation: [UUID v4, auto-increment, ULID, etc.]
  - Constraints: [UNIQUE, FK, CHECK, etc.]
- Persisted files:
  - `path/to/repository.ext` — role (e.g. repository implementation)
  - `path/to/migration.sql` — role (e.g. schema/migration)
  - `path/to/entity.ext` — role (e.g. ORM entity/model)
  - (Backtick-quote every path. This list is the source of truth for the do-work File Map gate.
     FULL traces list files here; COMPACT traces provide the equivalent via their `Files:` list.)

### 4. Side Effects
- DB changes:
  - INSERT: [table, key columns, value source]
  - UPDATE: [table, WHERE condition, changed columns]
  - DELETE: [table, WHERE condition] (if applicable)
- Events/messages published: [topic, payload schema]
- Cache changes: [cache key, TTL, invalidation rules]

### 5. Error Paths
- Validation failure: [which field violates which condition → HTTP status code, error response format]
- Auth/AuthZ failure: [→ 401/403, response]
- Conflict/idempotency: [duplicate request → 409 or idempotent handling, verify no DB state change]
- Downstream service failure: [retry policy, compensating transaction, circuit breaker]

### 6. Output (Response)
- Success status code: [200/201/204]
- Response schema:
  ```json
  {
    "id": "generated ID",
    "field1": "original or transformed value",
    "createdAt": "ISO 8601"
  }
  ```

### 7. Observability Hooks [Optional]
- Log fields: [traceId, userId, action, etc.]
- Trace/span naming: [span naming convention]
- Metrics: [counters, histograms, etc.]
```

### Parameter Transformation Arrows (MANDATORY)

**All Layer Flows must explicitly specify parameter transformation arrows:**

```
Request.X → Command.Y → Entity.Z → table.col
```

When Section 0 exists, extend the chain to the client on both legs: `UI.fieldA → Request.X → Command.Y → Entity.Z → table.col` and the return leg `table.col → Entity → Response.field → UI.render`. A trace that starts at API Entry lets a surface-only client fake the feature; the round trip is closed only when the client leg is specified.

Without these arrows, bugs in the parameter transformation process can be missed.
No future-tense expressions like "will implement." Use present/definitive tense: "transforms," "maps to," "converts."

## Granularity Rule — Full vs Compact Trace (single source; README FAQ defers here)

Write a FULL trace (all sections) when ANY of: parameter transformations exist, DB
side-effects exist, error paths branch, or a client surface exists. A COMPACT trace
is allowed for simple read-only flows (e.g. an unfiltered list GET with no
transformation). When in doubt, full.

A COMPACT trace contains exactly:
- the opening marker line `> Compact trace — granularity rule applied`
- Sections 1 (API Entry), 2 (Input), 6 (Output)
- a one-line Layer Flow note
- a mandatory `Files:` list (backtick-quoted paths the scenario touches, with roles) —
  this substitutes for Section 3c/4 as the File Map source, so the do-work/work
  File Map gate applies to compact scenarios unchanged
Downstream gates are compact-aware: work verifies a compact scenario against
Sections 1, 2, 6 + its `Files:` list only (no 7+1-section demand), and File Map
extraction reads `Files:` where Sections 3c/4 are absent.

### Required content in each trace

0. **Client Surface** [conditional] — UI entry, client-side transformation, response rendering, error display
1. **API Entry** — HTTP method, path, auth/authz
2. **Input** — Request payload + validation rules
3. **Layer Flow** — Including parameter transformation arrows, per-layer flow
4. **Side Effects** — DB INSERT/UPDATE/DELETE, events, cache
5. **Error Paths** — Condition → error → HTTP status
6. **Output** — Success response schema
7. **Observability** — Logs, traces, metrics (optional)

## Phase 4: Contract Tests (RED)

Derive tests from each scenario in the trace document.

### Test Categories

| Category | Derived from trace | Test form |
|----------|-------------------|-----------|
| **Happy Path** | Normal flow Request→Response + Side Effects | Input → Expected Output + DB state change verification |
| **Sad Path** | Error Paths (validation failure, auth failure, conflict, etc.) | Invalid input → Expected Error + verify no DB change |
| **Side-Effect** | Side Effects (DB, events, cache) | Independent verification of state changes after invocation |
| **Contract** | Layer Flow parameter transformation rules | End-to-end transformation chain verification (Request→DB) |

### Test Writing Rules

1. **Reflect trace scenario name in test class/method name**
   - Trace: "Stage 1 — Root Partner Creation" → Test: `RootPartnerCreate_HappyPath`
2. **Include trace reference comment in each test**
   ```
   // Trace: Stage 1, Section 3 — Layer Flow, Controller→Service transformation
   ```
3. **Confirm RED state** — Verify all tests fail
4. **Contract tests verify parameter transformation arrows end-to-end through DB**
   ```
   // Request.contactEmail("UPPER@CASE.COM") → Command.ContactEmail → Entity.Email → partner.email
   // Transformation rule: lowercase conversion
   ```

## Phase 5: Output

### Output Files

1. **`docs/{feature}/trace.md`** — Vertical Trace document
2. **Test files** — RED contract tests in the project's test directory

### trace.md Structure

```markdown
# {Feature Name} — Vertical Trace

> STV Trace | Created: {date}
> Spec: docs/{feature}/spec.md

## Table of Contents
1. [Scenario 1 — {title}](#scenario-1)
2. [Scenario 2 — {title}](#scenario-2)
...

---

## Scenario 1 — {title}

### 1. API Entry
- HTTP Method: {method}
- Path: {path}
- Auth/AuthZ: {auth}

### 2. Input
- Request payload:
  {payload schema}
- Validation rules:
  {validation rules}

### 3. Layer Flow

#### 3a. Controller/Handler
- Transformation: Request.X → Command.Y
- {class.method, file:line}

#### 3b. Service
- Domain decisions: {business rules}
- Transformation: Command.Y → Entity.Z
- Derived: {computed fields}

#### 3c. Repository/DB
- Transaction: {boundary}
- Mapping: Entity.Z → table.column

### 4. Side Effects
- DB INSERT: {table} ({columns})
- {other side effects}

### 5. Error Paths
| Condition | Error | HTTP Status |
|-----------|-------|-------------|
| ... | ... | ... |

### 6. Output
- Success: {status code}
- Response: {response schema}

### 7. Observability [Optional]
- Logs: {log fields}
- Spans: {span naming}

### Contract Tests (RED)
| Test Name | Category | Trace Reference |
|-----------|----------|-----------------|
| {test method} | Happy Path | Scenario 1, Section 3 |
| {test method} | Sad Path | Scenario 1, Section 5, Error 1 |
| {test method} | Side-Effect | Scenario 1, Section 4 |
| {test method} | Contract | Scenario 1, Section 3, Request.X→table.col |

---

## Auto-Decisions
{Content autonomously decided via Decision Gate}

## Implementation Status
| Scenario | Trace | Tests | Verify | Status |
|----------|-------|-------|--------|-------|
| 1. {title} | done | RED | — | Ready |
| 2. {title} | done | RED | — | Ready |

## Delta Log
{Change history when trace is updated. Empty on initial creation.}

## Next Step
→ Proceed with implementation + Trace Verify via `stv:work`
```

## Phase 6: Delta Protocol — Trace Evolution

When an existing trace.md needs updating (new requirements, changed scenarios, removed features), apply the Delta Protocol to maintain change history.

### When to Apply Delta Protocol

- New requirements added to an existing feature's spec
- Existing scenarios modified due to spec change
- Scenarios removed or deprecated
- Scenarios renamed or restructured

### Delta Format

Append a `## Delta Log` section at the end of trace.md. ("Delta Log" is the section heading; "Delta Protocol" refers to the change-tracking procedure below.) Each evolution is a dated entry with typed changes:

```markdown
## Delta Log

### {date} — {summary}

#### ADDED Scenarios
- **Scenario N — {title}**: {reason for addition}
  - Linked spec requirement: {requirement reference}
  - Contract tests: {test names added}

#### MODIFIED Scenarios
- **Scenario M — {title}**: {what changed and why}
  - Before: {brief description of previous behavior}
  - After: {brief description of new behavior}
  - Affected sections: {list of 7-section parts that changed}
  - Contract tests updated: {test names}

#### REMOVED Scenarios
- **Scenario K — {title}**: {reason for removal}
  - Migration: {what replaces this, or "N/A — feature deprecated"}
  - Contract tests removed: {test names}

#### RENAMED Scenarios
- **FROM**: Scenario J — {old title}
  **TO**: Scenario J — {new title}
  Reason: {why renamed}
```

### Delta Rules

1. **MODIFIED entries must include Before/After** — without comparison, the change is invisible
2. **REMOVED entries must include Reason + Migration** — deletion without explanation is information loss
3. **Contract tests must be updated alongside trace changes** — trace and tests are two faces of the same contract
4. **Implementation Status table must be updated** — changed scenarios reset to appropriate status:
   - ADDED → Status: "Ready for stv:work"
   - MODIFIED → Status: "Trace Updated — Re-verify needed"
   - REMOVED → Row removed from table
   - RENAMED → Status unchanged, title updated
5. **Original trace content is modified in-place** — the Delta Log records what changed, but the trace body always reflects the current state
6. **Status schema is fixed** — Implementation Status always uses `Scenario | Trace | Tests | Verify | Status`; a missing Verify column is a schema mismatch to fix, not a variant

### Integration with stv:work

When `stv:work` encounters a trace with MODIFIED scenarios (Status: "Trace Updated — Re-verify needed"):
1. Re-read the modified scenario's trace
2. Check if existing implementation still conforms
3. Update code if needed → re-run contract tests → re-verify

When `stv:work` encounters ADDED scenarios:
1. Treat as new RED scenarios → normal implementation flow

## Completion

1. Save trace.md
2. Write RED contract tests and **run them to confirm all FAIL**
3. Present trace summary + RED test results + next step guidance to user
4. **Next skill guidance**: `Skill(skill="stv:work")` or guide user to use `stv:work docs/{feature}/trace.md`
