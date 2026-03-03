---
name: spec
description: "STV Phase 1: Feature interview -> spec.md. PRD + Architecture decisions in one pass. Uses decision-gate to minimize questions."
---

# STV Spec — Feature Spec Interview

> STV Phase 1: 피쳐 인터뷰 → `docs/{feature}/spec.md`
> PRD(무엇을) + Architecture(어떻게)를 한 패스로 확정한다.

---

## Decision Gate (MANDATORY)

**Read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` and apply it to every decision in this workflow.**

**이 게이트를 모든 결정에 적용한다. switching cost < small이면 자율 판단, >= medium이면 유저에게 질문.**

---

## Phase 1: Input Analysis

1. **Argument 해석**:
   - 파일 경로 → 읽고 분석
   - Feature 이름/설명 → 시작점으로 사용
   - 기존 spec이 있으면 → 업데이트 모드

2. **코드베이스 탐색** (Agent:Explore):
   - 관련 기존 코드 파악
   - 기존 패턴, 컨벤션, 아키텍처 이해
   - 이 피쳐가 영향을 미치는 영역 매핑

## Phase 2: Spec Interview

**AskUserQuestion**으로 인터뷰한다. 단, Decision Gate 적용:
- **자율 판단 가능한 것** (기존 코드에서 명확한 패턴, tiny/small switching cost) → 묻지 않고 spec에 기록
- **유저 확인 필요한 것** (medium+ switching cost) → 질문

### 2.1 PRD 영역 — "무엇을 만들 건가?"

한 번의 AskUserQuestion에 관련 질문 2-4개를 묶어서 묻는다:

**반드시 커버할 항목:**
- 유저 스토리 / 핵심 시나리오
- 수용 기준 (Acceptance Criteria)
- 스코프 경계 (In-Scope / Out-of-Scope)
- 비기능 요구사항 (성능, 보안, 확장성)

**Decision Gate 적용:**
- 기존 코드에서 패턴이 명확한 것 → 자율 결정 + spec에 기록
- 비즈니스 규칙, 유저 경험 → 유저에게 질문

### 2.2 Architecture 영역 — "어떻게 만들 건가?"

**반드시 커버할 항목:**
- 레이어 구조 (Controller → Handler → Service → DB)
- DB 스키마 / Entity 설계
- API 엔드포인트 목록 + HTTP method
- 기존 코드와의 통합 포인트
- 에러 처리 전략
- 인증/인가 모델

**Decision Gate 적용:**
- 기존 아키텍처 패턴 답습 → 자율 결정
- 새로운 패턴 도입, 스키마 변경 → [tier ~N줄] 표기하여 질문

### Interview Guidelines

**DO:**
- 2-4개 질문을 한 번의 AskUserQuestion에 묶어 질문 횟수 최소화
- 코드베이스 탐색 결과를 바탕으로 구체적 질문 (파일명, 함수명 포함)
- 각 질문에 추천안 제시 (유저가 "OK" 한 마디로 넘어갈 수 있게)
- 자율 판단한 것들을 `### Auto-Decisions` 섹션에 기록

**DON'T:**
- 코드베이스에서 답을 알 수 있는 걸 묻지 않는다
- 한 번에 5개 이상 질문하지 않는다
- Yes/No로 끝나는 질문 대신 선택지를 제시한다

## Phase 3: Spec Writing

인터뷰 완료 후 (유저 확인 또는 모든 차원 커버):

### Output: `docs/{feature-name}/spec.md`

```markdown
# {Feature Name} — Spec

> STV Spec | Created: {date}

## 1. Overview
{1-2 문단: 이 피쳐가 무엇이고 왜 필요한가}

## 2. User Stories
- As a {actor}, I want {action}, so that {outcome}
- ...

## 3. Acceptance Criteria
- [ ] {criterion 1}
- [ ] {criterion 2}
- ...

## 4. Scope
### In-Scope
- ...
### Out-of-Scope
- ...

## 5. Architecture

### 5.1 Layer Structure
{Controller → Handler → Service → DB 흐름 개요}

### 5.2 API Endpoints
| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| POST | /api/... | ...Create | ... |
| GET | /api/... | ...List | ... |
| ... | ... | ... | ... |

### 5.3 DB Schema
{Entity 목록 + 주요 필드}

### 5.4 Integration Points
{기존 시스템과의 연결 지점}

## 6. Non-Functional Requirements
- Performance: ...
- Security: ...
- Scalability: ...

## 7. Auto-Decisions
{Decision Gate에서 자율 판단한 내용. switching cost와 근거 포함}

| Decision | Tier | Rationale |
|----------|------|-----------|
| ... | tiny | ... |
| ... | small | ... |

## 8. Open Questions
{남아있는 미결 사항. 없으면 "None"}

## 9. Next Step
→ `stv:trace` 로 Vertical Trace 진행
```

## Completion

1. spec.md를 `docs/{feature-name}/spec.md`에 저장
2. 유저에게 spec 요약 + 다음 단계 안내
3. **다음 스킬 안내**: `Skill(skill="stv:trace")` 또는 유저에게 `stv:trace docs/{feature-name}/spec.md` 사용 안내
