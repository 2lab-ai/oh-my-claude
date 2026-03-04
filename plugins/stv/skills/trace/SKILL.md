---
name: trace
description: "STV Phase 2: spec.md -> vertical trace + RED contract tests. Traces every API scenario through all layers with 7-section format and parameter transformation arrows."
---

# STV Trace — Vertical Trace + Contract Tests

> STV Phase 2: spec.md → `docs/{feature}/trace.md` + RED contract tests
> 시나리오별로 API entry → Handler → Service → DB를 파라미터 단위로 추적하고,
> trace에서 contract test를 파생시킨다.

---

## Decision Gate (MANDATORY)

**Read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` and apply it to every decision in this workflow.**

**이 게이트를 모든 결정에 적용한다. switching cost < small이면 자율 판단, == small이면 자율 결정+보고, >= medium이면 유저에게 질문.**

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
**Decision Gate 적용: tiny/small은 자율 판단, medium+ 만 질문.**

### 질문 대상 (medium+ switching cost)

- DB에 저장되는 구체적 필드값과 변환 규칙
- 에러 경로의 비즈니스 규칙 (어떤 조건에서 어떤 에러?)
- 여러 서비스 간 호출 순서와 트랜잭션 경계
- side-effect 간 의존성 (A가 실패하면 B는?)

### 자율 판단 대상 (small 이하)

- 기존 패턴과 동일한 validation 흐름
- 기존 패턴과 동일한 auth check
- 기존 패턴과 동일한 에러 매핑 (ArgumentException→BadRequest 등)
- 파라미터 이름, 응답 형태 등 컨벤션

### Phase 2 Checklist

- [ ] 모든 시나리오에 대해 Vertical Trace 문서가 작성됨
- [ ] 각 trace에 7개 섹션(API Entry, Input, Layer Flow, Side Effects, Error Paths, Output, Observability)이 모두 포함됨
- [ ] Layer Flow에 파라미터 변환 화살표가 명시됨 (Request.X → Command.Y → Entity.Z → table.column)
- [ ] 4가지 카테고리의 Contract Test가 모두 작성됨
- [ ] 모든 Contract Test가 RED 상태로 실행됨 (컴파일은 되지만 실패)
- [ ] 마이크로서비스인 경우, 서비스 간 CDC가 별도 정의됨

## Phase 3: Vertical Trace 작성

시나리오별로 **7-section Vertical Trace Minimum Field Spec** 형식으로 전체 콜스택을 문서화.

### 7-Section Vertical Trace 형식

**형식은 자유(Markdown, YAML, JSON 등)지만, 다음 필드가 하나라도 빠지면 빈틈을 이용해 버그를 숨길 수 있다. 반드시 모든 섹션을 포함할 것.**

```markdown
## Trace: [시나리오 이름]

### 1. API Entry
- HTTP Method: [GET/POST/PUT/DELETE/PATCH]
- Path: [/api/resource]
- 인증/인가: [필요한 권한 또는 인증 방식]

### 2. Input (요청)
- 요청 페이로드:
  ```json
  {
    "field1": "type (required/optional) - 설명",
    "field2": "type (required/optional) - 설명"
  }
  ```
- 검증 규칙:
  - field1: [최소/최대 길이, 허용 문자, 포맷 등]
  - field2: [범위, enum 값, 정규식 등]

### 3. Layer Flow (레이어별 흐름) ★핵심★

#### 3a. Controller/Handler
- 추출되는 파라미터: [Request → Command/DTO 변환]
- 파생 값: [자동 생성 ID, 타임스탬프 등]
- 변환 규칙:
  - Request.FieldA → Command.PropertyA (변환 로직 설명)
  - Request.FieldB → Command.PropertyB (변환 로직 설명)

#### 3b. Service
- 도메인 판단: [비즈니스 규칙, 조건 분기]
- 다른 서비스 호출: [동기/비동기, 호출 대상, 파라미터]
- 변환 규칙:
  - Command.PropertyA → Entity.AttributeA (변환 로직 설명)
  - 계산/파생: [Entity.ComputedField = f(PropertyA, PropertyB)]

#### 3c. Repository/DB
- 트랜잭션 경계: [시작점과 종료점]
- 기록되는 엔티티/로우:
  - 테이블: [테이블명]
  - 컬럼 매핑: Entity.AttributeA → column_a
  - ID 생성 규칙: [UUID v4, auto-increment, ULID 등]
  - 제약조건: [UNIQUE, FK, CHECK 등]

### 4. Side Effects (사이드이펙트)
- DB 변경:
  - INSERT: [테이블, 키 컬럼, 값 원천]
  - UPDATE: [테이블, WHERE 조건, 변경 컬럼]
  - DELETE: [테이블, WHERE 조건] (해당 시)
- 이벤트/메시지 발행: [토픽, 페이로드 스키마]
- 캐시 변경: [캐시 키, TTL, 무효화 규칙]

### 5. Error Paths (에러 경로)
- 검증 실패: [어떤 필드가 어떤 조건을 위반하면 → HTTP 상태코드, 에러 응답 형태]
- 인증/인가 실패: [→ 401/403, 응답]
- 충돌/멱등성: [중복 요청 시 → 409 또는 멱등 처리, DB 상태 변화 없음 확인]
- 하류 서비스 실패: [재시도 정책, 보상 트랜잭션, 서킷브레이커]

### 6. Output (응답)
- 성공 상태 코드: [200/201/204]
- 응답 스키마:
  ```json
  {
    "id": "생성된 ID",
    "field1": "원본 또는 변환된 값",
    "createdAt": "ISO 8601"
  }
  ```

### 7. Observability Hooks (관측성 훅) [선택]
- 로그 필드: [traceId, userId, action 등]
- 트레이스/스팬 네이밍: [span 이름 컨벤션]
- 메트릭: [카운터, 히스토그램 등]
```

### 파라미터 변환 화살표 (MANDATORY)

**모든 Layer Flow에서 파라미터 변환 화살표를 반드시 명시한다:**

```
Request.X → Command.Y → Entity.Z → table.col
```

이 화살표가 빠지면 파라미터 변환 과정에서 발생하는 버그를 놓칠 수 있다.
"구현할 것이다" 같은 미래형 표현 금지. "~한다" "~된다" 같은 현재형/확정형으로 기술한다.

### 각 trace에 반드시 포함할 내용

1. **API Entry** — HTTP method, path, 인증/인가
2. **Input** — 요청 페이로드 + 검증 규칙
3. **Layer Flow** — 파라미터 변환 화살표 포함, 레이어별 흐름
4. **Side Effects** — DB INSERT/UPDATE/DELETE, 이벤트, 캐시
5. **Error Paths** — 조건 → 에러 → HTTP status
6. **Output** — 성공 응답 스키마
7. **Observability** — 로그, 트레이스, 메트릭 (선택)

## Phase 4: Contract Tests (RED)

trace 문서의 각 시나리오에서 테스트를 파생한다.

### Test 카테고리

| Category | Trace에서 파생되는 것 | Test 형태 |
|----------|---------------------|----------|
| **Happy Path** | 정상 흐름의 Request→Response + Side Effects | Input → Expected Output + DB 상태 변화 검증 |
| **Sad Path** | Error Paths (검증 실패, 인증 실패, 충돌 등) | Invalid input → Expected Error + DB 무변경 검증 |
| **Side-Effect** | Side Effects (DB, 이벤트, 캐시) | 호출 후 DB/이벤트/캐시 상태 변화 독립 검증 |
| **Contract** | Layer Flow의 파라미터 변환 규칙 | 입력 A → 변환 결과 B 관통 검증 (Request→DB까지) |

### Test 작성 규칙

1. **trace의 시나리오 이름을 test class/method 이름에 반영**
   - Trace: "Stage 1 — 루트 파트너 생성" → Test: `RootPartnerCreate_HappyPath`
2. **각 test에 trace 참조 주석**
   ```
   // Trace: Stage 1, Section 3 — Layer Flow, Controller→Service 변환
   ```
3. **RED 상태 확인** — 모든 테스트가 실패하는 것을 확인
4. **Contract 테스트는 파라미터 변환 화살표를 DB까지 관통 검증**
   ```
   // Request.contactEmail("UPPER@CASE.COM") → Command.ContactEmail → Entity.Email → partner.email
   // 변환 규칙: 소문자 변환
   ```

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

### 1. API Entry
- HTTP Method: {method}
- Path: {path}
- 인증/인가: {auth}

### 2. Input
- 요청 페이로드:
  {payload schema}
- 검증 규칙:
  {validation rules}

### 3. Layer Flow

#### 3a. Controller/Handler
- 변환: Request.X → Command.Y
- {class.method, file:line}

#### 3b. Service
- 도메인 판단: {business rules}
- 변환: Command.Y → Entity.Z
- 파생: {computed fields}

#### 3c. Repository/DB
- 트랜잭션: {boundary}
- 매핑: Entity.Z → table.column

### 4. Side Effects
- DB INSERT: {table} ({columns})
- {other side effects}

### 5. Error Paths
| Condition | Error | HTTP Status |
|-----------|-------|-------------|
| ... | ... | ... |

### 6. Output
- 성공: {status code}
- 응답: {response schema}

### 7. Observability [선택]
- 로그: {log fields}
- 스팬: {span naming}

### Contract Tests (RED)
| Test Name | Category | Trace Reference |
|-----------|----------|-----------------|
| {test method} | Happy Path | Scenario 1, Section 3 |
| {test method} | Sad Path | Scenario 1, Section 5, Error 1 |
| {test method} | Side-Effect | Scenario 1, Section 4 |
| {test method} | Contract | Scenario 1, Section 3, Request.X→table.col |

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
