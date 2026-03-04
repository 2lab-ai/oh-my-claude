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
  2. trace의 7 섹션을 기준으로 코드 구현
     - Layer Flow의 파라미터 변환 규칙 그대로
     - Side Effects 그대로
     - Error Paths 그대로
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

### Test Portfolio Strategy

```
┌─────────────────────────────────────────────┐
│            1차 게이트 (빠르고 안정적)          │
│                                             │
│  Trace-Driven Contract/Component Tests      │
│  - Happy path, Sad path, Side-effect,       │
│    Contract(파라미터 변환) 테스트             │
│  - 실행 시간: 초~분 단위                     │
│  - 안정성: 높음 (외부 의존성 최소)            │
│  - PR merge 차단 기준                        │
│                                             │
├─────────────────────────────────────────────┤
│            2차 게이트 (최소 개수)             │
│                                             │
│  E2E Tests                                  │
│  - 배포 환경에서만 확인 가능한 것만 테스트     │
│    (네트워크, 권한, 배포 설정 등)             │
│  - 실행 시간: 분~십분 단위                   │
│  - 안정성: 낮음 (flaky 가능)                 │
│  - 배포 전 점검용, merge 차단에는 사용 안 함  │
│                                             │
└─────────────────────────────────────────────┘
```

Contract Test가 1차 게이트인 이유: E2E 테스트는 느리고, 깨지기 쉽고, flaky하며, 전용 환경이 필요하다. Contract Test는 빠르고 안정적이며 로컬에서 실행 가능하다.

## Phase 3: Trace Conformance Verify

모든 시나리오가 GREEN이 된 후, trace 문서와 실제 구현의 일치를 대조 검증.

### Trace Conformance Checklist

trace.md의 각 시나리오에 대해 7-section 기준으로 검증:

```markdown
### Scenario {N} Verify: {title}

**Section 1 — API Entry:**
- [ ] HTTP method + route 일치
- [ ] 인증/인가 방식 일치

**Section 2 — Input:**
- [ ] Request 페이로드 필드 일치
- [ ] 검증 규칙 구현됨

**Section 3 — Layer Flow:**
- [ ] Controller: Request → Command 변환 규칙 일치
- [ ] Service: Command → Entity 변환 규칙 일치
  - 도메인 판단 로직이 trace와 일치
  - 파생 값(ID 생성, 타임스탬프 등)이 trace 규칙대로
- [ ] Repository/DB: Entity → Row 매핑 일치
  - 트랜잭션 경계가 trace대로
  - FK, UNIQUE 등 제약조건이 스키마에 존재
- [ ] 파라미터 변환 화살표 관통 검증
  - Request.X → Command.Y → Entity.Z → table.col 체인 일치

**Section 4 — Side Effects:**
- [ ] trace에 명시된 모든 INSERT/UPDATE/DELETE가 코드에 존재
- [ ] trace에 없는 예상치 못한 DB 변경 없음
- [ ] 이벤트 발행/캐시 변경이 trace와 일치

**Section 5 — Error Paths:**
- [ ] 각 에러 조건 → 예외 타입 일치
- [ ] 예외 → HTTP status 매핑 일치
- [ ] 에러 시 DB 롤백/무변경 보장됨

**Section 6 — Output:**
- [ ] 성공 상태 코드 일치
- [ ] Response DTO 필드 일치

**Section 7 — Observability (해당 시):**
- [ ] 로그 필드 포함 여부
- [ ] 스팬 네이밍 일치
```

### Mismatch Handling Protocol

불일치 발견 시 다음 프로토콜을 따른다:

```
불일치 발견 →
  1. trace가 잘못된 경우 (구현이 더 나은 경우):
     → trace.md 수정 → 관련 test 수정 → 재검증
  2. 코드가 잘못된 경우 (trace가 맞는 경우):
     → 코드 수정 → test 재실행 → 재검증
  3. 판단 어려운 경우:
     → 유저에게 질문

★ 어느 쪽이든 trace와 코드는 항상 동기화되어야 한다.
★ 수정 이력은 trace.md의 Trace Deviations 섹션에 기록한다.
```

### Verify Loop

```
while (unverified scenarios exist):
  1. 다음 미검증 시나리오 선택
  2. 코드 읽고 trace와 7-section 기준 대조
  3. 불일치 → Mismatch Handling Protocol 적용
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

### Phase 3 Checklist

- [ ] 모든 Contract Test가 GREEN
- [ ] Trace Conformance 검증 완료 (불일치 항목 0개)
- [ ] trace 문서와 코드가 동기화됨
- [ ] 불일치로 인한 trace 또는 코드 수정이 있었다면, 수정 이력이 Trace Deviations에 기록됨

## NEVER

- trace에 없는 기능을 "개선"으로 추가
- 테스트를 수정해서 GREEN으로 만들기 (구현을 수정해야 함)
- verify 없이 "완료" 선언
- 불일치를 무시하고 넘어가기
- trace와 코드가 괴리된 채 방치하기
