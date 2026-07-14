# stv:think — Workflow Spec

> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/think/SKILL.md

## 1. Overview (Proposal) — inductive distillation

The skill is a methodology-design process that starts from experience and extracts minimal
structure. Its core principle: **strip away the unnecessary from what actually worked; do not fill
in from theory.** It is bottom-up (what succeeded in practice), never top-down design from an
imagined ideal. The output is a methodology/skill/process document sized to the experience.

## 2. Trigger Contract

Fires when the user wants real-world experience turned into a methodology, skill, or process:
"turn this into a methodology", "systematize my approach", "make this into a skill", "structure
this as a process". Within STV, trigger after `stv:explore` or after completed work — the moment
raw practice should become reusable structure. Does NOT fire for top-down theory design.

## 3. Workflow Trace — the 6-step process

```
real experience (2-3 lines that worked)
  → pattern recognition (find the invariant, not the differences)
  → minimal-structure draft (direction hint vs enforced procedure)
  → line-by-line executor simulation
       (ambiguous instruction causing wrong behavior → add constraint;
        excessive constraint → remove)
  → back-calculate missing pieces from failures (inductive "this failed without it",
     not deductive "logically this should be needed")
  → name anchoring (metaphor > functional description)
```

Step notes grounded in SKILL.md:
- Step 1: secure real successes ("I did this and it worked"); multiple experiences → lay side by
  side, extract the common structure.
- Step 3: if a 2-3 line experience becomes a 200-line doc, that is over-engineering.
- Step 4: e.g. "Follow the code" → jumps around → "Follow the callstack one step at a time,
  specifying filename:line".
- Step 6: if the name does not match the content, the content definition is still fuzzy.

## 4. Artifacts & Side Effects

- A methodology/skill/process document, sized to the experience.
- The over-engineering checklist is the **exit gate** — verify before shipping:
  - >10x longer than the actual experience?
  - Verbosely explaining what the executor already knows?
  - Sub-process separation truly necessary, or would a single file suffice?
  - Does a router/dispatcher pattern justify the actual complexity?
- If any apply, cut it down. Minimal structure is optimal.

## 5. Error Paths & NEVER

- NEVER fill structure from theory ("logically this should also be needed"); only add pieces that
  failed without them in practice.
- Over-engineering signals (checklist above) = stop and cut, do not ship.
- Ambiguous instructions that misdirect the executor are defects — fix by adding a constraint;
  over-constraint is equally a defect — fix by removing.

## 6. Acceptance Checklist

- [ ] Output grounded in 2-3 lines of real experience, not theory.
- [ ] Invariant across experiences identified.
- [ ] Draft distinguishes direction hints from enforced procedure.
- [ ] Each instruction survives line-by-line executor simulation.
- [ ] Missing pieces added inductively from actual failures.
- [ ] Name anchors identity (metaphor preferred).
- [ ] Over-engineering checklist passed.

## 7. Improvement Delta (2026-07-14)

- Description converted to the "Use when…" discovery convention the other STV skills now follow;
  methodology content unchanged.
