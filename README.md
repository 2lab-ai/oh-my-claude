# oh-my-claude

[![Korean](https://img.shields.io/badge/lang-한국어-blue.svg)](#한국어)

Claude Code plugin for AI-powered iterative development loops.

Inspired by [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) and [Ralph Wiggum](https://ghuntley.com/ralph/).

## Installation

```bash
/plugin marketplace add 2lab-ai/oh-my-claude
/plugin install oh-my-claude@oh-my-claude
/plugin install powertoy@oh-my-claude
```

---

## Main Features

### /ultrawork - Multi-Agent Work Loop

Ralph loop with 3 specialized AI agents for autonomous development.

```bash
/ultrawork "Build REST API for users"
```

**Agents:**
- **Oracle** (Codex GPT-5.2): Architecture decisions, failure analysis (blocking)
- **Explore** (Gemini): Internal codebase search (parallel)
- **Librarian** (Opus 4.5): External docs, GitHub source analysis (parallel)

Loop exits when task is genuinely complete.

### /deepwork - Reviewed Work Loop

Same as ultrawork, but requires **9.5+ score** from both Codex and Gemini reviewers before completion.

```bash
/deepwork "Critical security fix" --max-iterations 50
```

### /save & /load - Cross-Session Context

Save work context and resume in new sessions or different tools.

```bash
# Save current context
/save

# Resume later
/load
```

**Works across:**
- Claude Code sessions
- [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)

Saves: plan, TODO list, work context to `./docs/tasks/save/`

---

## Commands Reference

### oh-my-claude

| Command | Description |
|---------|-------------|
| `/ultrawork` | Multi-agent work loop |
| `/deepwork` | Work loop with 9.5+ review gate |
| `/save` | Save work context |
| `/load <id>` | Load saved context |
| `/list-saves` | List all saved contexts |
| `/check [all\|id]` | Verify archived saves completion |
| `/ralph-loop` | Start basic Ralph loop |
| `/cancel-ralph` | Cancel active loop |
| `/ralph-help` | Usage guide |

### powertoy

| Hook | Description |
|------|-------------|
| **auto-title.sh** | Auto-generate session titles (Claude Haiku) |
| **play-sound.sh** | Play sound on session end (macOS) |

---

## MCP Servers

Bundled MCP servers:

| Server | Package |
|--------|---------|
| gemini | @2lab.ai/gemini-mcp-server |
| claude | @2lab.ai/claude-mcp-server |
| codex | codex mcp-server |

---

## Credits

- **Ralph Wiggum technique**: [Geoffrey Huntley](https://ghuntley.com/ralph/)
- **Original plugin**: Daisy Hollman (Anthropic)
- **oh-my-opencode**: [code-yeongyu](https://github.com/code-yeongyu/oh-my-opencode)

## License

MIT

---

# 한국어

Claude Code용 AI 기반 반복 개발 루프 플러그인.

[oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)와 [Ralph Wiggum](https://ghuntley.com/ralph/)에서 영감을 받음.

## 설치

```bash
/plugin marketplace add 2lab-ai/oh-my-claude
/plugin install oh-my-claude@oh-my-claude
/plugin install powertoy@oh-my-claude
```

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

ultrawork와 동일하나, Codex와 Gemini 리뷰어 모두 **9.5점 이상** 필요.

```bash
/deepwork "보안 취약점 수정" --max-iterations 50
```

### /save & /load - 크로스 세션 컨텍스트

작업 컨텍스트를 저장하고 새 세션이나 다른 도구에서 재개.

```bash
# 현재 컨텍스트 저장
/save

# 나중에 재개
/load
```

**호환:**
- Claude Code 세션 간
- [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)와 상호 호환

저장 항목: 계획, TODO 목록, 작업 컨텍스트 (`./docs/tasks/save/`)

---

## 명령어 레퍼런스

### oh-my-claude

| 명령어 | 설명 |
|--------|------|
| `/ultrawork` | 멀티 에이전트 작업 루프 |
| `/deepwork` | 9.5+ 리뷰 게이트 작업 루프 |
| `/save` | 작업 컨텍스트 저장 |
| `/load <id>` | 저장된 컨텍스트 로드 |
| `/list-saves` | 저장된 컨텍스트 목록 |
| `/check [all\|id]` | 아카이브 완료 상태 확인 |
| `/ralph-loop` | 기본 Ralph 루프 시작 |
| `/cancel-ralph` | 활성 루프 취소 |
| `/ralph-help` | 사용 가이드 |

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

- **Ralph Wiggum 기법**: [Geoffrey Huntley](https://ghuntley.com/ralph/)
- **원본 플러그인**: Daisy Hollman (Anthropic)
- **oh-my-opencode**: [code-yeongyu](https://github.com/code-yeongyu/oh-my-opencode)

## 라이선스

MIT
