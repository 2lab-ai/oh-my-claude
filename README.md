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

> **Required**: Run `/oh-my-claude:setup` after installation to verify dependencies.

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

### /save & /load - Cross-Tool Context Management

Save work context in one tool and resume in another.

```bash
# In Claude Code: save your work
/save

# In Gemini CLI or Codex: resume the work
/load
```

**Cross-tool workflow example:**
1. Start work in Claude Code, `/save` when done
2. Open Gemini CLI or Codex, `/load` to continue
3. Work across tools seamlessly - they share `./docs/tasks/save/`

**To enable cross-tool commands:**
```bash
./install-cross-session-commands.sh
```

This installs `/save`, `/load`, `/list-saves`, `/check` to:
- `~/.gemini/commands/` (Gemini CLI)
- `~/.codex/prompts/` (Codex)

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

## TODO

- [ ] LSP support

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

> **필수**: 설치 후 `/oh-my-claude:setup`을 실행하여 의존성을 확인하세요.

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

## TODO

- [ ] LSP support

## 라이선스

MIT
