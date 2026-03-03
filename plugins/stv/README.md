# STV — Spec-Trace-Verify

**Traced Development: AI 시대의 스펙 기반 개발 방법론**

```
Spec → Trace → Verify
 왜?     청사진    대조
```

---

## Traced Development란?

Traced Development는 **구현 전에 전 레이어를 관통하는 Vertical Trace를 작성하고, trace에서 Contract Test를 파생시키고, 구현 후 trace와 대조 검증하는** 스펙 기반 개발 방법론이다.

Spec-Driven Development를 베이스로, Vertical Trace와 RED/GREEN TDD를 결합한다.

### 핵심 원칙

> **Trace가 진실의 원천(Source of Truth)이다.**
>
> 코드는 trace에 명시된 대로 동작해야 한다. trace에 없는 동작을 추가하지 않는다.
> trace와 다르게 구현해야 할 이유가 있으면, trace를 먼저 수정한다.

---

## 왜 필요한가? — AI Slop 문제

AI 코딩 에이전트의 구조적 문제:

- AI는 **완전한 솔루션을 한 번에** 생성하려 한다
- 개별 레이어를 격리해서 만들고, **임계 경로가 실제로 동작하는지 검증하지 않는다**
- 결과: 거대한 코드 덩어리가 재작업을 필요로 하는 **slop**
- LinearB 데이터: **AI 생성 PR의 67.3%가 reject** (수동 코드는 15.6%)

### Vertical Trace가 해결하는 것

```
AI 없이:
  "파트너 생성 API 만들어줘" → 서피스만 대충 구현 → "완료!"
  실제로는 DB에 저장 안 됨, validation 빠짐, auth 없음

Traced Development:
  "파트너 생성 API 만들어줘"
  → Spec: 무엇을, 왜
  → Trace: Controller→Handler→Service→DB 파라미터 단위 추적
  → Contract Test: trace의 각 단계를 강제하는 테스트
  → 구현: 테스트 통과 + trace 대조
  → 건너뛸 수 없다
```

---

## 이론적 배경

STV는 여러 검증된 방법론의 교차점에 있다:

| 방법론 | 핵심 아이디어 | STV에서의 역할 |
|--------|-------------|---------------|
| **Tracer Bullet Dev** (Pragmatic Programmer) | 첫날부터 전 레이어 관통 thin slice | Vertical Trace 사고방식 |
| **Specification by Example** (Gojko Adzic) | 구체적 예시 = 실행 가능한 스펙 | Trace = 실행 가능한 청사진 |
| **ATDD** | Acceptance test가 개발을 드라이브 | Contract Tests (RED) |
| **Design by Contract** (Bertrand Meyer) | Pre/Post condition 강제 | Trace Invariants |
| **Vertical Slice Architecture** (Jimmy Bogard) | 기능 단위로 전 레이어 관통 | 시나리오별 수직 분석 |
| **TDD** (Kent Beck) | RED → GREEN → REFACTOR | Contract Tests → Implementation → Verify |

**STV 고유의 기여:**
- 코드 작성 전 콜스택 수준 trace 문서화 (어디에도 없는 프랙티스)
- Trace에서 contract test 직접 파생
- 구현 후 trace-code 대조 검증 루프
- AI agent의 surface-level 구현 구조적 방지

---

## 3-Phase 구조

```
┌───────────────────────────────────────────────────────┐
│  Phase 1: SPEC                                        │
│  "무엇을, 어떻게"                                      │
│                                                       │
│  ① PRD Interview — 유저 스토리, 수용 기준, 스코프       │
│  ② Architecture Interview — 레이어, DB, API, 인증      │
│                                                       │
│  Output: docs/{feature}/spec.md                       │
└───────────────────────┬───────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────┐
│  Phase 2: TRACE                                       │
│  "청사진 + 계약"                                       │
│                                                       │
│  ① Vertical Trace — 시나리오별 콜스택 문서화            │
│    API → Handler → Service → DB (파라미터+부수효과)     │
│  ② Contract Tests (RED) — trace에서 테스트 파생        │
│    Happy path / Sad path / Side-effect 검증           │
│                                                       │
│  Output: docs/{feature}/trace.md + *Tests (all RED)   │
└───────────────────────┬───────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────┐
│  Phase 3: VERIFY                                      │
│  "구현 + 대조"                                         │
│                                                       │
│  ① Implementation (GREEN) — 테스트 통과시키는 코드     │
│  ② Trace Verify — trace 문서 ↔ 구현 대조               │
│  ③ Loop: 불일치 시 → trace 수정 or 코드 수정           │
│                                                       │
│  Output: src/**/* (all GREEN) + trace.md (Verified)   │
└───────────────────────────────────────────────────────┘
```

---

## Vertical Trace란?

시나리오별로 API 요청이 시스템의 전 레이어를 관통하는 과정을 **함수 호출 단위**로 추적한 문서.

### Trace 박스 형식

```
 {Caller}
       │
       │  {HTTP Method} {Path}
       │  Body: {RequestType} { field: value, ... }
       ▼
 ┌─────────────────────────────────────────────────────┐
 │  {ClassName}.{MethodName}(param1, param2)            │
 │  {FilePath}:{LineNumber}                            │
 │                                                     │
 │  Step 1: Validation                                 │
 │    if (field == null) → BadRequest                  │
 │                                                     │
 │  Step 2: Transform                                  │
 │    var entity = request.Adapt<Entity>();             │
 │                                                     │
 │  Step 3: DB Call                                    │
 │    await _service.CreateAsync(entity);              │
 │                                                     │
 │  Error Paths:                                       │
 │    duplicate → Conflict (409)                       │
 │    not found → NotFound (404)                       │
 └──────────────────────┬──────────────────────────────┘
                        │
                        ▼
 ┌─────────────────────────────────────────────────────┐
 │  {ServiceLayer}                                     │
 │                                                     │
 │  DB Side-Effects:                                   │
 │    INSERT {table} (col1, col2, col3)                │
 │                                                     │
 │  Invariants:                                        │
 │    - col1 is UNIQUE                                 │
 │    - parent must exist if set                       │
 └──────────────────────┬──────────────────────────────┘
                        │
                        ▼
 ┌─────────────────────────────────────────────────────┐
 │  Response: {ResponseType} {                         │
 │    Result: 200,                                     │
 │    Entity: { No: 1, Field: "value" }                │
 │  }                                                  │
 └─────────────────────────────────────────────────────┘
```

### 각 박스에 반드시 포함

| 항목 | 설명 |
|------|------|
| **클래스.메서드(파라미터)** | 실제 코드 위치 (파일:라인) |
| **파라미터 변환** | 입력 → 다음 레이어 전달 시 변환 규칙 |
| **DB Side-Effect** | INSERT/UPDATE/DELETE 대상 테이블 + 필드 |
| **Error Paths** | 조건 → 예외 → HTTP status |
| **Invariants** | 이 단계에서 보장되어야 할 불변 조건 |

---

## Contract Tests

Trace 문서에서 직접 파생되는 테스트. **Trace = 계약서, Test = 계약 이행 검증.**

### Test 카테고리

| Category | Trace에서 파생 | 검증 대상 |
|----------|--------------|----------|
| **Happy Path** | 정상 흐름 Request→Response | 올바른 입력 → 기대 출력 |
| **Sad Path** | Error Paths | 잘못된 입력 → 기대 에러 |
| **Side-Effect** | DB Side-Effects | 호출 후 DB 상태 변화 |
| **Contract** | 파라미터 변환 규칙 | 입력 A → 변환 결과 B |
| **Invariant** | Invariants | 불변 조건 위반 시 에러 |

### 예시

```csharp
// Trace: Stage 1, Step 2 — CreatePartnerAsync duplicate check
[Fact]
public async Task CreatePartner_DuplicateId_ReturnsConflict()
{
    // Arrange: 이미 존재하는 partner
    await CreateTestPartner("existing_id");

    // Act: 같은 ID로 생성 시도
    var result = await _service.CreatePartnerAsync(
        new affiliate_partner { PartnerId = "existing_id" });

    // Assert: Trace의 Error Path 대로 BusinessRuleViolation
    Assert.Throws<BusinessRuleViolationException>();
}
```

---

## Decision Gate

모든 결정에 적용하는 **자율 판단 vs 유저 질문 판별기**.

### 핵심: Switching Cost

> "이 결정을 나중에 뒤집으려면 몇 줄 고쳐야 하나?"

| Tier | Lines | 행동 | 예시 |
|------|-------|------|------|
| tiny | ~5 | 자율 판단 | Config 값, 상수, 에러 메시지 |
| small | ~20 | 자율 판단 | 함수 내 구현, 파일 위치 |
| medium | ~50 | **유저에게 질문** | 인터페이스 변경, 여러 파일 |
| large | ~100 | **유저에게 질문** | 스키마 마이그레이션 |
| xlarge | ~500 | **유저에게 질문** | 아키텍처 전환 |

**목적: 유저 질문 횟수 최소화.** 사소한 것은 자율 판단하고 로그만 남긴다.

---

## Skill Reference

### Core Skills (3-Phase)

| Skill | Phase | 역할 | Input → Output |
|-------|-------|------|----------------|
| `stv:spec` | 1. Spec | PRD + Architecture 인터뷰 | 피쳐 설명 → `docs/{f}/spec.md` |
| `stv:trace` | 2. Trace | Vertical Trace + RED tests | spec.md → `docs/{f}/trace.md` + tests |
| `stv:work` | 3. Verify | 구현(GREEN) + Trace Verify | trace.md → code + verified trace |

### Orchestration Skills

| Skill | 역할 | 호출 관계 |
|-------|------|----------|
| `stv:new-task` | 모호한 요구사항 → spec + trace | spec → trace 순차 호출 |
| `stv:do-work` | 자율 구현 실행 루프 | work 반복 호출 + quality gate |
| `stv:what-to-work` | 다음 작업 결정 라우터 | → what-we-have or plan-new-task |
| `stv:what-we-have-to-work` | 미완성 시나리오 번들링 | → do-work |
| `stv:plan-new-task` | 백로그 빈 경우 신규 피쳐 제안 | → new-task |

### Skill Flow Diagram

```
유저: "뭐 할까?"
       │
       ▼
 ┌──────────────┐
 │ what-to-work │ ← trace.md 스캔
 └──────┬───────┘
        │
   ┌────┴─────┐
   ▼          ▼
 미완성     완료/없음
 시나리오    시나리오
   │          │
   ▼          ▼
 ┌──────────────────┐   ┌───────────────┐
 │what-we-have-to-  │   │ plan-new-task  │
 │work              │   │               │
 │ (번들 제안)       │   │ (피쳐 제안)    │
 └────────┬─────────┘   └───────┬───────┘
          │                     │
          ▼                     ▼
 ┌──────────────┐       ┌──────────────┐
 │   do-work    │       │   new-task   │
 │ (자율 실행)   │       │ (spec+trace) │
 └──────┬───────┘       └──────┬───────┘
        │                      │
        ▼                      ▼
 ┌──────────────┐       ┌──────────────┐
 │  stv:work    │       │  stv:spec    │
 │ (GREEN+검증)  │       │  stv:trace   │
 └──────────────┘       └──────────────┘
```

```
유저: "이 피쳐 만들어줘"
       │
       ▼
 ┌──────────────┐
 │   new-task   │
 └──────┬───────┘
        │
   ┌────┴────┐
   ▼         ▼
 stv:spec  stv:trace
   │         │
   ▼         ▼
 spec.md   trace.md + RED tests
              │
              ▼
        ┌──────────┐
        │ do-work  │
        └────┬─────┘
             │
        ┌────┴────┐
        ▼         ▼
     stv:work   stv:work
     (scenario1) (scenario2)
        │         │
        ▼         ▼
      GREEN     GREEN
        │         │
        ▼         ▼
     Verify    Verify
```

---

## Artifact 구조

STV가 생성하는 파일:

```
docs/
└── {feature-name}/
    ├── spec.md       ← Phase 1: PRD + Architecture
    └── trace.md      ← Phase 2: Vertical Trace + Contract Test 목록

tests/
└── {feature}/
    └── *Tests.cs     ← Phase 2: RED Contract Tests

src/
└── **/*.cs           ← Phase 3: GREEN Implementation
```

### trace.md가 태스크 리스트

trace.md의 **Implementation Status** 테이블이 곧 태스크 리스트:

```markdown
## Implementation Status
| Scenario | Trace | Tests | Verify | Status |
|----------|-------|-------|--------|--------|
| 1. 루트 파트너 생성 | done | GREEN | Verified | Complete |
| 2. 수수료 플랜 생성 | done | RED | — | Ready |
| 3. 서브 파트너 생성 | done | RED | — | Ready |
```

별도 태스크 관리 도구 불필요. trace.md 자체가 살아있는 진행 관리 문서.

---

## 용어집

| 용어 | 정의 |
|------|------|
| **Traced Development** | STV 방법론의 정식 명칭 |
| **Vertical Trace** | 시나리오의 전 레이어 콜스택을 파라미터 단위로 추적한 문서 |
| **Contract Test** | Trace에서 파생된 테스트. Trace가 계약서, Test가 이행 검증 |
| **Trace Verify** | 구현 후 trace 문서와 실제 코드의 일치를 대조 검증 |
| **Decision Gate** | Switching cost 기반 자율 판단 vs 유저 질문 판별기 |
| **Side-Effect** | DB INSERT/UPDATE/DELETE 등 상태 변경 |
| **Invariant** | 각 단계에서 보장되어야 할 불변 조건 |
| **Slop** | AI가 생성한 표면적으로만 동작하는 저품질 코드 |
| **Source of Truth** | Trace 문서. 코드가 아닌 trace가 기준 |

---

## Quick Start

```bash
# 1. 새 피쳐 시작 (spec → trace → 태스크 리스트 자동 생성)
/stv:new-task "파트너 트래킹 링크 CRUD"

# 2. 또는 단계별로 수동 실행
/stv:spec "파트너 트래킹 링크 CRUD"
/stv:trace docs/tracking-link/spec.md
/stv:work docs/tracking-link/trace.md

# 3. 자율 실행 모드 (시나리오 반복 구현)
/stv:do-work

# 4. 다음 작업 결정
/stv:what-to-work
```

---

## Plugin Structure

```
stv/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── spec/SKILL.md          # Phase 1: Feature Spec Interview
│   ├── trace/SKILL.md         # Phase 2: Vertical Trace + RED Tests
│   ├── work/SKILL.md          # Phase 3: GREEN + Trace Verify
│   ├── new-task/SKILL.md      # Orchestration: 모호한 요구 → spec+trace
│   ├── do-work/SKILL.md       # Orchestration: 자율 실행 루프
│   ├── what-to-work/SKILL.md  # Orchestration: 라우터
│   ├── what-we-have-to-work/SKILL.md  # Orchestration: 번들링
│   └── plan-new-task/SKILL.md # Orchestration: 신규 피쳐 제안
└── prompts/
    └── decision-gate.md       # Switching cost 기반 판별기
```

---

## License

MIT
