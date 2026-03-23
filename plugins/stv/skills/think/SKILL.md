---
name: inductive-distillation
description: Meta-skill for designing methodologies, skills, and processes from experience. Triggers on "I want to turn this into a methodology", "organize this pattern", "systematize my approach", "make this into a skill", "structure this as a process". Use when the user mentions real-world experience and wants to structure/systematize/formalize it. Not top-down design from theory, but bottom-up distillation that strips away the unnecessary from what actually worked.
---

# Inductive Distillation

A methodology design process that starts from experience and extracts minimal structure.
Core principle: **Strip away the unnecessary from what worked. Do not fill in from theory.**

---

## Process

### 1. Start from Real-World Experience

First, secure experiences where the user actually succeeded (even 2-3 lines).
The raw material is **"I did this and it worked"**, not "theoretically it should be this way."
If there are multiple experiences, lay them side by side and extract the common structure.

### 2. Pattern Recognition

Extract common principles across experiences.
Is only the direction different? Only the scale? Only the domain? — Find the **invariant**, not the differences.

### 3. Draft with Minimal Structure

The most important thing in the first structuring pass is **not overdoing it**.
If the experience succeeded in 2-3 lines, creating a 200-line process document is over-engineering.
Distinguish between what a sufficiently smart executor (human or AI) needs as **just a direction hint** versus what requires **enforced procedure**.

### 4. Line-by-Line Real-World Simulation

Simulate each sentence of the draft as "If I give this to an executor, how will they actually behave?"

- "Follow the code" → they jump around arbitrarily → "Follow the callstack one step at a time, specifying filename:line number"
- "Explore all branches" → they do it mentally and skip some → "Write it down as you explore. What isn't written wasn't explored."

**If an ambiguous instruction causes wrong behavior, add a constraint. If a constraint is excessive, remove it.**

### 5. Back-Calculate Missing Pieces from Experience

Fill in with "when we actually tried it, omitting this caused failure."
Add inductively ("this failed without it in practice"), not deductively ("logically this should also be needed").

### 6. Anchor Identity with a Name

A good name makes **what the methodology actually does** sharp and clear in one word.
Metaphors (Blackbox, Dead Reckoning) have stronger identity than functional descriptions (A* Debug).
If the name doesn't match the content, the name isn't wrong — the content definition is still fuzzy.

---

## Over-Engineering Checklist

After structuring, verify the following:

- [ ] Is the document more than 10x longer than the actual experience?
- [ ] Are you verbosely explaining what the executor already knows?
- [ ] Is sub-process separation truly necessary, or would a single file suffice?
- [ ] Does a router/dispatcher pattern justify the actual complexity?

If any of these apply, cut it down. **Minimal structure is optimal.**
