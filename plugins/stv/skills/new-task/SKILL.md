---
name: new-task
description: "Transform vague user requirements into STV-structured feature specs with traced scenarios. Orchestrates stv:spec and stv:trace to produce implementable work."
---

# New Task — STV Feature Decomposition

## Overview

**new-task transforms vague user requirements into structured STV artifacts (spec.md + trace.md) with traced scenarios as the task list.**

Core principle: Understand intent deeply → Create spec via stv:spec → Create trace via stv:trace → trace.md scenarios = task list.

## When to Use

Use when:
- User describes feature/idea in vague or high-level terms
- Need to decompose work into implementable scenarios
- Architectural decisions required before implementation
- Multiple implementation approaches possible
- Work requires structured spec + trace before coding

Do NOT use when:
- User request is already specific (1-2 file changes)
- Fixing obvious bug with clear solution
- Quick clarification or simple question
- Spec and trace already exist (use `stv:do-work` directly)

## Sizing Rubric

| Tier   | Lines  | 예시                              |
|--------|--------|-----------------------------------|
| tiny   | ~5     | Config 값, 상수, 문자열 리터럴      |
| small  | ~20    | 한 함수, 한 파일, 로컬 리팩터       |
| medium | ~50    | 여러 파일, 인터페이스 변경           |
| large  | ~100   | 횡단 관심사, 스키마 마이그레이션      |
| xlarge | ~500   | 아키텍처 전환, 프레임워크 교체        |

## Workflow Phases

```
Phase 1: Intent Understanding
    ↓
Phase 2: Spec Creation (→ stv:spec)
    ↓
Phase 3: Trace Creation (→ stv:trace)
    ↓
Phase 4: Summary & Next Steps
```

### Phase 1: Intent Understanding (~5min)

**Goal**: Ground the vague request in actual project context.

1. **유저 요청 분석**
   - 핵심 의도 파악
   - 암묵적 요구사항 추출
   - 스코프 범위 예측

2. **코드베이스 탐색** (Agent:Explore)
   - 관련 기존 코드 파악
   - 기존 패턴, 컨벤션, 아키텍처 이해
   - 유사 기능 존재 여부 확인
   - 영향 받는 영역 매핑

3. **컨텍스트 요약**
   - 발견한 관련 코드/패턴 정리
   - 기존 아키텍처와의 통합 포인트 식별
   - Phase 2에서 spec 인터뷰에 활용할 정보 준비

### Phase 2: Spec Creation → Invoke stv:spec

**Goal**: 구조화된 spec.md 생성.

```
Skill(skill="stv:spec") 발동
```

- Phase 1에서 수집한 컨텍스트를 기반으로 spec 인터뷰 진행
- Decision Gate 적용: switching cost < small → 자율 판단, >= medium → 유저 질문
- **Output**: `docs/{feature}/spec.md`

### Phase 3: Trace Creation → Invoke stv:trace

**Goal**: spec을 시나리오별 수직 트레이스로 분해 + RED contract tests 생성.

```
Skill(skill="stv:trace") 발동
```

- spec.md를 입력으로 시나리오별 콜스택 추적
- 각 시나리오에 contract test 파생
- **Output**: `docs/{feature}/trace.md` + RED tests

### Phase 4: Summary & Next Steps (~2min)

**Goal**: 유저에게 전체 결과 요약 + 실행 안내.

1. **trace.md 시나리오 목록 = 태스크 리스트**
   - Implementation Status 테이블에서 각 시나리오가 하나의 작업 단위

2. **유저에게 요약 제시**

```markdown
## Feature Ready: {feature-name}

### Artifacts Created
- `docs/{feature}/spec.md` — PRD + Architecture
- `docs/{feature}/trace.md` — {N} scenarios traced
- {N} RED contract tests created

### Scenario Task List
| # | Scenario | Size | Status |
|---|----------|------|--------|
| 1 | {title} | {tier} | Ready |
| 2 | {title} | {tier} | Ready |
| ... | ... | ... | ... |

### Auto-Decisions Made
{Decision Gate에서 자율 판단한 항목 요약}

### Next Step
→ `stv:do-work` 로 시나리오별 구현 시작
→ 또는 `stv:work docs/{feature}/trace.md` 로 직접 구현
```

## Integration with Other Skills

**INVOKES:**
- `stv:spec` — Phase 2에서 spec 생성
- `stv:trace` — Phase 3에서 trace 생성

**SEQUENTIAL:**
After new-task completes → Use `stv:do-work` for execution

**CALLED BY:**
- `stv:plan-new-task` — 신규 피쳐 제안 후 선택된 아이디어에 대해 호출

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Phase 1 건너뛰기 | 항상 코드베이스 탐색 먼저 — 현실에 기반한 계획 |
| spec 없이 trace 시작 | 반드시 stv:spec → stv:trace 순서 |
| trace 시나리오를 태스크로 보지 않음 | trace.md의 Implementation Status = 태스크 리스트 |
| 사소한 것까지 유저에게 질문 | Decision Gate 적용: switching cost < small이면 자율 판단 |

## NEVER

- stv:spec 또는 stv:trace의 워크플로우를 건너뛰거나 축약
- trace 없이 구현 시작 안내
- 시나리오 목록 없이 "완료" 선언
