# stv:do-work — Workflow Spec
> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/do-work/SKILL.md

## 1. Overview (Proposal)

do-work automates the complete STV implementation workflow: select unfinished trace scenarios → implement via `stv:work` → quality gates → loop until done (SKILL.md:10). Core principle: scan `trace.md` for ready scenarios, bundle into work chunks, execute with `stv:work`, commit, repeat (SKILL.md:12). Every decision passes the Decision Gate + Sizing Rubric sourced from `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` (SKILL.md:14-18).

## 2. Trigger Contract — Use-when / NOT-when

Use when: a `trace.md` with unfinished scenarios exists; ready for autonomous execution; user wants minimal interruption until done; a bundle contract `{trace_path, scenario_ids}` was handed off from `what-we-have-to-work` (SKILL.md:22-26).
NOT when: no `trace.md` exists (use `stv:new-task` first); user asked a single specific question; exploring/researching without implementation (SKILL.md:28-32).

## 3. Workflow Trace — Phase A→B→C→D loop

```
Phase A (Task Selection, ~5min)
  step 0: bundle contract {trace_path, scenario_ids}
          → validate trace_path exists AND every scenario_id ∈ trace Implementation Status
          → valid: SKIP global glob discovery (steps 1 + scan of 3) = contract IS the scope
          → mismatch: STOP with targeted-scope error (NEVER widen to recover)   (SKILL.md:50-54)
  → File Map extraction: trace §3c Persisted files + §4 side effects (UPDATE/INSERT/DELETE)
          → dedupe → File Map Checklist (the real completion list; tests ⊂ File Map)  (SKILL.md:61-66)
  → prioritize (dependency order; integration-first: 200+ line existing files first) (SKILL.md:68-72)
  → bundle (target xlarge, cap xlarge, split if >xlarge) → present bundle + Contract (SKILL.md:74-103)
    ↓
Phase B (STV Work Execution) → Skill(stv:work) with SAME targeted scope (SKILL.md:110-113)
  gate chain (in order):
    File Map Completion Gate → Gap Detection → Quality Gates → Spec Re-verification → Finalize
    · File Map Completion Gate: git diff --name-only per Checklist file; any NOT modified →
      re-read scenario, implement missing change, re-run tests; do NOT proceed until 100% (SKILL.md:120-135)
    · Gap Detection: re-read spec.md, check 5 gap types (assumption_injection, scope_creep,
      direction_drift, missing_core, over_engineering); 1 autonomous correction, else → Phase D (SKILL.md:137-144)
    · Quality Gates: test / build / lint (project-specific)                             (SKILL.md:146-152)
    · Spec Re-verification: each spec acceptance criterion covered by test/§4/code else implement (SKILL.md:154-163)
    · Finalize (environment-dependent): commit referencing scenarios; push/PR ONLY where host
      policy allows; unknown policy → commit local + report, never invent a push               (SKILL.md:166-170)
    ↓
Phase C (Context Check) → harness signal >~70%: checkpoint + compact/resume;
    no signal: checkpoint trace after EVERY bundle, prefer bundle-boundary stop (SKILL.md:176-181)
    ↓
Phase D (Loop Decision) → loop back to A if more scenarios + clear + no blocker + budget OK;
    STOP+report if all complete / unclear / arch decision (switch cost ≥ medium, no generic
    pattern) / near context limit / milestone / 2nd gap correction failed (SKILL.md:188-200)
```

## 4. Artifacts & Side Effects

- Reads: `docs/*/trace.md` (Implementation Status, §3c, §4), `docs/{feature}/spec.md`.
- Writes: source/config files per File Map; `trace.md` Implementation Status updates (checkpoint) (SKILL.md:116,179).
- Emits: Work Bundle table + Contract (SKILL.md:82-103); Auto-Decision Log for sub-small decisions (SKILL.md:242); Work Session Report on stop (SKILL.md:204-223).
- Git: local commit referencing trace scenarios by default; push/PR is conditional (see §5).

## 5. Error Paths & NEVER

- Scope-widening violation: rescanning the repo despite a valid bundle contract is a contract violation; mismatch → stop, never widen (SKILL.md:52-54,268,291).
- Protected-branch push ban: pushing to protected/default branch without the host's ship gate is forbidden; unknown policy → commit local + report (SKILL.md:168,170,292).
- "Test pass = done" bias: all tests GREEN but integration unwired/config stale — File Map Gate + Spec Re-verification catch it (SKILL.md:274).
- File Map as decoration: trace lists 5 files, only 3 modified — every §3c/§4 file MUST show a diff (SKILL.md:275).
- Complexity avoidance: new util files created while 500-line core pipeline untouched — integration-first ordering; the wiring IS the feature (SKILL.md:276-278).
- NEVER (SKILL.md:282-292): start without trace.md; skip quality gates; skip gap detection (runs BEFORE quality gates); ignore context mgmt; skip logging autonomous decisions; >1 gap correction per bundle; declare complete with unmodified File Map files; skip Spec Re-verification before commit; treat test coverage as spec coverage; widen beyond contract; push protected/default without ship gate.

## 6. Acceptance Checklist

- [ ] If a bundle contract was given, it was validated and honored (no global rescan; mismatch stopped).
- [ ] File Map extracted from trace §3c + §4 and every listed file shows a diff.
- [ ] Gap Detection ran BEFORE quality gates; ≤1 autonomous correction, else escalated to Phase D.
- [ ] Quality gates (test/build/lint) all pass and Spec Re-verification ran before commit.
- [ ] Autonomous decisions (≤ small) recorded in Auto-Decision Log; ≥ medium switching cost escalated.
- [ ] Context checkpointed at bundle boundaries; trace Implementation Status updated.
- [ ] Finalize matched host policy — no push to protected/default branch without a ship gate.

## 7. Improvement Delta (2026-07-14)

- Explicit bundle-contract step 0 (SKILL.md:50-54): a valid `{trace_path, scenario_ids}` skips global trace rescan and IS the scope; scope mismatch stops with a targeted error instead of widening.
- Commit&Push → environment-dependent Finalize (SKILL.md:166-170): commit stays default, but push/PR now requires the host's ship gate; protected/default-branch push without it is forbidden; unknown policy → commit local + report.
- Context check made harness-aware (SKILL.md:176-181): uses `/compact` only if the harness exposes context usage; with no signal, checkpoints at every bundle boundary rather than assuming a threshold tool exists.
- NEVER additions (SKILL.md:291-292): scope widening beyond the contract, and protected/default-branch push without the host ship gate.
