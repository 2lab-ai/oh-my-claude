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

## STV의 4 Invariants

STV를 방법론으로 성립시키는 핵심 컴포넌트. 어떤 Phase에 있든 이 네 가지는 항상 유지되어야 한다.

### 1. 트레이스 스펙 (Trace Spec)

시나리오별 엔드투엔드 실행선 문서. 코드가 아닌 **문서가 먼저** 만들어진다. Tracer Bullet이 "코드로 뚫는다"면, STV는 "문서로 먼저 고정한다."

### 2. 계약 테스트 (Contract Tests)

트레이스 스펙을 자동화 테스트로 변환한 것. 반드시 RED 상태로 시작한다. **트레이스 문서 = 계약의 텍스트 버전, 계약 테스트 = 계약의 실행 버전.**

### 3. 적합성 게이트 (Conformance Gate)

"스펙이 있어야 테스트가 가능하고, 테스트가 있어야 적합성 주장이 가능하다"는 논리적 체인. 실무적으로는 **스펙 없이는 PR merge 불가**라는 프로세스 게이트로 운영한다.

### 4. 피드백 루프 (Feedback Loop)

구현 중 trace와 불일치가 발견되면 trace를 수정하거나 코드를 수정한다. **어느 쪽이든 둘은 항상 동기화된다.** trace와 코드가 괴리된 채 방치되면 STV는 죽은 문서가 된다.

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
  → Trace: 7-section으로 전 레이어 파라미터 단위 추적
  → Contract Test: trace의 각 섹션을 강제하는 테스트
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
| **Design by Contract** (Bertrand Meyer) | Pre/Post condition 강제 | Error Paths + Side Effects 검증 |
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
│  Step 1-0: Input Analysis                             │
│  Step 1-1: Business Interview — 유저 스토리, 수용 기준  │
│  Step 1-2: Architecture Interview — 레이어, DB, API    │
│  Step 1-3: Spec Writing                               │
│                                                       │
│  Output: docs/{feature}/spec.md                       │
└───────────────────────┬───────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────┐
│  Phase 2: TRACE                                       │
│  "청사진 + 계약"                                       │
│                                                       │
│  ① 7-Section Vertical Trace — 시나리오별 전 레이어 문서 │
│    API Entry → Input → Layer Flow → Side Effects →    │
│    Error Paths → Output → Observability               │
│    (파라미터 변환 화살표 필수)                           │
│  ② Contract Tests (RED) — 4가지 카테고리로 파생        │
│    Happy path / Sad path / Side-effect / Contract     │
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
│  ② Trace Conformance — 7-section 기준 대조 검증        │
│  ③ Loop: 불일치 시 → trace 수정 or 코드 수정           │
│                                                       │
│  Output: src/**/* (all GREEN) + trace.md (Verified)   │
└───────────────────────────────────────────────────────┘
```

---

## Vertical Trace — 7-Section Format

시나리오별로 API 요청이 시스템의 전 레이어를 관통하는 과정을 **7개 섹션**으로 구조화한 문서.

### 7-Section Minimum Field Spec

```markdown
## Trace: [시나리오 이름]

### 1. API Entry
- HTTP Method, Path, 인증/인가

### 2. Input (요청)
- 요청 페이로드 + 검증 규칙

### 3. Layer Flow ★핵심★
- 3a. Controller/Handler: Request → Command 변환
- 3b. Service: Command → Entity 변환 + 도메인 판단
- 3c. Repository/DB: Entity → Row 매핑 + 트랜잭션

### 4. Side Effects
- DB 변경 (INSERT/UPDATE/DELETE)
- 이벤트/메시지, 캐시 변경

### 5. Error Paths
- 검증 실패, 인증/인가 실패, 충돌, 하류 실패

### 6. Output (응답)
- 성공 상태 코드 + 응답 스키마

### 7. Observability Hooks [선택]
- 로그 필드, 트레이스/스팬, 메트릭
```

### 파라미터 변환 화살표 (MANDATORY)

Layer Flow에서 반드시 명시:

```
Request.FieldA → Command.PropertyA → Entity.AttributeA → table.column_a
```

이 화살표가 Contract 테스트의 원천이 된다.

### 각 섹션의 역할

| Section | 역할 | 파생 테스트 |
|---------|------|-----------|
| 1. API Entry | 진입점 정의 | — |
| 2. Input | 요청 검증 규칙 | Sad Path (검증 실패) |
| 3. Layer Flow | 파라미터 변환 체인 | Contract (변환 검증) |
| 4. Side Effects | 상태 변경 | Side-Effect |
| 5. Error Paths | 에러 분기 | Sad Path (비즈니스 에러) |
| 6. Output | 응답 검증 | Happy Path |
| 7. Observability | 관측성 | — (선택) |

---

## Contract Tests

Trace 문서에서 직접 파생되는 테스트. **Trace = 계약서, Test = 계약 이행 검증.**

### Test 카테고리 (4개)

| Category | Trace에서 파생 | 검증 대상 |
|----------|--------------|----------|
| **Happy Path** | 정상 흐름 Request→Response + Side Effects | 올바른 입력 → 기대 출력 + DB 상태 변화 |
| **Sad Path** | Error Paths (검증 실패, 인증 실패, 충돌 등) | 잘못된 입력 → 기대 에러 + DB 무변경 |
| **Side-Effect** | Side Effects (DB, 이벤트, 캐시) | 호출 후 상태 변화 독립 검증 |
| **Contract** | Layer Flow의 파라미터 변환 규칙 | Request→DB까지 변환 체인 관통 검증 |

### 예시

```csharp
// Category: Contract — Trace Section 3, Layer Flow 파라미터 변환
// Request.contactEmail("UPPER@CASE.COM") → Command.ContactEmail → Entity.Email → partner.email
// 변환 규칙: 소문자 변환
[Fact]
public async Task CreatePartner_ParameterTransformation_EmailLowercased()
{
    var request = new CreatePartnerRequest
    {
        CompanyName = "Test Corp",
        ContactEmail = "UPPER@CASE.COM",
        CommissionRate = 0.10m
    };

    var response = await _client.PostAsJsonAsync("/api/partners", request);
    var body = await response.Content.ReadFromJsonAsync<PartnerResponse>();

    // 변환 규칙 검증: API 응답
    body.Email.Should().Be("upper@case.com");

    // DB까지 관통 검증
    var partner = await _dbContext.Partners.FindAsync(body.Id);
    partner!.Email.Should().Be("upper@case.com");
}
```

### Test Portfolio Strategy

```
1차 게이트 (PR merge 기준):
  Contract/Component Tests — 빠르고 안정적, 초~분 단위

2차 게이트 (배포 전 점검):
  E2E Tests — 배포 환경에서만 확인 가능한 것만, 분~십분 단위
```

---

## Decision Gate

모든 결정에 적용하는 **자율 판단 vs 유저 질문 판별기**.

### 핵심: Switching Cost

> "이 결정을 나중에 뒤집으려면 몇 줄 고쳐야 하나?"

| Tier | Lines | 행동 | 예시 |
|------|-------|------|------|
| tiny | ~5 | 자율 판단 | Config 값, 상수, 에러 메시지 |
| small | ~20 | 자율 결정 + 보고 | 함수 내 구현, 파일 위치 |
| medium | ~50 | **유저에게 질문** | 인터페이스 변경, 여러 파일 |
| large | ~100 | **유저에게 질문** | 스키마 마이그레이션 |
| xlarge | ~500 | **유저에게 질문** | 아키텍처 전환 |

**small의 차이점**: 자율 결정하되, 결정 내용과 근거를 유저에게 보고한다.

**목적: 유저 질문 횟수 최소화.** 사소한 것은 자율 판단하고 로그만 남긴다.

---

## 마이크로서비스 — CDC 분리

서비스 간 인터랙션이 있는 경우, **서비스 내부 trace**와 **서비스 간 계약(CDC)** 을 분리한다.

```
┌─────────────────────────┐     ┌─────────────────────────┐
│  Service A (소비자)      │     │  Service B (공급자)      │
│                         │     │                         │
│  Vertical Trace (내부)  │     │  Vertical Trace (내부)  │
│  Contract Tests (내부)  │────▶│  Contract Tests (내부)  │
└────────────┬────────────┘     └────────────┬────────────┘
             │                               │
             └──────── CDC Contract ─────────┘
                  (서비스 간 인터페이스 계약)
                  (Pact 등으로 자동 검증)
```

서비스 내부는 Vertical Trace + Contract Test로 검증하고, 서비스 간 인터페이스는 Pact 같은 CDC 도구로 별도 검증한다.

---

## Runtime Observability Extension (선택)

마이크로서비스 환경에서 Trace Verify의 범위를 런타임 관측까지 넓히고 싶다면, trace 문서의 Section 7 (Observability Hooks)을 활용한다.

```
Trace 문서 (설계 시간)          런타임 관측 (운영 시간)
─────────────────────          ─────────────────────
Controller → Service → DB      Span: POST /api/partners
       │         │                  └─ Span: Handler
       │         │                       └─ Span: Repository
  파라미터 변환 규칙           Span attributes에 변환 전후 값 기록
  Side Effects               Span events로 DB INSERT 기록
```

trace에 적어둔 호출 체인이 런타임의 실제 span 관계로 관측되는지 확인함으로써, 문서적 스펙과 관측 가능한 사실을 연결할 수 있다.

---

## Skill Reference

### Core Skills (3-Phase)

| Skill | Phase | 역할 | Input → Output |
|-------|-------|------|----------------|
| `stv:spec` | 1. Spec | PRD + Architecture 인터뷰 | 피쳐 설명 → `docs/{f}/spec.md` |
| `stv:trace` | 2. Trace | 7-Section Vertical Trace + RED tests | spec.md → `docs/{f}/trace.md` + tests |
| `stv:work` | 3. Verify | 구현(GREEN) + Trace Conformance | trace.md → code + verified trace |

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
    └── trace.md      ← Phase 2: 7-Section Vertical Trace + Contract Test 목록

tests/
└── {feature}/
    └── *Tests.cs     ← Phase 2: RED Contract Tests (4 categories)

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

## FAQ

### Q: 모든 시나리오에 trace를 써야 하나?

핵심 비즈니스 로직이 있는 시나리오에 집중한다. 단순 CRUD의 GET(목록 조회) 같은 것까지 full trace를 쓸 필요는 없다. 판단 기준: "파라미터 변환이 있는가?", "DB 사이드이펙트가 있는가?", "에러 경로가 분기되는가?" — 하나라도 해당되면 trace를 쓴다.

### Q: trace 문서가 거대해지면 관리가 안 되지 않나?

시나리오 단위로 파일을 분리한다. `traces/partner-create.md`, `traces/partner-update-tier.md`처럼 1 시나리오 = 1 trace 파일로 운영하면 각 파일은 1~2페이지로 유지된다.

### Q: 기존 TDD와 뭐가 다른가?

TDD는 "테스트를 먼저 쓴다." STV는 "trace를 먼저 쓰고, trace에서 테스트를 파생시킨다." TDD에서는 어떤 테스트를 쓸지가 개발자 판단에 달려 있지만, STV에서는 trace가 테스트의 원천이므로 기계적으로 결정된다. 특히 Side-effect 테스트와 파라미터 변환 테스트는 TDD에서 흔히 누락되지만, STV에서는 trace에 명시되어 있으므로 빠뜨릴 수 없다.

### Q: AI 에이전트 없이도 쓸 수 있는가?

물론이다. STV의 핵심은 "코드 전에 trace를 쓴다"는 규율이지, AI 에이전트가 필수 조건은 아니다. 다만 AI 에이전트와 함께 쓸 때 가치가 극대화된다 — 인간 개발자는 머릿속에서 trace를 수행할 수 있지만, AI 에이전트에게는 이 암묵지가 없기 때문이다.

### Q: trace와 코드가 계속 불일치하면 어떡하나?

불일치가 반복된다는 것은 Phase 1(Spec)이 불충분했다는 신호다. spec으로 돌아가서 비즈니스 요구사항이나 기술 결정을 재검토하라. trace는 "콜스택 수준"이어야 하지, 코드 한 줄 한 줄을 기술하는 것이 아니다.

---

## 용어집

| 용어 | 정의 |
|------|------|
| **Traced Development** | STV 방법론의 정식 명칭 |
| **Vertical Trace** | 시나리오의 전 레이어 콜스택을 7-section 형식으로 추적한 문서 |
| **7-Section Format** | API Entry, Input, Layer Flow, Side Effects, Error Paths, Output, Observability |
| **Parameter Transformation Arrow** | `Request.X → Command.Y → Entity.Z → table.col` 형식의 변환 체인 표기 |
| **Contract Test** | Trace에서 파생된 테스트. Trace가 계약서, Test가 이행 검증 |
| **Trace Conformance** | 구현 후 trace 문서와 실제 코드의 일치를 7-section 기준으로 대조 검증 |
| **4 Invariants** | 트레이스 스펙, 계약 테스트, 적합성 게이트, 피드백 루프 |
| **Decision Gate** | Switching cost 기반 자율 판단 vs 유저 질문 판별기 (tiny/small/medium/large/xlarge) |
| **CDC** | Consumer-Driven Contract Testing. 마이크로서비스 간 인터페이스 계약 검증 |
| **Side-Effect** | DB INSERT/UPDATE/DELETE 등 상태 변경 |
| **Source of Truth** | Trace 문서. 코드가 아닌 trace가 기준 |
| **Slop** | AI가 생성한 표면적으로만 동작하는 저품질 코드 |

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
│   ├── trace/SKILL.md         # Phase 2: 7-Section Vertical Trace + RED Tests
│   ├── work/SKILL.md          # Phase 3: GREEN + Trace Conformance
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
