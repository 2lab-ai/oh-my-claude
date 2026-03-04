# STV — Spec-Trace-Verify

**Traced Development: A Spec-Driven Development Methodology for the AI Era**

```
Spec → Trace → Verify
 Why?   Blueprint  Verify
```

---

## What is Traced Development?

Traced Development is a **spec-driven development methodology that writes Vertical Traces spanning all layers before implementation, derives Contract Tests from the trace, and verifies alignment between trace and code after implementation.**

It builds on Spec-Driven Development, combining Vertical Trace with RED/GREEN TDD.

### Core Principle

> **The Trace is the Source of Truth.**
>
> Code must behave exactly as specified in the trace. Do not add behavior not in the trace.
> If there's a reason to implement differently, update the trace first.

---

## STV's 4 Invariants

Core components that make STV a methodology. These four must always hold regardless of which phase you are in.

### 1. Trace Spec

A per-scenario end-to-end execution path document. The **document comes first**, not the code. While Tracer Bullet "punches through with code," STV "locks down with documentation first."

### 2. Contract Tests

Trace specs converted into automated tests. They must always start in RED state. **The trace document = text version of the contract. Contract tests = executable version of the contract.**

### 3. Conformance Gate

A logical chain: "specs must exist for tests to be possible, and tests must exist for conformance claims to be valid." In practice, this operates as a **process gate where PRs cannot merge without a spec**.

### 4. Feedback Loop

When a mismatch between trace and implementation is found during coding, either the trace or the code is updated. **Either way, the two are always synchronized.** If trace and code drift apart and are left unattended, STV becomes dead documentation.

---

## Why Is This Needed? — The AI Slop Problem

Structural problems with AI coding agents:

- AI tries to **generate complete solutions in one shot**
- It builds individual layers in isolation and **never verifies that the critical path actually works end-to-end**
- Result: massive code blobs requiring rework — **slop**
- LinearB data: **67.3% of AI-generated PRs are rejected** (manual code: 15.6%)

### What Vertical Trace Solves

```
Without AI:
  "Build a partner creation API" → surface-level implementation → "Done!"
  Actually: not saved to DB, validation missing, no auth

Traced Development:
  "Build a partner creation API"
  → Spec: what and why
  → Trace: 7-section parameter-level tracking across all layers
  → Contract Test: tests enforcing each trace section
  → Implementation: pass tests + verify against trace
  → Nothing can be skipped
```

---

## Theoretical Background

STV sits at the intersection of several proven methodologies:

| Methodology | Core Idea | Role in STV |
|-------------|-----------|-------------|
| **Tracer Bullet Dev** (Pragmatic Programmer) | Thin slice through all layers from day one | Vertical Trace mindset |
| **Specification by Example** (Gojko Adzic) | Concrete examples = executable specs | Trace = executable blueprint |
| **ATDD** | Acceptance tests drive development | Contract Tests (RED) |
| **Design by Contract** (Bertrand Meyer) | Enforced pre/post conditions | Error Paths + Side Effects verification |
| **Vertical Slice Architecture** (Jimmy Bogard) | Cut through all layers per feature | Per-scenario vertical analysis |
| **TDD** (Kent Beck) | RED → GREEN → REFACTOR | Contract Tests → Implementation → Verify |

**STV's unique contribution:**
- Call-stack-level trace documentation before writing code (a practice found nowhere else)
- Contract test derivation directly from trace
- Post-implementation trace-code conformance verification loop
- Structural prevention of AI agents' surface-level implementations

---

## 3-Phase Structure

```
┌───────────────────────────────────────────────────────┐
│  Phase 1: SPEC                                        │
│  "What and How"                                       │
│                                                       │
│  Step 1-0: Input Analysis                             │
│  Step 1-1: Business Interview — User stories, AC      │
│  Step 1-2: Architecture Interview — Layers, DB, API   │
│  Step 1-3: Spec Writing                               │
│                                                       │
│  Output: docs/{feature}/spec.md                       │
└───────────────────────┬───────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────┐
│  Phase 2: TRACE                                       │
│  "Blueprint + Contract"                               │
│                                                       │
│  ① 7-Section Vertical Trace — Per-scenario all-layer  │
│    API Entry → Input → Layer Flow → Side Effects →    │
│    Error Paths → Output → Observability               │
│    (Parameter transformation arrows mandatory)        │
│  ② Contract Tests (RED) — Derived in 4 categories    │
│    Happy path / Sad path / Side-effect / Contract     │
│                                                       │
│  Output: docs/{feature}/trace.md + *Tests (all RED)   │
└───────────────────────┬───────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────┐
│  Phase 3: VERIFY                                      │
│  "Implementation + Conformance"                       │
│                                                       │
│  ① Implementation (GREEN) — Code to pass tests        │
│  ② Trace Conformance — Verify against 7-section       │
│  ③ Loop: mismatch → fix trace or fix code             │
│                                                       │
│  Output: src/**/* (all GREEN) + trace.md (Verified)   │
└───────────────────────────────────────────────────────┘
```

---

## Vertical Trace — 7-Section Format

A document that structures how an API request penetrates all layers of the system per scenario into **7 sections**.

### 7-Section Minimum Field Spec

```markdown
## Trace: [Scenario Name]

### 1. API Entry
- HTTP Method, Path, Auth/AuthZ

### 2. Input (Request)
- Request payload + validation rules

### 3. Layer Flow ★Core★
- 3a. Controller/Handler: Request → Command transformation
- 3b. Service: Command → Entity transformation + domain decisions
- 3c. Repository/DB: Entity → Row mapping + transactions

### 4. Side Effects
- DB changes (INSERT/UPDATE/DELETE)
- Events/messages, cache changes

### 5. Error Paths
- Validation failure, auth/authz failure, conflicts, downstream failures

### 6. Output (Response)
- Success status code + response schema

### 7. Observability Hooks [Optional]
- Log fields, trace/spans, metrics
```

### Parameter Transformation Arrows (MANDATORY)

Must be specified in Layer Flow:

```
Request.FieldA → Command.PropertyA → Entity.AttributeA → table.column_a
```

These arrows become the source of Contract tests.

### Role of Each Section

| Section | Role | Derived Tests |
|---------|------|---------------|
| 1. API Entry | Entry point definition | — |
| 2. Input | Request validation rules | Sad Path (validation failure) |
| 3. Layer Flow | Parameter transformation chain | Contract (transformation verification) |
| 4. Side Effects | State changes | Side-Effect |
| 5. Error Paths | Error branches | Sad Path (business errors) |
| 6. Output | Response verification | Happy Path |
| 7. Observability | Observability | — (optional) |

---

## Contract Tests

Tests derived directly from the trace document. **Trace = the contract. Test = contract compliance verification.**

### Test Categories (4)

| Category | Derived from Trace | Verification Target |
|----------|-------------------|---------------------|
| **Happy Path** | Normal flow Request→Response + Side Effects | Correct input → expected output + DB state change |
| **Sad Path** | Error Paths (validation failure, auth failure, conflict, etc.) | Invalid input → expected error + no DB change |
| **Side-Effect** | Side Effects (DB, events, cache) | Independent verification of state changes after invocation |
| **Contract** | Layer Flow parameter transformation rules | End-to-end transformation chain verification (Request→DB) |

### Example

```csharp
// Category: Contract — Trace Section 3, Layer Flow parameter transformation
// Request.contactEmail("UPPER@CASE.COM") → Command.ContactEmail → Entity.Email → partner.email
// Transformation rule: lowercase conversion
[Fact]
public async Task CreatePartner_ParameterTransformation_EmailLowercased()
{
    var request = new CreatePartnerRequest
    {
        CompanyName = "Test Corp",
        ContactEmail = "UPPER@CASE.COM",
        CommissionRate = 0.10m
    };

    var response = await _client.PostAsJsonAsync("/api/partners", request);
    var body = await response.Content.ReadFromJsonAsync<PartnerResponse>();

    // Transformation rule verification: API response
    body.Email.Should().Be("upper@case.com");

    // End-to-end DB verification
    var partner = await _dbContext.Partners.FindAsync(body.Id);
    partner!.Email.Should().Be("upper@case.com");
}
```

### Test Portfolio Strategy

```
Primary gate (PR merge criterion):
  Contract/Component Tests — fast and stable, seconds to minutes

Secondary gate (pre-deployment check):
  E2E Tests — only test what can only be verified in deployment env, minutes to tens of minutes
```

---

## Decision Gate

**Autonomous judgment vs user question discriminator** applied to every decision.

### Core: Switching Cost

> "How many lines would need to change to reverse this decision later?"

| Tier | Lines | Action | Example |
|------|-------|--------|---------|
| tiny | ~5 | Autonomous judgment | Config values, constants, error messages |
| small | ~20 | Autonomous decision + report | In-function implementation, file location |
| medium | ~50 | **Ask the user** | Interface changes, multiple files |
| large | ~100 | **Ask the user** | Schema migrations |
| xlarge | ~500 | **Ask the user** | Architecture shift |

**small distinction**: Decide autonomously, but report the decision and rationale to the user.

**Goal: Minimize the number of user questions.** Decide trivial things autonomously and just log them.

---

## Microservices — CDC Separation

When inter-service interactions exist, separate **intra-service traces** from **inter-service contracts (CDC)**.

```
┌─────────────────────────┐     ┌─────────────────────────┐
│  Service A (Consumer)    │     │  Service B (Provider)    │
│                         │     │                         │
│  Vertical Trace (int.)  │     │  Vertical Trace (int.)  │
│  Contract Tests (int.)  │────▶│  Contract Tests (int.)  │
└────────────┬────────────┘     └────────────┬────────────┘
             │                               │
             └──────── CDC Contract ─────────┘
                  (Inter-service interface contract)
                  (Automated verification via Pact, etc.)
```

Verify service internals with Vertical Trace + Contract Tests, and inter-service interfaces with CDC tools like Pact.

---

## Runtime Observability Extension (Optional)

To extend Trace Verify scope to runtime observation in microservice environments, leverage Section 7 (Observability Hooks) of the trace document.

```
Trace Document (Design Time)         Runtime Observation (Ops Time)
─────────────────────                ─────────────────────
Controller → Service → DB           Span: POST /api/partners
       │         │                       └─ Span: Handler
       │         │                            └─ Span: Repository
  Parameter transformation rules    Record pre/post values in span attributes
  Side Effects                      Record DB INSERT as span events
```

By verifying that the call chain documented in the trace is observed as actual span relationships at runtime, you can connect documentary specs with observable facts.

---

## Skill Reference

### Core Skills (3-Phase)

| Skill | Phase | Role | Input → Output |
|-------|-------|------|----------------|
| `stv:spec` | 1. Spec | PRD + Architecture interview | Feature description → `docs/{f}/spec.md` |
| `stv:trace` | 2. Trace | 7-Section Vertical Trace + RED tests | spec.md → `docs/{f}/trace.md` + tests |
| `stv:work` | 3. Verify | Implementation (GREEN) + Trace Conformance | trace.md → code + verified trace |

### Orchestration Skills

| Skill | Role | Call Relationship |
|-------|------|-------------------|
| `stv:new-task` | Vague requirements → spec + trace | Calls spec → trace sequentially |
| `stv:do-work` | Autonomous execution loop | Calls work repeatedly + quality gates |
| `stv:what-to-work` | Next work decision router | → what-we-have or plan-new-task |
| `stv:what-we-have-to-work` | Unfinished scenario bundling | → do-work |
| `stv:plan-new-task` | New feature proposal when backlog is empty | → new-task |

### Skill Flow Diagram

```
User: "What should I work on?"
       │
       ▼
 ┌──────────────┐
 │ what-to-work │ ← scans trace.md
 └──────┬───────┘
        │
   ┌────┴─────┐
   ▼          ▼
 Unfinished  Complete/
 scenarios   None
   │          │
   ▼          ▼
 ┌──────────────────┐   ┌───────────────┐
 │what-we-have-to-  │   │ plan-new-task  │
 │work              │   │               │
 │ (bundle proposal)│   │ (feature idea) │
 └────────┬─────────┘   └───────┬───────┘
          │                     │
          ▼                     ▼
 ┌──────────────┐       ┌──────────────┐
 │   do-work    │       │   new-task   │
 │ (autonomous) │       │ (spec+trace) │
 └──────┬───────┘       └──────┬───────┘
        │                      │
        ▼                      ▼
 ┌──────────────┐       ┌──────────────┐
 │  stv:work    │       │  stv:spec    │
 │ (GREEN+verify)│      │  stv:trace   │
 └──────────────┘       └──────────────┘
```

```
User: "Build this feature"
       │
       ▼
 ┌──────────────┐
 │   new-task   │
 └──────┬───────┘
        │
   ┌────┴────┐
   ▼         ▼
 stv:spec  stv:trace
   │         │
   ▼         ▼
 spec.md   trace.md + RED tests
              │
              ▼
        ┌──────────┐
        │ do-work  │
        └────┬─────┘
             │
        ┌────┴────┐
        ▼         ▼
     stv:work   stv:work
     (scenario1) (scenario2)
        │         │
        ▼         ▼
      GREEN     GREEN
        │         │
        ▼         ▼
     Verify    Verify
```

---

## Artifact Structure

Files generated by STV:

```
docs/
└── {feature-name}/
    ├── spec.md       ← Phase 1: PRD + Architecture
    └── trace.md      ← Phase 2: 7-Section Vertical Trace + Contract Test list

tests/
└── {feature}/
    └── *Tests.cs     ← Phase 2: RED Contract Tests (4 categories)

src/
└── **/*.cs           ← Phase 3: GREEN Implementation
```

### trace.md is the Task List

The **Implementation Status** table in trace.md serves as the task list:

```markdown
## Implementation Status
| Scenario | Trace | Tests | Verify | Status |
|----------|-------|-------|--------|--------|
| 1. Root partner creation | done | GREEN | Verified | Complete |
| 2. Commission plan creation | done | RED | — | Ready |
| 3. Sub-partner creation | done | RED | — | Ready |
```

No separate task management tool needed. trace.md itself is the living progress tracking document.

---

## FAQ

### Q: Do I need to write a trace for every scenario?

Focus on scenarios with core business logic. Simple CRUD GET (list queries) don't need full traces. Decision criteria: "Are there parameter transformations?", "Are there DB side-effects?", "Do error paths branch?" — if any apply, write a trace.

### Q: Won't trace documents become unmanageable when they grow large?

Split by scenario. Operate as `traces/partner-create.md`, `traces/partner-update-tier.md` — one scenario = one trace file keeps each file to 1-2 pages.

### Q: How is this different from traditional TDD?

TDD says "write tests first." STV says "write the trace first, then derive tests from the trace." In TDD, which tests to write is up to the developer's judgment. In STV, the trace is the source of tests, so they're mechanically determined. Side-effect tests and parameter transformation tests are commonly missed in TDD, but in STV they're specified in the trace and cannot be overlooked.

### Q: Can this be used without AI agents?

Absolutely. STV's core is the discipline of "write the trace before the code," not a dependency on AI agents. However, value is maximized when used with AI agents — human developers can perform traces mentally, but AI agents lack this tacit knowledge.

### Q: What if trace and code keep falling out of sync?

Repeated misalignment signals that Phase 1 (Spec) was insufficient. Go back to the spec and re-examine business requirements or technical decisions. The trace should be "call-stack level," not line-by-line code description.

---

## Glossary

| Term | Definition |
|------|-----------|
| **Traced Development** | Official name for the STV methodology |
| **Vertical Trace** | Document tracking a scenario's full-layer call stack in 7-section format |
| **7-Section Format** | API Entry, Input, Layer Flow, Side Effects, Error Paths, Output, Observability |
| **Parameter Transformation Arrow** | Notation in `Request.X → Command.Y → Entity.Z → table.col` format for transformation chains |
| **Contract Test** | Test derived from trace. Trace is the contract, test is compliance verification |
| **Trace Conformance** | Post-implementation verification comparing trace document and actual code against 7-section criteria |
| **4 Invariants** | Trace Spec, Contract Tests, Conformance Gate, Feedback Loop |
| **Decision Gate** | Switching-cost-based discriminator for autonomous judgment vs user question (tiny/small/medium/large/xlarge) |
| **CDC** | Consumer-Driven Contract Testing. Inter-service interface contract verification for microservices |
| **Side-Effect** | State changes such as DB INSERT/UPDATE/DELETE |
| **Source of Truth** | The trace document. The trace is the standard, not the code |
| **Slop** | Low-quality code generated by AI that only works superficially |

---

## Quick Start

```bash
# 1. Start a new feature (spec → trace → task list auto-generated)
/stv:new-task "Partner tracking link CRUD"

# 2. Or run each phase manually
/stv:spec "Partner tracking link CRUD"
/stv:trace docs/tracking-link/spec.md
/stv:work docs/tracking-link/trace.md

# 3. Autonomous execution mode (iterative scenario implementation)
/stv:do-work

# 4. Decide what to work on next
/stv:what-to-work
```

---

## Plugin Structure

```
stv/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── spec/SKILL.md          # Phase 1: Feature Spec Interview
│   ├── trace/SKILL.md         # Phase 2: 7-Section Vertical Trace + RED Tests
│   ├── work/SKILL.md          # Phase 3: GREEN + Trace Conformance
│   ├── new-task/SKILL.md      # Orchestration: Vague requirements → spec+trace
│   ├── do-work/SKILL.md       # Orchestration: Autonomous execution loop
│   ├── what-to-work/SKILL.md  # Orchestration: Router
│   ├── what-we-have-to-work/SKILL.md  # Orchestration: Bundling
│   └── plan-new-task/SKILL.md # Orchestration: New feature proposal
└── prompts/
    └── decision-gate.md       # Switching-cost-based discriminator
```

---

## License

MIT
