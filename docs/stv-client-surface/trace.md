# STV Client Surface (Section 0) — Vertical Trace

> STV Trace | Created: 2026-07-14
> Spec: docs/stv-client-surface/spec.md

## Scenario 1 — UI-Bearing Feature Gets a Round-Trip Trace

### 1. API Entry
- HTTP Method: SKILL
- Path: `trace` (authoring) → `work` (conformance)
- Auth/AuthZ: None

### 2. Input
- Request payload:
  ```json
  { "feature": "has UI/client surface = true", "spec": "docs/{feature}/spec.md §5.2 Client Surface" }
  ```
- Validation rules:
  - If the feature has a UI/client, Section 0 is MANDATORY; a trace without it is incomplete.
  - Pure-backend features omit Section 0 entirely (absent, not empty).

### 3. Layer Flow

#### 3a. Controller/Handler
- `spec` interview captures the client surface (screens/actions → endpoints → rendered response, or N/A).
- Transformation: `spec §5.2 Client Surface` → `trace Section 0 fields`

#### 3b. Service
- `trace` authors Section 0 + double-leg arrows; the Granularity Rule forces a full trace when a client surface exists.
- Transformation: `UI.fieldA → Request.X → Command.Y → Entity.Z → table.col` and `table.col → Entity → Response.field → UI.render`
- `work` verifies Section 0 during trace conformance (event fires request, transformations match, response renders, errors display).

#### 3c. Repository/DB
- Persisted files:
  - `plugins/stv/skills/trace/SKILL.md` — Section 0 format + arrow legs + granularity trigger + checklist
  - `plugins/stv/skills/work/SKILL.md` — Section 0 conformance block
  - `plugins/stv/skills/spec/SKILL.md` — §5.2 Client Surface template + interview coverage + checklist
  - `plugins/stv/README.md` — format block, role table, arrows, glossary, rationale

### 4. Side Effects
- UPDATE: the four files above (documentation is the persistence boundary).

### 5. Error Paths
| Condition | Error | Handling |
|-----------|-------|----------|
| UI feature traced without Section 0 | incomplete trace | trace Phase 2 checklist blocks; work conformance flags |
| Client in separate repo, no boundary noted | untraced gap | Section 0 Boundary rule records client↔API as CDC |
| Section 0 added to pure-backend feature | noise | conditionality rule: absent, not empty |

### 6. Output
- A UI-bearing feature's trace specifies the full round trip; work cannot mark it Verified while the client leg is unimplemented.

### 7. Observability [Optional]
- Conformance grep: `grep -c "Client Surface" trace/work/spec SKILL.md + README` ≥ 1 each.

### Contract Tests (doc-conformance)
| Check | Category | Result |
|-------|----------|--------|
| Section 0 block precedes Section 1 in trace format | Contract | GREEN (grep) |
| Double-leg arrow text present in trace SKILL + README | Contract | GREEN (grep) |
| work checklist contains Section 0 block | Side-Effect | GREEN (grep) |
| spec template contains §5.2 Client Surface | Side-Effect | GREEN (grep) |

## Auto-Decisions

See spec.md §7.

## Implementation Status

| Scenario | Trace | Tests | Verify | Status |
|----------|-------|-------|--------|--------|
| 1. UI-bearing feature gets a round-trip trace | done | GREEN (doc-conformance grep) | Verified | Complete |

## Delta Log

Initial creation, 2026-07-14.
