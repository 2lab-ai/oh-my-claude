---
name: work
description: "STV Phase 3: Implementation (GREEN) + Trace Verify loop. Implements code to pass contract tests, then verifies implementation matches trace document."
---

# STV Work — Implementation + Trace Verify Loop

> STV Phase 3: trace.md → GREEN implementation + Trace Verify
> Contract tests를 통과시키는 코드를 작성하고,
> 구현이 trace 문서와 일치하는지 대조 검증한다.

---

## Phase 1: Context Loading

1. **Trace 읽기**: 지정된 경로의 trace.md를 읽는다
   - trace가 없으면 → 유저에게 `stv:trace` 먼저 실행하라고 안내
2. **Spec 읽기**: trace.md에서 참조하는 spec.md를 읽는다
3. **RED Tests 확인**: contract test 파일을 읽고, 현재 상태 확인
   - 모든 테스트가 RED(FAIL)인지 확인
   - RED가 아닌 테스트가 있으면 경고
4. **구현 순서 결정**: trace의 시나리오 순서 = 구현 순서
   - 의존성이 있으면 의존 대상 먼저

## Phase 2: Implementation Loop (GREEN)

**각 시나리오별로 반복:**

```
for each scenario in trace.md:
  1. trace의 해당 시나리오 다시 읽기
  2. trace의 각 박스(레이어)를 코드로 구현
     - 파라미터 변환 규칙 그대로
     - DB side-effect 그대로
     - Error path 그대로
  3. 해당 시나리오의 contract tests 실행
  4. if GREEN → 다음 시나리오
  5. if RED → 수정 후 재실행 (trace 기준으로 수정)
```

### 구현 규칙

1. **Trace가 진실의 원천(Source of Truth)**
   - trace에 "Step 2: ValidatePartner(entity)" 라고 되어있으면, 정확히 그 이름/시그니처로 구현
   - trace에 명시되지 않은 동작을 추가하지 않는다
   - trace와 다르게 구현해야 할 이유가 있으면 → trace 먼저 수정

2. **한 시나리오씩 GREEN**
   - 전체를 한 번에 구현하지 않는다
   - 시나리오 1 GREEN → 시나리오 2 GREEN → ...
   - 이전 시나리오가 깨지면 즉시 수정

3. **Side-Effect 정확성**
   - DB INSERT/UPDATE는 trace에 명시된 필드만
   - trace에 없는 필드를 저장하면 → trace 수정 or 코드 수정

## Phase 3: Trace Verify

모든 시나리오가 GREEN이 된 후, trace 문서와 실제 구현의 일치를 대조 검증.

### Verify Checklist

trace.md의 각 시나리오에 대해:

```markdown
### Scenario {N} Verify: {title}

**Call Path:**
- [ ] API entry point: method + route 일치
- [ ] Handler: class.method + 파일위치 일치
- [ ] Service: class.method + 파일위치 일치
- [ ] DB: table + operation 일치

**Parameters:**
- [ ] Request DTO 필드 일치
- [ ] 레이어 간 파라미터 변환 규칙 일치
- [ ] Response DTO 필드 일치

**Side-Effects:**
- [ ] DB INSERT: 대상 테이블 + 필드 일치
- [ ] DB UPDATE: 대상 테이블 + 조건 + 필드 일치
- [ ] 기타 side-effect (캐시, 이벤트 등) 일치

**Error Paths:**
- [ ] 각 에러 조건 → 예외 타입 일치
- [ ] 예외 → HTTP status 매핑 일치

**Invariants:**
- [ ] 각 불변 조건 코드에서 강제됨 확인
```

### Verify 방법

1. **Agent:Explore로 실제 코드 읽기**
   - trace 박스에 명시된 파일:라인을 실제로 읽어서 대조
2. **불일치 발견 시**:
   - 구현이 더 나은 경우 → trace.md 업데이트
   - trace가 맞는 경우 → 코드 수정
   - 판단 어려운 경우 → 유저에게 질문
3. **trace.md에 마킹**
   - verify 통과한 시나리오에 상태 표시

### Verify Loop

```
while (unverified scenarios exist):
  1. 다음 미검증 시나리오 선택
  2. 코드 읽고 trace와 대조
  3. 불일치 → 수정 (trace or code)
  4. 수정 후 관련 tests 재실행
  5. GREEN + trace 일치 → Verified 마킹
```

## Phase 4: Completion Report

모든 시나리오가 GREEN + Verified 후:

### trace.md 업데이트

```markdown
## Implementation Status
| Scenario | Trace | Tests | Verify | Status |
|----------|-------|-------|--------|--------|
| 1. {title} | done | GREEN | Verified | Complete |
| 2. {title} | done | GREEN | Verified | Complete |

## Trace Deviations
{구현 중 trace에서 벗어난 부분과 그 이유. 없으면 "None"}

## Verified At
{date} — All {N} scenarios GREEN + Verified
```

### 유저에게 보고

```
## STV Work Complete: {feature}

{N}/{N} scenarios GREEN
{N}/{N} scenarios Trace Verified
{N} trace deviations (documented in trace.md)

### Test Results
- Total: {N} tests
- Passed: {N}
- Failed: 0

### Files Modified
{modified file list}

### Next Steps
- [ ] Code review
- [ ] Commit & PR
```

## NEVER

- trace에 없는 기능을 "개선"으로 추가
- 테스트를 수정해서 GREEN으로 만들기 (구현을 수정해야 함)
- verify 없이 "완료" 선언
- 불일치를 무시하고 넘어가기
