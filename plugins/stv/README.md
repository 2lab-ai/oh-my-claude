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

## Recommended Usage

STV has two layers:

- **A. Core engine**: `spec → trace → work`
- **B. Default product UX**: `new-task → do-work`

The recommended day-to-day flow is **B**.

### Default Surface

Use these commands most of the time:

| Skill | When to use it | Role |
|-------|----------------|------|
| `stv:new-task` | Starting a new feature or clarifying a vague requirement | Creates `spec.md` and `trace.md` |
| `stv:do-work` | Implementing or continuing traced work | Executes scenarios from the trace and drives them to GREEN + verify |
| `stv:what-to-work` | You do not know what to work on next | Finds unfinished traced work first, then suggests new work only if backlog is empty |

### Advanced / Manual Control

Use these only when you intentionally want lower-level control:

| Skill | When to use it directly | Role |
|-------|--------------------------|------|
| `stv:spec` | You want to stop at requirements and architecture first | Manual Phase 1 |
| `stv:trace` | You already have a spec and want to derive traces/tests manually | Manual Phase 2 |
| `stv:work` | You want to implement a specific trace or specific scenarios directly | Manual Phase 3 |

### Internal Orchestration

These exist to support routing and bundle selection. They are not intended to be the primary user-facing entry points.

| Skill | Intended use |
|-------|---------------|
| `stv:what-we-have-to-work` | Internal bundling helper used by `stv:what-to-work` |
| `stv:plan-new-task` | Internal planning helper used when no unfinished traced work remains |

### Practical Rule

If you are wondering which command to run:

- New idea or vague request -> `stv:new-task`
- Ready to implement or continue -> `stv:do-work`
- Not sure what is next -> `stv:what-to-work`
- Need manual phase control -> `stv:spec`, `stv:trace`, or `stv:work`

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

### Default Surface

| Skill | Role | Input → Output |
|-------|------|----------------|
| `stv:new-task` | Default planning entry point | Vague feature request → `docs/{f}/spec.md` + `docs/{f}/trace.md` |
| `stv:do-work` | Default execution entry point | Trace backlog or selected trace scope → code + verified trace rows |
| `stv:what-to-work` | Optional navigation entry point | Existing traces → next execution recommendation |

### Advanced / Manual Control

| Skill | Phase | Role | Input → Output |
|-------|-------|------|----------------|
| `stv:spec` | 1. Spec | PRD + Architecture interview | Feature description → `docs/{f}/spec.md` |
| `stv:trace` | 2. Trace | 7-Section Vertical Trace + RED tests | spec.md → `docs/{f}/trace.md` + tests |
| `stv:work` | 3. Verify | Implementation (GREEN) + Trace Conformance | trace.md or selected scenarios → code + verified trace |

### Internal Orchestration

| Skill | Role | Call Relationship |
|-------|------|-------------------|
| `stv:what-we-have-to-work` | Internal unfinished-scenario bundling | Used by `stv:what-to-work` before `stv:do-work` |
| `stv:plan-new-task` | Internal new-feature proposal | Used by `stv:what-to-work` when backlog is empty |

### Skill Flow Diagram

```
User: "Build this feature"
       │
       ▼
 ┌──────────────┐
 │   new-task   │   ← default planning entry point
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │   stv:spec   │
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │  stv:trace   │
 └──────┬───────┘
        │
        ▼
   spec.md + trace.md
        │
        ▼
 ┌──────────────┐
 │   do-work    │   ← default execution entry point
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │  stv:work    │
 └──────────────┘
```

```
User: "Continue implementation"
       │
       ▼
 ┌──────────────┐
 │   do-work    │
 └──────┬───────┘
        │
        ▼
   Select trace scope
        │
        ▼
 ┌──────────────┐
 │  stv:work    │
 └──────────────┘
```

```
User: "What should I work on?"
       │
       ▼
 ┌──────────────┐
 │ what-to-work │   ← optional navigator
 └──────┬───────┘
        │
   ┌────┴─────┐
   ▼          ▼
 Unfinished  No unfinished
 work        work
   │          │
   ▼          ▼
 ┌──────────────────┐   ┌───────────────┐
 │what-we-have-to-  │   │ plan-new-task │
 │work              │   │               │
 │ (internal helper)│   │ (internal helper)│
 └────────┬─────────┘   └───────┬───────┘
          │                     │
          ▼                     ▼
 ┌──────────────┐       ┌──────────────┐
 │   do-work    │       │   new-task   │
 │ (default exec)│      │ (default plan)│
 └──────┬───────┘       └──────┬───────┘
        │                      │
        ▼                      ▼
 ┌──────────────┐       ┌──────────────┐
 │  stv:work    │       │  stv:spec    │
 │ (GREEN+verify)│      │  stv:trace   │
 └──────────────┘       └──────────────┘
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

### Q: Which commands should I usually use?

Use the opinionated workflow by default:

- `stv:new-task` for planning
- `stv:do-work` for execution
- `stv:what-to-work` only when you want help choosing the next item

Treat `stv:spec`, `stv:trace`, and `stv:work` as advanced manual controls, not the normal starting point.

### Q: Do I need to call `spec`, `trace`, and `work` directly?

No. Those are the core engine phases. Most users should not need to invoke them directly for routine feature work.

Call them directly only when you want to pause at a specific phase:

- `stv:spec` when requirements and architecture need explicit review before tracing
- `stv:trace` when a spec exists and you want to regenerate the execution contract
- `stv:work` when you want to target a specific trace or scenario set manually

### Q: Do I need to write a trace for every scenario?

Focus on scenarios with core business logic. Simple CRUD GET (list queries) don't need full traces. Decision criteria: "Are there parameter transformations?", "Are there DB side-effects?", "Do error paths branch?" — if any apply, write a trace.

### Q: Won't trace documents become unmanageable when they grow large?

Keep one `docs/{feature}/trace.md` by default and structure it by scenario sections plus the `Implementation Status` table. Only split further if you intentionally redesign the workflow and update the orchestration skills together.

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
# Recommended default flow

# 1. Start a new feature
/stv:new-task "Partner tracking link CRUD"

# 2. Execute the traced work
/stv:do-work

# 3. If you do not know what to work on next
/stv:what-to-work
```

### Advanced / Manual Control

```bash
# Use only when you intentionally want phase-level control
/stv:spec "Partner tracking link CRUD"
/stv:trace docs/tracking-link/spec.md
/stv:work docs/tracking-link/trace.md
```

### Generic Usage Outside Plugin Slash Commands

```text
new-task -> default planning
do-work -> default execution
what-to-work -> optional next-work navigator
spec / trace / work -> advanced manual control
```

---

## Plugin Structure

```
stv/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── new-task/SKILL.md      # Default user-facing planning entry point
│   ├── do-work/SKILL.md       # Default user-facing execution entry point
│   ├── what-to-work/SKILL.md  # Optional user-facing next-work router
│   ├── spec/SKILL.md          # Advanced manual Phase 1
│   ├── trace/SKILL.md         # Advanced manual Phase 2
│   ├── work/SKILL.md          # Advanced manual Phase 3
│   ├── what-we-have-to-work/SKILL.md  # Internal bundling helper
│   └── plan-new-task/SKILL.md # Internal planning helper
└── prompts/
    └── decision-gate.md       # Switching-cost-based discriminator
```

---

## License

MIT
