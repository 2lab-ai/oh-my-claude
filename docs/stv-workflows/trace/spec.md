# stv:trace — Workflow Spec

> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/trace/SKILL.md

## 1. Overview (Proposal)

A spec.md states *what* a feature does but never *how* an input becomes a persisted row and a
response — the gap where bugs hide. trace is **STV Phase 2: spec.md → `docs/{feature}/trace.md` +
RED contract tests** (SKILL.md:6-11), tracing each scenario from API entry → Handler → Service → DB
at parameter-level granularity, then deriving contract tests from the trace. It is a design/tracing
skill, not an implementer; the traced scenarios plus their RED tests become the executable contract
`stv:work` fills in.

## 2. Trigger Contract

**Use when** (SKILL.md:3): a spec.md exists and per-scenario vertical traces + RED contract tests
must be derived — OR an existing trace.md needs Delta Protocol updates.

**NOT when / preconditions:** no spec.md exists → guide user to run `stv:spec` first (SKILL.md:25).
Handoffs: emits → `stv:work` / `stv:do-work docs/{feature}/trace.md` (SKILL.md:314-315, 384-389).

## 3. Workflow Trace

```
spec.md (Phase 1: Read spec + Agent:Explore codebase → map entities/DTOs/enums → extract scenario list)
  → scenario list (from User Stories + Acceptance Criteria, SKILL.md:30)
  → Phase 2 Trace Interview — apply Decision Gate: tiny/small = autonomous, medium+ only = ask user (:35)
        · Update Mode: existing trace.md → diff spec → Delta Protocol classify → interview only changed
  → Phase 3: per-scenario 7+1-section Vertical Trace (:74)
        0. Client Surface [conditional] → 1. API Entry → 2. Input → 3. Layer Flow (3a Controller /
           3b Service / 3c Repository·DB) → 4. Side Effects → 5. Error Paths → 6. Output → 7. Observability
  → Phase 4: 4-category RED contract tests (Happy / Sad / Side-Effect / Contract, :203-208)
  → Phase 5: docs/{feature}/trace.md + RED test files
```

- **Double-leg arrows (MANDATORY, SKILL.md:166-177):** every Layer Flow specifies
  `Request.X → Command.Y → Entity.Z → table.col`. When Section 0 exists, extend both legs —
  client→DB `UI.fieldA → Request.X → Command.Y → Entity.Z → table.col` and the return leg
  `table.col → Entity → Response.field → UI.render`. Without the client leg a surface-only client can
  fake the feature; the round trip closes only when both legs are traced.
- **Granularity Rule (single source; README FAQ defers here, SKILL.md:179-184):** write a FULL trace
  (all sections) when ANY of — parameter transformations, DB side-effects, branching error paths, or
  a client surface exists. COMPACT (Sections 1/2/6 + one-line Layer Flow note) only for simple
  read-only flows (unfiltered list GET, no transformation). When in doubt, full.
- **Update mode → Delta Protocol (SKILL.md:37-44, 318-372):** classify each change ADDED / MODIFIED /
  REMOVED / RENAMED; update trace body in-place and append a dated `## Delta Log` entry.

## 4. Artifacts & Side Effects

- `docs/{feature}/trace.md` — Vertical Trace document (SKILL.md:229, structure :234-316):
  TOC → per-scenario 7 sections + Contract Tests table → Auto-Decisions → Implementation Status →
  Delta Log → Next Step.
- **Persisted-files list** (Section 3c, SKILL.md:129-133) — every path backtick-quoted; this list is
  **the source of truth for the do-work File Map gate**.
- RED contract test files in the project's test directory (SKILL.md:230).
- **Implementation Status — fixed 5-column schema** `Scenario | Trace | Tests | Verify | Status`
  (SKILL.md:305-310); a missing Verify column is a schema mismatch to fix, not a variant (:372).

## 5. Error Paths & NEVER

- **Future-tense ban (SKILL.md:177):** no "will implement" — use present/definitive tense
  ("transforms," "maps to," "converts"). A trace states what the code does, not intentions.
- **Missing sections hide bugs (SKILL.md:76):** format is flexible (MD/YAML/JSON) but every required
  section must be present — gaps in the 7+1 fields are where bugs hide.
- **Missing arrows (SKILL.md:176):** without parameter transformation arrows, bugs in the
  transformation process can be missed.
- **RED confirmation mandatory (SKILL.md:67, 218, 387):** all contract tests must compile and FAIL;
  run them to confirm RED before completion — a green-on-write test proves nothing.
- Delta: MODIFIED without Before/After = invisible change; REMOVED without Reason+Migration = info
  loss (SKILL.md:363-365).

## 6. Acceptance Checklist

- [ ] spec.md read + Agent:Explore run; scenario list extracted from User Stories + Acceptance Criteria.
- [ ] A Vertical Trace written for every scenario — FULL traces include all 7 sections; COMPACT traces (Granularity Rule) include Sections 1, 2, 6 + a one-line Layer Flow and carry the `> Compact trace` marker.
- [ ] Section 0 (client leg + return leg) present for every scenario with a UI/client surface.
- [ ] Layer Flow specifies parameter transformation arrows (Request.X → Command.Y → Entity.Z → table.col).
- [ ] Granularity Rule applied (full vs compact) — full when transform/side-effect/branch/client exists.
- [ ] Section 3c Persisted-files list present, all paths backtick-quoted (File Map source of truth).
- [ ] All 4 contract-test categories written and confirmed RED (compile but fail).
- [ ] Implementation Status uses the 5-column schema; no future-tense phrasing anywhere.
- [ ] Update runs: changes classified ADDED/MODIFIED/REMOVED/RENAMED with a dated Delta Log entry.

## 7. Improvement Delta (2026-07-14)

- **Section 0 Client Surface added** (SKILL.md:81-87) — conditional-mandatory for UI/client features;
  when the client lives in a separate repo it becomes a CDC boundary (contract defined here, client
  repo owns its own trace). Closes the surface-only-fake gap of API-Entry-first traces.
- **Arrows extended to both client legs** (SKILL.md:174) — round trip `UI → Request → … → table` and
  `table → … → Response → UI.render`; the trip is closed only when the client leg is specified.
- **Granularity Rule made the single source** (SKILL.md:179) — README FAQ now defers here instead of
  duplicating full-vs-compact criteria.
- **Implementation Status unified to 5 columns** `Scenario | Trace | Tests | Verify | Status` (:305);
  **Delta rule 6 added** (:372) — fixed status schema; a missing Verify column is a mismatch to fix.
