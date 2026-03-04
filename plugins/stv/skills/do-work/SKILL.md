---
name: do-work
description: "Autonomous work execution on STV-traced scenarios. Selects unfinished scenarios from trace.md, implements via stv:work, loops until done or user input needed."
---

# Do Work — STV Autonomous Execution

## Overview

**do-work automates the complete STV implementation workflow: select unfinished trace scenarios → implement via stv:work → quality gates → loop until done.**

Core principle: Scan trace.md for ready scenarios → Bundle into work chunks → Execute with stv:work → Commit → Repeat.

## Sizing Rubric (expected code change, added + deleted)

| Tier   | Lines  | 예시                              |
|--------|--------|-----------------------------------|
| tiny   | ~5     | Config 값, 상수, 문자열 리터럴      |
| small  | ~20    | 한 함수, 한 파일, 로컬 리팩터       |
| medium | ~50    | 여러 파일, 인터페이스 변경           |
| large  | ~100   | 횡단 관심사, 스키마 마이그레이션      |
| xlarge | ~500   | 아키텍처 전환, 프레임워크 교체        |

## When to Use

Use when:
- trace.md with unfinished scenarios exists
- Ready for autonomous implementation execution
- User wants minimal interruption until work is done

Do NOT use when:
- No trace.md exists (use `stv:new-task` first)
- User asked a single specific question
- Exploring/researching without implementation

## Workflow Phases

```
Phase A: Task Selection
    ↓
Phase B: STV Work Execution (→ stv:work)
    ↓
Phase C: Context Check
    ↓
Phase D: Loop Decision
    ↓ (loop back to A or stop)
```

### Phase A: Task Selection (~5min)

**Goal**: Select unfinished scenarios from trace.md and bundle for execution.

1. **Scan trace files**
   - Glob for `docs/*/trace.md` across the project
   - Read each trace.md's Implementation Status table
   - Collect scenarios where Status != "Complete"

2. **Prioritize scenarios**
   - Respect dependency order (earlier scenarios first)
   - Group by feature if multiple features have ready scenarios
   - Estimate combined size tier

3. **Bundle scenarios** (target: xlarge)
   - Bundle related scenarios into work chunks
   - If total < large: include more related scenarios
   - If total > xlarge: split into multiple bundles, execute first bundle
   - Cap at xlarge per bundle

4. **Present bundle to user**

```markdown
## Work Bundle

### Target: {feature-name}
Trace: docs/{feature}/trace.md

### Scenarios to implement:
| # | Scenario | Size | Dependencies |
|---|----------|------|-------------|
| {n} | {title} | {tier} | {deps or "none"} |
| ... | ... | ... | ... |

Estimated total: {tier}

Proceed? (or adjust bundle)
```

### Phase B: STV Work Execution

**Goal**: Implement the bundled scenarios using stv:work.

```
Skill(skill="stv:work") 발동
```

- stv:work가 시나리오별 GREEN + Trace Verify 수행
- 완료 후 trace.md의 Implementation Status 업데이트

**After stv:work completes:**

1. **Quality Gates**
   ```bash
   # Run project-specific commands
   npm test    # or bun test / pytest / dotnet test
   npm run build   # if applicable
   npm run lint    # if applicable
   ```

2. **Commit & Push**
   - Commit with detailed message referencing trace scenarios
   - Push to remote

### Phase C: Context Check (~1min)

**Goal**: Prevent context overflow.

```
IF context > 70%:
  1. Save critical state (current trace progress)
  2. Use /compact or context compression
  3. OR end session gracefully with resume point

ELSE:
  Continue to Phase D
```

### Phase D: Loop Decision (~1min)

**Goal**: Decide whether to continue autonomous work.

**Continue to Phase A if:**
- More unfinished scenarios exist in trace.md
- All requirements understood
- No blockers
- Context budget OK

**Stop and report to user if:**
- All scenarios complete (feature done)
- Requirements unclear or ambiguous
- Architectural decision needed (switching cost >= medium, can't use generic pattern)
- Context near limit
- Major milestone reached

**Report format when stopping:**

```markdown
## Work Session Report

### Completed
- {N}/{total} scenarios GREEN + Verified
- Feature: {feature-name}

### Remaining
- {M} scenarios still pending
- Next: Scenario {n} — {title}

### Quality
- Tests: {pass}/{total} passing
- Build: clean / {N} errors
- Lint: clean / {N} warnings

### Next Step
→ Run `stv:do-work` to continue
→ Or `stv:work docs/{feature}/trace.md` for specific trace
```

## Mid-Implementation Decision Thresholds

During execution, unexpected architectural decisions may arise.

**기본 임계값**: `auto_decide <= small(~20줄)`, `must_ask >= medium(~50줄)`

```
for each unexpected decision:
  if switching_cost <= small:
    → 자율 결정 + Auto-Decision Log 기록
    → small인 경우 결과를 유저에게 보고
  elif switching_cost >= medium:
    → 제네릭 아키텍처로 비용 줄일 수 있는지 확인
      → 줄일 수 있으면: 자율 결정 + 로그
      → 못 줄이면: Phase D로 이동하여 유저에게 질문
```

**Auto-Decision Log 포맷:**

```markdown
### Auto-Decision Log: [결정 제목]
- **결정**: [선택한 옵션]
- **switching cost**: [tier] (~Y lines)
- **판단 근거**: [상세 이유]
- **제네릭 패턴 적용**: [있으면 패턴명 / 없으면 "불필요"]
- **변경 시 영향**: [나중에 바꾸려면 어디를 고치면 되는지]
```

## Integration with Other Skills

**INVOKES:**
- `stv:work` — Phase B에서 시나리오별 구현 실행

**CALLED BY:**
- `stv:what-we-have-to-work` — 번들 선택 후 실행
- `stv:what-to-work` — 라우팅 후 실행

**PRECONDITIONS:**
- `docs/{feature}/trace.md` 존재 필수
- trace.md에 미완성 시나리오 존재 필수
- 없으면 → `stv:new-task` 안내

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| trace 없이 실행 시도 | docs/*/trace.md 확인 먼저 |
| 번들 크기 무시 | target xlarge, cap at xlarge |
| Quality gate 건너뛰기 | test/build/lint 모두 실행 |
| context overflow | Phase C에서 70% 초과시 대응 |
| 사소한 결정에 멈춤 | switching cost <= small이면 자율 결정 |

## NEVER

- trace.md 없이 구현 시작
- Quality gate 건너뛰기
- context 관리 무시
- 자율 결정에 로그 안 남기기
