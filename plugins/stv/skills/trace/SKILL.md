---
name: trace
description: "STV Phase 2: spec.md -> vertical trace + RED contract tests. Traces every API scenario through all layers with parameters and side-effects."
---

# STV Trace — Vertical Trace + Contract Tests

> STV Phase 2: spec.md → `docs/{feature}/trace.md` + RED contract tests
> 시나리오별로 API entry → Handler → Service → DB를 파라미터 단위로 추적하고,
> trace에서 contract test를 파생시킨다.

---

## Decision Gate (MANDATORY)

**Read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` and apply it to every decision in this workflow.**

---

## Phase 1: Spec Loading

1. **Spec 읽기**: 지정된 경로의 spec.md를 읽는다
   - spec이 없으면 → 유저에게 `stv:spec` 먼저 실행하라고 안내
2. **코드베이스 탐색** (Agent:Explore):
   - spec의 API endpoints에 해당하는 기존 코드 위치 파악
   - 기존 유사 기능의 구현 패턴 분석
   - DB entity, DTO, enum 등 관련 타입 매핑
3. **시나리오 목록 추출**: spec의 User Stories + Acceptance Criteria에서 trace할 시나리오 목록 도출

## Phase 2: Trace Interview

각 시나리오의 구체적 흐름을 확정하기 위해 유저 인터뷰.
**Decision Gate 적용: 기존 패턴 답습은 자율 판단, 새로운 비즈니스 로직은 질문.**

### 질문 대상 (medium+ switching cost만)

- DB에 저장되는 구체적 필드값과 변환 규칙
- 에러 경로의 비즈니스 규칙 (어떤 조건에서 어떤 에러?)
- 여러 서비스 간 호출 순서와 트랜잭션 경계
- side-effect 간 의존성 (A가 실패하면 B는?)

### 자율 판단 대상 (small 이하)

- 기존 패턴과 동일한 validation 흐름
- 기존 패턴과 동일한 auth check
- 기존 패턴과 동일한 에러 매핑 (ArgumentException→BadRequest 등)
- 파라미터 이름, 응답 형태 등 컨벤션

## Phase 3: Vertical Trace 작성

시나리오별로 ASCII 다이어그램 + 텍스트로 전체 콜스택을 문서화.

### Trace 작성 규칙

각 시나리오에 대해 아래 형식으로 작성:

```
 {Caller}
       │
       │  {HTTP Method} {Path}
       │  Headers: { ... }
       │  Body: {RequestType} { ... }
       ▼
 ┌─────────────────────────────────────────────────────┐
 │  {ClassName}.{MethodName}(                          │
 │      param1: type, param2: type)                    │
 │  {FilePath}:{LineNumber}                            │
 │                                                     │
 │  Step 1: {Description}                              │
 │    {구체적 로직 — 파라미터 변환, 조건 분기}            │
 │                                                     │
 │  Step 2: {Description}                              │
 │    {DB 호출, 외부 서비스 호출 등}                     │
 │                                                     │
 │  Error paths:                                       │
 │    {condition} → {ErrorType} ({HTTP status})        │
 └──────────────────────┬──────────────────────────────┘
                        │
                        ▼
 ┌─────────────────────────────────────────────────────┐
 │  {NextLayer — Service/DB}                           │
 │                                                     │
 │  DB Side-Effects:                                   │
 │    INSERT {table} (field1, field2, ...)             │
 │    UPDATE {table} SET field1 = ... WHERE ...        │
 │                                                     │
 │  Invariants:                                        │
 │    - {검증해야 할 불변 조건}                          │
 └──────────────────────┬──────────────────────────────┘
                        │
                        ▼
 ┌─────────────────────────────────────────────────────┐
 │  Response: {ResponseType} {                         │
 │    Result: {code},                                  │
 │    {payload fields}                                 │
 │  }                                                  │
 └─────────────────────────────────────────────────────┘
```

### 각 trace 박스에 반드시 포함할 내용

1. **클래스.메서드(파라미터)** — 실제 코드 위치 (파일:라인)
2. **파라미터 변환** — 입력이 어떻게 변환되어 다음 레이어로 전달되는지
3. **DB Side-Effect** — INSERT/UPDATE/DELETE 대상 테이블 + 필드
4. **Error Paths** — 어떤 조건에서 어떤 에러 (HTTP status 포함)
5. **Invariants** — 이 단계에서 보장되어야 할 불변 조건

## Phase 4: Contract Tests (RED)

trace 문서의 각 시나리오에서 테스트를 파생한다.

### Test 카테고리

| Category | Trace에서 파생되는 것 | Test 형태 |
|----------|---------------------|----------|
| **Happy Path** | 정상 흐름의 Request→Response | Input → Expected Output 검증 |
| **Sad Path** | Error Paths | Invalid input → Expected Error 검증 |
| **Side-Effect** | DB Side-Effects | 호출 후 DB 상태 변화 검증 |
| **Contract** | 파라미터 변환 규칙 | 입력 A → 변환 결과 B 검증 |
| **Invariant** | Invariants | 불변 조건 위반 시 에러 검증 |

### Test 작성 규칙

1. **trace의 시나리오 이름을 test class/method 이름에 반영**
   - Trace: "Stage 1 — 루트 파트너 생성" → Test: `RootPartnerCreate_HappyPath`
2. **각 test에 trace 참조 주석**
   ```
   // Trace: Stage 1, Step 2 — CreatePartnerAsync validation
   ```
3. **RED 상태 확인** — 모든 테스트가 실패하는 것을 확인
4. **side-effect test는 DB 상태를 직접 검증**

## Phase 5: Output

### Output Files

1. **`docs/{feature}/trace.md`** — Vertical Trace 문서
2. **테스트 파일** — 프로젝트 테스트 디렉토리에 RED contract tests

### trace.md 구조

```markdown
# {Feature Name} — Vertical Trace

> STV Trace | Created: {date}
> Spec: docs/{feature}/spec.md

## 목차
1. [Scenario 1 — {title}](#scenario-1)
2. [Scenario 2 — {title}](#scenario-2)
...

---

## Scenario 1 — {title}

### 1.1 ASCII Diagram
{콜스택 다이어그램}

### 1.2 DB Entity
{관련 entity 구조}

### 1.3 Error Paths
| Condition | Error | HTTP Status |
|-----------|-------|-------------|
| ... | ... | ... |

### 1.4 Contract Tests (RED)
| Test Name | Category | Trace Reference |
|-----------|----------|-----------------|
| {test method} | Happy Path | Scenario 1, Step 3 |
| {test method} | Sad Path | Scenario 1, Error Path 1 |
| {test method} | Side-Effect | Scenario 1, DB INSERT |

---

## Auto-Decisions
{Decision Gate에서 자율 판단한 내용}

## Implementation Status
| Scenario | Trace | Tests (RED) | Status |
|----------|-------|-------------|--------|
| 1. {title} | done | RED | Ready for stv:work |
| 2. {title} | done | RED | Ready for stv:work |

## Next Step
→ `stv:work` 로 구현 + Trace Verify 진행
```

## Completion

1. trace.md 저장
2. RED contract tests 작성 및 **실행하여 모두 FAIL 확인**
3. 유저에게 trace 요약 + RED test 결과 + 다음 단계 안내
4. **다음 스킬 안내**: `Skill(skill="stv:work")` 또는 유저에게 `stv:work docs/{feature}/trace.md` 사용 안내
