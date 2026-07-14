# stv:debug — Workflow Spec

> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/debug/SKILL.md

## 1. Overview (Proposal)

**Blackbox Debugging: record everything like an airplane black box while hunting the root cause**
(SKILL.md:6-9). The core constraint — *an unexplored branch is an unexamined branch* — makes the
written trace the evidence: a branch is explored only when it is written down. debug traces the real
callstack from an entry point to where the symptom is born, records every hop at `file:line`, then
proves the fix with a red→green cycle and folds the durable root cause back into the owning contract.

## 2. Trigger Contract

**Use when** (SKILL.md:3): code behaves differently from expectations — "why does this happen",
"find the bug", "follow the callstack", or any symptom report, even without the explicit word
"debugging".

**NOT when / precondition:** never start without AS-IS/TO-BE confirmation (SKILL.md:20) — the gap
between them *is* the bug, and debugging without it is guessing.

## 3. Workflow Trace

```
symptom → AS-IS/TO-BE confirmation (forward + reverse, no debugging without it, SKILL.md:13-20)
  → ./.claude/stv/debugging/{issueID}-{YYYYMMDDhhmm}/trace.md (CWD-relative, SKILL.md:22-30)
        3 path guards: never home-.claude / gitignore before first write / disposable-evidence lifecycle (:32-36)
  → Phase 1 Heuristic: check top-3 most-likely hypotheses first (:49)
  → Phase 2 Exhaustive: draw callstack graph, walk EVERY branch by writing each down (:50)
        recording rules: file:line each hop, branch conditions, cross-service (API/DB/MQ) hops, no assumptions (:42-45)
  → Red-Green fix: repro test RED → fix → GREEN → regression check (:56-59)
  → root cause folded back to issue/PR/spec + vertical trace Delta (:60, SKILL.md:36)
```

- **6 systematic principles — how to *think* while tracing (SKILL.md:63-100):** reproduce-first
  (instrument if not reproducible, 4a) · single hypothesis per iteration, revert on miss (4b) ·
  root-cause tracing backward to origin, not the symptom site (4c) · condition-based waiting over
  `sleep`/`setTimeout` for flaky tests (4d) · defense-in-depth across all 4 layers after the fix (4e) ·
  3 consecutive failed fixes → stop and suspect architecture (4f).

## 4. Artifacts & Side Effects

- **Debugging trace.md — scratch, disposable** (SKILL.md:22-30): `./.claude/stv/debugging/{issueID}-{ts}/trace.md`,
  CWD-relative for multi-tenant/multi-session isolation. Records AS-IS/TO-BE, Phase-1 top-3, and the
  exhaustive branch walk (example at SKILL.md:104-125). Its lifecycle *ends* with the investigation.
- **The feature's vertical trace — the contract** (`docs/{feature}/trace.md`, SKILL.md:60): durable.
  The distinction is load-bearing — durable knowledge (root cause, red→green test, fix rationale)
  moves *out* of the scratch dir *into* the contract; the scratch dir never outlives the investigation.
- Side effect: on a git checkout, `.claude/stv/` is appended to `.git/info/exclude` before the first
  trace write (SKILL.md:35), and the code fix + regression tests land in the project tree.

## 5. Error Paths & NEVER

- **NEVER write to the home-level `.claude`** (SKILL.md:34): a trace path resolving to `~/.claude`,
  `$HOME/.claude`, `/Users/<user>/.claude` is a run bug, not a fallback. If the CWD is unwritable,
  stop and surface it — do not fall back to home.
- **NEVER let a trace dir leak into a commit** (SKILL.md:35): gitignore `.claude/stv/` before the
  first write; a debugging trace in a commit is scratch entering the tree.
- **NEVER start debugging without AS-IS/TO-BE** (SKILL.md:20) and **NEVER assume a hop** — only write
  what you directly read in code (SKILL.md:45).
- **NEVER fix at the symptom site** (SKILL.md:82) — same bug re-emerges via another path.
- 3 failed fixes → **stop**, consult user/Oracle, do not keep patching (SKILL.md:96-100).

## 6. Acceptance Checklist

- [ ] AS-IS/TO-BE confirmed (forward + reverse) before any tracing.
- [ ] Trace dir is CWD-relative `./.claude/stv/debugging/…`; not home `.claude`; gitignored on a checkout.
- [ ] Callstack recorded one hop at a time with actual `file:line`, branch conditions, and cross-service hops.
- [ ] Phase 1 top-3 done; if inconclusive, Phase 2 exhaustive branch walk written down for every branch.
- [ ] Fix proven red→green with a reproduction test; regression suite still passes.
- [ ] Root cause folded into the owning issue/PR/spec AND the feature's `docs/{feature}/trace.md` via Delta Protocol.
- [ ] Scratch trace dir handled per lifecycle rule (left for session sandboxes, removed in long-lived checkouts).

## 7. Improvement Delta (2026-07-14)

- **Description made trigger-based** (SKILL.md:3) — reframed from "trigger this skill in any
  situation…" to a WHEN + methodology-summary form matching the description contract.
- **Root-cause → vertical-trace Delta feedback step added** (SKILL.md:60) — Verification step 5 now
  folds a confirmed root cause back into `docs/{feature}/trace.md` (wrong transform → MODIFIED,
  missing error path → ADDED), closing the Feedback Loop between debug findings and the trace contract
  so trace and code stay synchronized.
