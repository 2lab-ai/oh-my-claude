---
name: debug
description: Trigger this skill in any situation where code behaves differently from expectations like "why does this happen", "find the bug", "form a hypothesis", "follow the callstack", "trace back from the result". Even without the explicit word "debugging", trigger on symptom reports.
---

# stv:debug: 'Blackbox Debugging'

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
~/.claude/stv/debugging/{issueID}-{YYYYMMDDhhmm}/trace.md
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

## 4. Systematic Debugging Principles

The above blackbox method covers **how to trace**. These principles cover **how to think** while debugging.

### 4a. Reproduce First

- **재현 없이 수정하지 마라.** 재현할 수 없으면 계측(instrumentation)부터 추가하라.
- 재현 가능하면 → 가설 수립. 재현 불가면 → 로그/계측 추가 후 재실행.

### 4b. Single Hypothesis per Iteration

- 한 번에 **하나의 가설만** 검증한다.
- 여러 수정을 동시에 하면 뭐가 효과인지 모른다.
- 가설이 틀리면 **원복하고** 새 가설을 세워라.

### 4c. Root-Cause Tracing

- 증상이 나타난 곳이 아니라 **원인이 시작된 곳**을 찾아라.
- 콜스택을 **역방향으로** 추적: "이 값은 어디서 왔나?" → "그걸 누가 넘겼나?" → 원점까지.
- 증상 지점에서 수정하면 다른 경로로 같은 버그가 재발한다.

### 4d. Condition-Based Waiting (Flaky Test 대응)

- `setTimeout`/`sleep` 대신 **조건 폴링**을 써라.
- 패턴: `waitFor(() => condition, timeout)` — 10ms 간격 폴링 + 타임아웃 필수.
- 타이밍 테스트가 아닌데 임의 딜레이를 쓰면 flaky의 원흉.

### 4e. Defense-in-Depth (버그 수정 후)

- 버그를 고친 뒤, **데이터가 지나는 모든 레이어에 검증을 추가**하라.
- 4개 레이어: Entry Point → Business Logic → Environment Guard → Debug Instrumentation.
- 한 곳만 막으면 다른 코드 경로로 우회된다. 구조적으로 불가능하게 만들어라.

### 4f. 3회 실패 시 아키텍처 의심

- 3번 연속 수정이 실패하면 **멈추고 구조를 의심**하라.
- 각 수정이 다른 곳에서 새 문제를 만들면, 그건 버그가 아니라 설계 문제다.
- 더 고치지 말고 유저/Oracle과 상의하라.

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
