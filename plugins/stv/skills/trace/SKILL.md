---
name: trace
description: "STV Phase 2: spec.md -> vertical trace + RED contract tests. Traces every API scenario through all layers with 7-section format and parameter transformation arrows."
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

- [ ] Vertical Trace document written for every scenario
- [ ] Each trace includes all 7 sections (API Entry, Input, Layer Flow, Side Effects, Error Paths, Output, Observability)
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

Without these arrows, bugs in the parameter transformation process can be missed.
No future-tense expressions like "will implement." Use present/definitive tense: "transforms," "maps to," "converts."

### Required content in each trace

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
| Scenario | Trace | Tests (RED) | Status |
|----------|-------|-------------|--------|
| 1. {title} | done | RED | Ready for stv:work |
| 2. {title} | done | RED | Ready for stv:work |

## Next Step
→ Proceed with implementation + Trace Verify via `stv:work`
```

## Completion

1. Save trace.md
2. Write RED contract tests and **run them to confirm all FAIL**
3. Present trace summary + RED test results + next step guidance to user
4. **Next skill guidance**: `Skill(skill="stv:work")` or guide user to use `stv:work docs/{feature}/trace.md`
