# oh-my-claude

```
   ____  _    _       __  ____     __      _____ _                 _
  / __ \| |  | |     |  \/  \ \   / /     / ____| |               | |
 | |  | | |__| |_____| \  / |\ \_/ /_____| |    | | __ _ _   _  __| | ___
 | |  | |  __  |_____| |\/| | \   /______| |    | |/ _` | | | |/ _` |/ _ \
 | |__| | |  | |     | |  | |  | |       | |____| | (_| | |_| | (_| |  __/
  \____/|_|  |_|     |_|  |_|  |_|        \_____|_|\__,_|\__,_|\__,_|\___|

```

> [!CAUTION]
> **실험적 프로젝트** - 이 플러그인은 자율 AI 루프를 실행하며 상당한 토큰을 소비할 수 있습니다.
> 토큰 사용량에 주의하세요! `/ultrawork`와 `/deepwork`는 완료될 때까지 반복합니다.
> `--max-iterations`로 제한을 설정하세요. 경고했습니다.

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)

Claude Code용 AI 기반 반복 개발 루프 플러그인.

[oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)와 [Ralph Wiggum](https://ghuntley.com/ralph/)에서 영감을 받음.

## 설치

```bash
/plugin marketplace add 2lab-ai/oh-my-claude
/plugin install oh-my-claude@oh-my-claude
/plugin install powertoy@oh-my-claude
```

> **필수**: 설치 후 `/oh-my-claude:setup` 실행.

### 인증

oh-my-claude는 **Gemini CLI**와 **Codex CLI** 구독을 사용합니다 (API 키 아님).

```bash
# 1. setup으로 의존성 확인
/oh-my-claude:setup

# 2. 각 서비스에 로그인
gemini auth login    # 브라우저에서 Google 인증
codex auth           # 브라우저에서 OpenAI 인증

# 3. 다시 setup으로 확인
/oh-my-claude:setup
```

인증 후, 에이전트는 기존 구독을 사용:
- **Explore 에이전트** → Gemini 구독
- **Oracle 에이전트** → OpenAI/Codex 구독
- **Librarian 에이전트** → Claude 구독 (Claude Code로 이미 인증됨)

---

## 주요 기능

### /ultrawork - 멀티 에이전트 작업 루프

3개의 전문 AI 에이전트를 활용한 자율 개발 Ralph 루프.

```bash
/ultrawork "REST API 구현"
```

**에이전트:**
- **Oracle** (Codex GPT-5.2): 아키텍처 결정, 실패 분석 (블로킹)
- **Explore** (Gemini): 내부 코드베이스 검색 (병렬)
- **Librarian** (Opus 4.5): 외부 문서, GitHub 소스 분석 (병렬)

작업이 완료되면 루프 종료.

### /deepwork - 리뷰 기반 작업 루프

ultrawork와 동일하나, 3개 리뷰어(GPT-5.2, Gemini-3, Opus-4.5) 모두 **9.5점 이상** 필요.

```bash
/deepwork "보안 취약점 수정" --max-iterations 50
```

### /save & /load - 크로스 툴 컨텍스트 관리

한 도구에서 작업 컨텍스트를 저장하고 다른 도구에서 재개.

```bash
# Claude Code에서: 작업 저장
/save

# Gemini CLI 또는 Codex에서: 작업 재개
/load
```

**크로스 툴 워크플로우 예시:**
1. Claude Code에서 작업 시작, 완료 시 `/save`
2. Gemini CLI 또는 Codex 열기, `/load`로 이어서 작업
3. 도구 간 자유롭게 전환 - 모두 `./docs/tasks/save/` 공유

**크로스 툴 명령어 설치:**
```bash
./install-cross-session-commands.sh
```

다음 위치에 `/save`, `/load`, `/list-saves`, `/check` 설치:
- `~/.gemini/commands/` (Gemini CLI)
- `~/.codex/prompts/` (Codex)

---

## 명령어 레퍼런스

### oh-my-claude

| 명령어 | 설명 |
|--------|------|
| `/ultrawork` | 멀티 에이전트 자율 작업 루프 |
| `/deepwork` | 삼중 AI 리뷰 게이트 작업 루프 (GPT-5.2 + Gemini-3 + Opus-4.5, 모두 ≥9.5) |
| `/save` | 작업 컨텍스트 저장 |
| `/load <id>` | 저장된 컨텍스트 로드 |
| `/list-saves` | 저장된 컨텍스트 목록 |
| `/check [all\|id]` | 아카이브 완료 상태 확인 |
| `/cancel-work` | 활성 루프 취소 |
| `/setup` | 의존성 확인 |

### powertoy

| 훅 | 설명 |
|----|------|
| **auto-title.sh** | 세션 제목 자동 생성 (Claude Haiku) |
| **play-sound.sh** | 세션 종료 시 알림음 (macOS) |

---

## MCP 서버

번들 MCP 서버:

| 서버 | 패키지 |
|------|--------|
| gemini | @2lab.ai/gemini-mcp-server |
| claude | @2lab.ai/claude-mcp-server |
| codex | codex mcp-server |

---

## 크레딧

- **oh-my-opencode**: [code-yeongyu](https://github.com/code-yeongyu/oh-my-opencode)
- **Ralph Wiggum 플러그인**: https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum
- **Ralph Wiggum 기법**: [Geoffrey Huntley](https://ghuntley.com/ralph/)

## FAQ

**Q: 토큰 많이 태우나요?**

A: 네. 버그가 아니라 기능입니다.

```
     /\_/\
    ( o.o )  "I'm helping!"
     > ^ <   - Your AI, iteration 47
```

## TODO

- [ ] LSP support

## 라이선스

MIT
