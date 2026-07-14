# STV Client Surface (Section 0) — Spec

> STV Spec | Created: 2026-07-14

## 1. Overview

### Proposal
- **Why**: STV exists to stop surface-only AI implementations, yet its 7-section Vertical Trace starts at API Entry — the client leg (frontend → dto → api and the response back to the UI) sits outside the trace. A feature with a UI can still be faked at exactly the layer STV was built to protect: an agent renders the screen, never wires it to the API, and produces a receipt. The methodology owner's stated surface is `frontend – dto – api – backend service – dto/protocol – other services/db/cache` **round trip**; the trace must cover the whole loop.
- **What Changes**: A conditional **Section 0 (Client Surface)** is added to the Vertical Trace format; parameter transformation arrows gain a client leg on both directions; work's conformance checklist, spec's architecture template, and the README format/glossary carry the same contract.
- **Capabilities**: Traces for UI-bearing features now specify UI entry → client transformation → request, and response → UI rendering, plus per-error-path user-visible display. Separate-repo clients are recorded as CDC boundaries instead of being silently skipped.
- **Impact**: `plugins/stv/skills/trace/SKILL.md`, `plugins/stv/skills/work/SKILL.md`, `plugins/stv/skills/spec/SKILL.md`, `plugins/stv/README.md`. Non-BREAKING: Section 0 is conditional; pure-backend features are untouched.

## 2. User Stories

- As a backend-leaning owner driving AI agents, I want the client leg locked into the trace before code, so that an agent cannot fake a feature at the frontend and hand me a receipt.
- As an implementer, I want the return leg (Response.field → UI state) specified, so that "API works in curl" can never be conflated with "feature works".
- As a maintainer with a separate frontend repo, I want the client↔API boundary recorded as CDC, so that cross-repo features keep an explicit contract instead of an untraced gap.

## 3. Acceptance Criteria

- [x] trace SKILL: Section 0 block (conditional, MANDATORY when a UI/client exists) precedes Section 1 in the format spec.
- [x] trace SKILL: arrows extend on both legs — `UI.fieldA → Request.X → … → table.col` and `table.col → … → Response.field → UI.render`.
- [x] trace SKILL: Granularity Rule counts "a client surface exists" as a full-trace trigger; Phase 2 checklist includes Section 0.
- [x] work SKILL: conformance checklist gains a Section 0 block (event fires request / client transformation / response rendering / error display / CDC boundary).
- [x] spec SKILL: architecture template gains a Client Surface subsection (§5.2) and the layer overview names the full round trip; interview must cover it (or N/A).
- [x] README: format block, section-role table, arrow extension, glossary entry, and the "What Vertical Trace Solves" rationale carry Section 0.

## 4. Scope

### In-Scope
- The four documentation files above.

### Out-of-Scope
- A client-side test harness or UI test tooling prescription.
- Renumbering existing sections 1–7 (Section 0 prefixes; Delta cascade avoided by design).
- Mandating Section 0 for pure-backend features.

## 5. Architecture

Section 0 is a **prefix section**, not an eighth tail section: numbering of 1–7 is stable, so existing traces need no Delta churn. The client leg participates in the Contract test category through the extended arrows; when the client lives in another repo, the boundary degrades to a CDC contract (same pattern the methodology already uses for microservices).

## 6. Non-Functional Requirements

- Conditionality must be unambiguous: "has a UI/client" triggers MANDATORY; otherwise the section is absent (not empty).

## 7. Auto-Decisions

| Decision | Tier | Rationale |
|----------|------|-----------|
| Number the section 0 instead of renumbering 1–7 | small | Avoids Delta MODIFIED cascade across every existing trace |
| Reuse CDC (existing STV concept) for separate-repo clients | small | One boundary concept instead of two |

## 8. Open Questions

None.

## 9. Delta Log

Initial creation, 2026-07-14. Implemented in the same change set (see trace.md).

## 10. Next Step

→ trace.md in this directory records the per-file execution paths and their verification.
