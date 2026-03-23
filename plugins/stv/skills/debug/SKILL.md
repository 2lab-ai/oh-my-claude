---
name: blackbox-debugging
description: Record-based debugging methodology. Use on bug reports, debugging requests, "why does this happen", "find the bug", "form a hypothesis", "follow the callstack", "trace back from the result". Trigger this skill in any situation where code behaves differently from expectations. Even without the explicit word "debugging", trigger on symptom reports like "why is this happening", "it's behaving oddly", "the result is different".
---

# Blackbox Debugging

A debugging methodology that records everything like an airplane black box while hunting for the root cause.
Core constraint: **An unexplored branch is an unexamined branch.**

---

## 1. Problem Definition — AS-IS / TO-BE Confirmation

Before starting, always confirm with the user:

- **Forward**: "Did X, got Y → doing X should produce Z"
- **Reverse**: "Got Y → should have been Z"

The gap between AS-IS and TO-BE is the bug. **Do not start debugging without confirmation.**

## 2. Tracing — Follow the Callstack While Recording in trace.md

Create a debugging log file:

```
docs/debugging/{issueID}-{YYYYMMDDhhmm}/trace.md
```

Follow the callstack **one step at a time** from the entry point, recording in this file.

### Recording Rules

- At each step, specify the **actual filename:line number**.
- At conditional branches, record **which condition leads where**.
- **API calls to other services, DB queries, and message queue publications are part of the callstack.** When crossing service boundaries, follow into that service's code and continue tracing.
- **Do not assume.** Only write what you have directly read and verified in the code.

### Exploration Strategy: Heuristic → Exhaustive

1. **Phase 1 — Heuristic**: Quickly check the **top-3 most likely hypotheses** first.
2. **Phase 2 — Exhaustive**: If top-3 yields nothing, draw the callstack graph in trace.md and **exhaustively explore every branch by actually writing each one down**.

## 3. Verification — Red-Green Cycle

Once a hypothesis is identified:

1. Write a test that reproduces the bug first (**Red** — confirm the test fails)
2. Apply the fix
3. Confirm the test passes (**Green**)
4. Confirm existing tests are not broken (regression prevention)

---

## trace.md Example

```markdown
# Bug Trace: ISSUE-1234 — Soccer team names appear in results

## AS-IS: Movie search results include soccer team names mixed in
## TO-BE: Movie search results should only contain movies

## Phase 1: Heuristic Top-3

### Hypothesis 1: Search query runs without category filter
- `SearchController.cs:45` → calls `SearchService.Query()`
- `SearchService.cs:112` → check categoryFilter parameter → **passed as null** ✅ Likely

### Hypothesis 2: DB table join is incorrect
- `SearchRepository.cs:78` → check SQL → join is correct ❌ Ruled out

### Hypothesis 3: Response mapping mixes in other entities
- `SearchMapper.cs:34` → check mapping logic → correct ❌ Ruled out

## Conclusion: Hypothesis 1 confirmed — categoryFilter passed as null to SearchService.Query()
```
