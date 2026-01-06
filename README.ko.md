# oh-my-claude

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)

> [!CAUTION]
> **실험적 프로젝트** - 이 플러그인은 자율 AI 루프를 실행하며 상당한 토큰을 소비할 수 있습니다.
> 토큰 사용량에 주의하세요! `/ultrawork`와 `/deepwork`는 완료될 때까지 반복합니다.
> `--max-iterations`로 제한을 설정하세요. 경고했습니다.

[2lab.ai](https://2lab.ai)의 Claude Code 플러그인 마켓플레이스

[oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)에서 영감을 받음

Ralph Loop는 [ralph wiggum plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-wiggum)에서 가져옴

## 설치

```bash
# 마켓플레이스 추가
/plugin marketplace add 2lab-ai/oh-my-claude
/plugin install oh-my-claude@oh-my-claude
/plugin install powertoy@oh-my-claude
```

---

## 워크플로우

### Ultra Work Loop

```bash
/ultrawork "할일"      # 자율 완료
/deepwork "할일"       # AI 리뷰 게이트 (9.5+ 필요)
```

에이전트 오케스트레이션이 포함된 Ralph Loop. `/deepwork`는 GPT-5.2 + Gemini-3 + Opus-4.5 삼중 리뷰를 통해 모두 9.5점 이상일 때만 완료.

### 크로스 세션 & 크로스 툴 워크플로우

```bash
# 작업 중 컨텍스트 저장
/save

# 새 세션에서 이어서 작업
/load
```

**사용 시나리오:**

1. **세션 간 작업 연속성** - Claude Code에서 작업하다가 `/save` 후, 새 세션에서 `/load`하면 그대로 이어서 작업 가능

2. **도구 간 작업 이동** - Claude Code에서 `/save` 후, [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)에서 `/load`로 이어서 작업 가능 (또는 그 반대)

저장되는 내용: 현재 플랜, TODO 리스트, 작업 컨텍스트

---

## oh-my-claude

작업 관리 및 Ralph Wiggum 루프.

### 작업 관리 명령어

| 명령어 | 설명 |
|--------|------|
| `/ohmyclaude:save` | 현재 작업 컨텍스트를 `./docs/tasks/save/{id}`에 저장 |
| `/ohmyclaude:load <id>` | 저장된 작업 컨텍스트 로드 후 재개 |
| `/ohmyclaude:list-saves` | 브랜치 필터링으로 저장된 모든 컨텍스트 목록 표시 |
| `/ohmyclaude:check [all\|id]` | 아카이브된 저장의 완료 상태 확인 |

### Ralph Wiggum Loop

반복적인 작업 완료를 위한 자기 참조 AI 개발 루프.

| 명령어 | 설명 |
|--------|------|
| `/ultrawork` | 멀티 에이전트 자율 작업 루프 |
| `/deepwork` | 삼중 AI 리뷰 게이트 작업 루프 (GPT-5.2 + Gemini-3 + Opus-4.5, 모두 ≥9.5) |
| `/cancel-work` | 활성 루프 취소 |
| `/setup` | 의존성 확인 |

**빠른 시작:**
```bash
/ultrawork "TODO를 위한 REST API 구축"
```

### MCP 서버 (포함)

- `gemini` - @2lab.ai/gemini-mcp-server
- `claude` - @2lab.ai/claude-mcp-server
- `codex` - codex mcp-server

---

## powertoy

Claude Code 세션을 위한 파워 유틸리티.

### 훅

| 훅 | 설명 |
|----|------|
| **auto-title.sh** | Claude Haiku를 사용하여 제목 없는 세션에 자동으로 제목 생성 |
| **play-sound.sh** | 세션 종료 시 알림 소리 재생 (macOS) |

---

## Ralph Wiggum 기법

```json
{
  "credits": [
    {
      "name": "Geoffrey Huntley",
      "contribution": "Ralph Wiggum 기법",
      "url": "https://ghuntley.com/ralph/"
    },
    {
      "name": "Daisy Hollman",
      "email": "daisy@anthropic.com",
      "contribution": "원본 ralph-wiggum 플러그인 구현"
    }
  ]
}
```

Ralph는 연속적인 AI 에이전트 루프를 기반으로 한 개발 방법론입니다. 이 기법은 심슨 가족의 Ralph Wiggum의 이름을 따서 명명되었으며, 좌절에도 불구하고 끈질기게 반복하는 철학을 구현합니다.

### 작동 방식

```bash
# 한 번만 실행:
/ultrawork "작업 설명"

# 그러면 Claude Code가 자동으로:
# 1. 작업 수행
# 2. 종료 시도
# 3. Stop 훅이 종료 차단
# 4. Stop 훅이 동일한 프롬프트를 다시 전달
# 5. 완료될 때까지 반복
```

### 모범 사례

1. **명확한 완료 기준** - 작업이 "완료"되는 시점을 항상 지정
2. **점진적 목표** - 큰 작업을 단계별로 분할
3. **자가 수정** - TDD/검증 단계 포함
4. **안전 제한** - 탈출구로 `--max-iterations` 항상 사용

### 사용 시기

**적합한 경우:**
- 명확한 성공 기준이 있는 잘 정의된 작업
- 반복이 필요한 작업 (예: 테스트 통과시키기)
- 자리를 비울 수 있는 그린필드 프로젝트
- 자동 검증이 가능한 작업

**적합하지 않은 경우:**
- 인간의 판단이 필요한 작업
- 일회성 작업
- 불명확한 성공 기준

---

## 크레딧

- **Ralph Wiggum 기법**: [Geoffrey Huntley](https://ghuntley.com/ralph/)
- **원본 ralph-wiggum 플러그인**: Daisy Hollman (daisy@anthropic.com, Anthropic)

## 더 알아보기

- Ralph Wiggum: https://ghuntley.com/ralph/
- Ralph Orchestrator: https://github.com/mikeyobrien/ralph-orchestrator

## 라이선스

MIT
