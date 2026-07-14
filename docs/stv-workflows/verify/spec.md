# stv:verify — Workflow Spec

> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/verify/SKILL.md

## 1. Overview (Proposal)

A PR can compile, pass CI, and still not do what its issue asked — or quietly do more. verify is the
**final Conformance Gate before merge** (SKILL.md:8): it cross-checks the spec carried by an issue
(Jira/Linear/GitHub) against the actual code changes in a PR using **3-dimensional verification —
Completeness, Correctness, Coherence** (SKILL.md:44-54). It is a read-only judgment skill: it extracts,
compares, and issues a verdict; it never mutates code. Every decision routes through the mandatory
Decision Gate (SKILL.md:12-14).

## 2. Trigger Contract — both inputs required

**Use when** (SKILL.md:3): a PR must be checked against its issue/spec before merge.

**Both inputs mandatory (SKILL.md:20-24):**
- **Issue** — URL or full contents; if neither, ask the user to provide MCP access or paste contents.
- **PR URL** — e.g. `https://github.com/xxx/yyy/pull/123`.

`Do not proceed unless both are provided` (SKILL.md:24). Handoff out: FAIL/PARTIAL verdict with a
suspected bug → suggest switching to **stv:debug** (SKILL.md:137).

## 3. Workflow Trace

```
issue (URL or contents)
  → Step 1 Extract Spec: AS-IS / TO-BE / Implementation Spec (SKILL.md:28-33)
        · AS-IS/TO-BE not explicit → infer + confirm with user (:35)
  → Step 2 Extract Changes from PR: diff via MCP, or gh pr diff / gh pr view --json files fallback (:39)
        → changed files + summary, core logic changes, test changes (:40-42)
  → Step 3 Determine Dimensions — Graceful Degradation by available artifacts (:56-63):
        issue-only → Completeness (1D); + spec.md → + Correctness (2D); + trace.md → + Coherence (3D)
        · detect artifacts, announce dimensions, apply only those (:65-68)
  → Step 4 Gap Detection (Ouroboros, feeds Correctness) — 5 types (:70-82):
        assumption_injection · scope_creep · direction_drift · missing_core · over_engineering
  → Step 5 Spec vs Implementation comparison, per applicable dimension (:89-109)
  → Step 6 Verdict, priority GAP_DETECTED > FAIL > PARTIAL > PASS (:111-118)
  → Report (STV Verify Report template, :139-166)
```

- **Graceful Degradation (SKILL.md:56-68):** dimensions scale to artifacts present — never claim
  Coherence without trace.md or Correctness without spec.md; announce the applied set before comparing.
- **Gap severity (SKILL.md:133):** a gap (wrong direction) outranks a quality issue; when both exist,
  report `GAP_DETECTED` and demote quality issues to secondary findings.

## 4. Artifacts & Side Effects

- **Report only, no file mutation.** Output is the STV Verify Report (SKILL.md:139-166): Issue/PR
  header, Gap Analysis, Dimensional Assessment table, Spec Coverage table, Verdict, Action Required.
- Dimensional Assessment uses the fixed 3-row schema Completeness/Correctness/Coherence with
  ✅/⚠️/❌/N/A scores (SKILL.md:124-131, 152-158).
- Read-side inputs: the issue, the PR diff, and (when present) `docs/{feature}/spec.md` +
  `docs/{feature}/trace.md` for artifact detection (SKILL.md:66).

## 5. Error Paths & NEVER

- **NEVER proceed on one input** — missing issue or PR URL halts the run (SKILL.md:24).
- **NEVER assert a dimension without its artifact** — Correctness only if spec.md, Coherence only if
  trace.md exist (SKILL.md:56-63, 99, 105).
- **NEVER silently substitute AS-IS/TO-BE** — when inferred, confirm with the user first (SKILL.md:35).
- **Specificity mandatory (SKILL.md:135):** mismatches state exactly "X in issue, missing from PR" or
  "Y in PR, not in issue spec" — never a bare verdict.
- **Gap before checklist (SKILL.md:74):** run the 5-type gap analysis *before* per-item comparison;
  per-item checklists miss directional drift.

## 6. Acceptance Checklist

- [ ] Both inputs collected (issue URL/contents + PR URL); run halted if either missing.
- [ ] Spec extracted as AS-IS / TO-BE / Implementation Spec; inferred fields confirmed with user.
- [ ] PR changes extracted via MCP or gh fallback (diff + files + tests).
- [ ] Available artifacts detected; applied dimension set announced before comparison.
- [ ] 5-type Gap Detection run before spec-vs-impl comparison; each gap reported expected→actual→correction.
- [ ] Comparison applied per active dimension only; Dimensional Assessment table filled (N/A where absent).
- [ ] Verdict assigned by priority GAP_DETECTED > FAIL > PARTIAL > PASS; mismatches stated specifically.
- [ ] FAIL/PARTIAL with suspected bug → stv:debug handoff suggested; no code/files mutated.

## 7. Improvement Delta (2026-07-14)

- **Description made trigger-based** (SKILL.md:3) — rewritten from "Triggers on …" to "Use when a PR
  must be checked against its issue/spec before merge …", aligning with the WHEN+ARGS description
  convention and surfacing the required inputs.
- **gh CLI fallback for PR diff added** (SKILL.md:39) — `gh pr diff <PR-URL>` / `gh pr view <PR-URL>
  --json files` when no MCP connector is available, so the gate is no longer MCP-dependent.
