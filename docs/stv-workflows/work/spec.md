# stv:work — Workflow Spec
> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/work/SKILL.md

## 1. Overview (Proposal)

work is STV Phase 3: take a `trace.md` and drive its scenarios to GREEN, then verify the implementation conforms to the trace document (SKILL.md:6-10). Two loops in sequence — Implementation Loop (write code that passes contract tests) then Trace Verify Loop (code matches the trace, 7-section criteria) — with the trace as source of truth throughout (SKILL.md:34-36,52-55). Every decision passes the Decision Gate + Sizing Rubric sourced from `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` (SKILL.md:14-18).

## 2. Trigger Contract — trace path + OPTIONAL scenario_ids (targeted execution)

Invoked with a trace path and OPTIONAL `scenario_ids` for targeted execution (SKILL.md:3). Use when trace scenarios need implementation to GREEN plus trace-conformance verification. Context loading first: read trace.md (missing → guide user to `stv:trace`), read the referenced spec.md, check contract tests are RED, set implementation order = scenario order in trace (dependencies first) (SKILL.md:22-31). Scope resolution: if `scenario_ids` were provided (bundle contract from do-work / what-we-have-to-work), the scenario loop operates ONLY on those rows (`targetedRows[] → verifyQueue[]`); a provided id absent from the trace → STOP with a targeted-scope mismatch error; omitted → all unfinished scenarios in scope (SKILL.md:32).

## 3. Workflow Trace

```
trace.md
  → scope resolution: scenario_ids → targetedRows[] → verifyQueue[]  (SKILL.md:32)
        · provided id ∉ trace → STOP (targeted-scope mismatch, never widen)
        · omitted → all unfinished scenarios
    ↓
per-scenario GREEN loop (trace = source of truth; ONE scenario at a time) (SKILL.md:36-59)
  for each scenario in scope:
    1. re-read scenario trace
    2. implement per trace's 7 sections (Layer Flow / Side Effects / Error Paths exactly)
    3. run contract tests for THIS scenario
    4. GREEN → next; RED → fix against trace, re-run
  · exact names/signatures from trace; add nothing not in trace (differ → update trace first)
  · GREEN scenario 1 → scenario 2 → …; previous breaks → fix immediately
  · primary gate = trace-driven Contract/Component tests (fast, stable, merge-blocking);
    E2E = secondary, minimal, deploy-only, non-blocking                     (SKILL.md:66-93)
    ↓
gap self-check (BEFORE trace verify) — re-read spec.md, list features, 5 gap types:  (SKILL.md:99-116)
  assumption_injection · scope_creep · direction_drift · missing_core · over_engineering
  detected → log type+fix, 1 autonomous correction, persists → ask user, re-run affected tests
    ↓
7+1-section trace conformance verify (per in-scope scenario)                         (SKILL.md:118-168)
  Section 0 Client Surface (if trace has one): UI event→request, UI.field→Request.field,
    Response.field→UI state, each §5 error → user-visible display, separate-repo client↔API = CDC
  §1 API Entry · §2 Input · §3 Layer Flow (Request→Command→Entity→table.col chain) ·
  §4 Side Effects · §5 Error Paths · §6 Output · §7 Observability
    ↓
mismatch protocol (fix trace OR fix code, NEVER diverge)                             (SKILL.md:170-196)
  trace wrong (impl better) → update trace.md + tests → re-verify
  code wrong (trace right)  → fix code → re-run tests → re-verify
  hard judgment → ask user;  ★ record in Trace Deviations; mark Verified only when GREEN + aligned
    ↓
File Map verification (after scenario verify loop)                                   (SKILL.md:198-210)
  extract file paths from §3c Persisted files + §4 Side Effects (in-scope scenarios only — scenario_ids if provided, else all)
  → check each vs `git diff --name-only`; unmodified → read scenario, implement, re-run
  ★ tests ⊂ spec; File Map = full modification surface
    ↓
completion report (§4)
```

Artifact Backtrack protocol — going back is not failure (SKILL.md:270-311). Always fix upstream first: **spec → trace → code**. Spec assumption/architecture wrong → backtrack to SPEC (re-invoke `stv:spec` update or Update-vs-New tree); trace section wrong / new scenario → backtrack to TRACE (update in-place + Delta Protocol). Record every backtrack in Trace Deviations; re-run affected contract tests; never silently diverge.

## 4. Artifacts & Side Effects

- Code driven to GREEN against trace-driven contract tests (primary gate) (SKILL.md:66-93).
- `trace.md` Implementation Status updated — 5-column table `Scenario | Trace | Tests | Verify | Status` (done/GREEN/Verified/Complete) (SKILL.md:218-223).
- `trace.md` Trace Deviations section: every mismatch fix + backtrack, with reason and what changed ("None" if empty) (SKILL.md:184,225-226,309).
- Verified At line + user report: `{N}/{N}` GREEN, Scope (all | targeted: scenario_ids), `{N}/{N}` Trace Verified, deviations count, test results, files modified, File Map coverage (SKILL.md:228-258).

## 5. Error Paths & NEVER

- Targeted-scope mismatch: a provided `scenario_id` not in the trace → STOP, do not widen to recover (SKILL.md:32).
- Gap ignored: gap correction takes priority over all other fixes; runs BEFORE trace verify (SKILL.md:112-116,320-321).
- Trace/code out of sync: mismatch must resolve to trace-update OR code-fix; recorded in Trace Deviations (SKILL.md:170-196,311).
- File Map decoration: trace lists a file, no diff → not complete; implement the missing change (SKILL.md:198-210).
- NEVER (SKILL.md:313-325): add features not in trace as "improvements"; modify tests to force GREEN (fix impl instead); declare complete without verify; ignore mismatches; leave trace and code out of sync; skip gap self-check before trace verify; ignore detected gaps; declare complete with unmodified File Map files; treat test coverage as spec coverage; **execute scenarios outside the provided `scenario_ids` scope (scope widening)**; **mark Status=Complete while Verify ≠ 'Verified'**.

## 6. Acceptance Checklist

- [ ] Trace + referenced spec read; contract tests confirmed RED before implementation (SKILL.md:22-29).
- [ ] Scope resolved: if `scenario_ids` given, loop + verify operate ONLY on targetedRows; missing id stopped (SKILL.md:32,190).
- [ ] Each in-scope scenario driven GREEN one at a time, trace as source of truth (SKILL.md:36-59).
- [ ] Gap self-check (5 types) ran BEFORE trace verify; ≤1 autonomous correction else escalated (SKILL.md:99-116).
- [ ] 7+1-section conformance passed incl. Section 0 Client Surface where the trace has one (SKILL.md:125-168).
- [ ] Every mismatch resolved via protocol and logged in Trace Deviations — trace and code synchronized (SKILL.md:170-196).
- [ ] File Map: every §3c/§4 file shows a `git diff` (SKILL.md:198-210).
- [ ] Status=Complete set only when Verify='Verified' for all in-scope scenarios (SKILL.md:325).

## 7. Improvement Delta (2026-07-14)

- Scope resolution step added (SKILL.md:32): a provided `{scenario_ids}` bundle contract narrows the scenario loop to `targetedRows[] → verifyQueue[]`; a scenario_id absent from the trace stops with a targeted-scope mismatch instead of widening.
- Loop and verify operate in-scope only (SKILL.md:39,190): both the GREEN loop and the Verify Loop iterate the resolved scope, not all scenarios; report states Scope (all | targeted) (SKILL.md:238).
- Section 0 Client Surface conformance block added (SKILL.md:125-130): verifies UI event→request wiring, UI↔Request/Response field transforms, per-error user-visible display, and separate-repo client↔API as a CDC boundary.
- NEVER additions (SKILL.md:324-325): executing scenarios outside the provided `scenario_ids` (scope widening), and marking Status=Complete while Verify is not 'Verified'.
