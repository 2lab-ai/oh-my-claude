# oh-my-claude Specification

## Overview

**oh-my-claude**는 Claude Code를 위한 AI 기반 반복 개발 루프 플러그인입니다.

[oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)와 [Ralph Wiggum](https://ghuntley.com/ralph/) 기법에서 영감을 받았습니다.

---

## Architecture

### Plugin Structure

```
oh-my-claude/
├── plugins/
│   ├── oh-my-claude/           # Core plugin
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json     # Plugin manifest
│   │   ├── .mcp.json           # MCP server configuration
│   │   ├── agents/             # Subagent definitions
│   │   │   ├── oracle.md       # Strategic advisor (Codex GPT-5.2)
│   │   │   ├── explore.md      # Internal codebase explorer (Gemini)
│   │   │   ├── librarian.md    # External docs specialist (Opus 4.5)
│   │   │   └── reviewer.md     # Code critic (opus-4.5-ultrathink)
│   │   ├── commands/           # Slash commands
│   │   │   ├── ultrawork.md    # Multi-agent work loop
│   │   │   ├── deepwork.md     # Reviewed work loop (9.5+ gate)
│   │   │   ├── save.md         # Save work context
│   │   │   ├── load.md         # Load work context
│   │   │   ├── list-saves.md   # List saved contexts
│   │   │   ├── check.md        # Verify archived saves
│   │   │   ├── setup.md        # Setup & dependency check
│   │   │   └── cancel-work.md  # Cancel active loops
│   │   ├── hooks/
│   │   │   ├── hooks.json      # Hook configuration
│   │   │   └── stop-hook.sh    # Ralph loop stop hook
│   │   └── scripts/
│   │       └── setup-ralph-loop.sh
│   │
│   └── powertoy/               # Power utilities plugin
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── hooks/
│           ├── hooks.json
│           ├── auto-title.sh   # Auto session titling
│           └── play-sound.sh   # Notification sounds
```

---

## Core Components

### 1. MCP Servers

| Server | Package | Purpose | Required Env |
|--------|---------|---------|--------------|
| `gemini-as-mcp` | @2lab.ai/gemini-mcp-server | Gemini 모델 접근 (대용량 컨텍스트) | `GOOGLE_API_KEY` |
| `claude-as-mcp` | @2lab.ai/claude-mcp-server | Claude 세션 관리 | `ANTHROPIC_API_KEY` |
| `gpt-as-mcp` | codex mcp-server | Codex GPT-5.2 접근 (deep reasoning) | `OPENAI_API_KEY` |

**Fallback Behavior**:
- `ANTHROPIC_API_KEY` 미설정: Claude Code 자체가 작동하지 않음 (필수)
- `GOOGLE_API_KEY` 미설정: Gemini MCP 비활성화, Explore 에이전트는 기본 도구(Grep/Glob) 사용
- `OPENAI_API_KEY` 미설정: Codex MCP 비활성화, Oracle 에이전트는 Opus 모델만 사용

### 2. Agents (Subagents)

#### Oracle - Strategic Advisor
- **Model**: Opus 4.5 + Codex GPT-5.2 (가용 시)
- **Execution**: BLOCKING (결과 대기)
- **Purpose**: 아키텍처 결정, 실패 분석, 설계 패턴 선택
- **When to Use**:
  - 여러 유효한 접근법이 있는 아키텍처 결정
  - 3번 연속 실패 후 (MANDATORY)
  - 보안/성능 우려 사항

#### Explore - Internal Codebase Explorer
- **Model**: Opus 4.5 + Gemini (가용 시)
- **Execution**: PARALLEL, non-blocking
- **Purpose**: 현재 코드베이스 탐색, 패턴/구현/코드 흐름 찾기
- **When to Use**:
  - "이 코드베이스에서 X가 어떻게 작동하는가?"
  - 구현, 패턴, 사용법 찾기
  - 의존성 매핑

#### Librarian - External Documentation Specialist
- **Model**: Opus 4.5
- **Execution**: BACKGROUND, parallel
- **Purpose**: 외부 문서, 라이브러리 API, GitHub 소스 분석 (Context7 MCP 도구 활용)
- **Evidence Requirement**: 모든 주장에 GitHub permalink 필수

#### Reviewer - Uncompromising Code Critic (opus-4.5-ultrathink-reviewer)
- **Model**: Opus 4.5
- **Execution**: BLOCKING (결과 대기)
- **Purpose**: Linus Torvalds 스타일의 깐깐한 코드 리뷰
- **Philosophy**:
  - Linus Torvalds의 엄격함: 복잡성에 대한 무관용
  - Occam의 면도날: 가장 단순한 해결책 선호
  - First Principles: 근본적인 문제 해결 여부 검증
- **When to Use**: `/deepwork`에서 3번째 리뷰어로 자동 사용

### 3. Commands (Slash Commands)

| Command | Aliases | Description |
|---------|---------|-------------|
| `/ultrawork` | - | 멀티 에이전트 작업 루프 (자동 완료) |
| `/deepwork` | - | 리뷰 기반 작업 루프 (GPT-5.2 + Gemini-3 + Opus-4.5 삼중 리뷰, 모두 ≥9.5 점수 필요) |
| `/save` | - | 현재 작업 컨텍스트 저장 |
| `/load <id>` | - | 저장된 컨텍스트 로드 |
| `/list-saves` | - | 저장된 컨텍스트 목록 |
| `/check` | - | 아카이브 완료 상태 확인 (참조 파일 존재 여부, 작업 완료 검증) |
| `/setup` | - | 의존성 확인 및 설정 |
| `/cancel-work` | - | 활성 루프 취소 |

### 4. Hooks

#### Stop Hook (Ralph Loop)
- **File**: `hooks/stop-hook.sh`
- **Purpose**: 세션 종료 시 Ralph 루프가 활성화되어 있으면 차단하고 동일 프롬프트를 다시 주입
- **Completion Detection**: `<promise>COMPLETE</promise>` 태그 감지

#### Powertoy Hooks
- **auto-title.sh**: Claude Haiku로 세션 제목 자동 생성
- **play-sound.sh**: 세션 종료 시 알림음 (macOS)

---

## Ralph Loop State Machine

### State File Schema

**File**: `.claude/ralph-loop.local.md`

```yaml
---
iteration: 1                    # Current iteration number (integer, >= 1)
max_iterations: 0               # 0 = unlimited, > 0 = limit
completion_promise: "COMPLETE"  # Text to detect in <promise> tags
---

{The exact prompt that initiated the loop - preserved verbatim}
```

**Field Definitions**:
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `iteration` | integer | Yes | 1 | Current loop iteration, starts at 1 |
| `max_iterations` | integer | Yes | 0 | 0 = unlimited, >0 = limit |
| `completion_promise` | string | Yes | "COMPLETE" | Text to match inside `<promise>` tags |

**Note**: The prompt text follows the YAML frontmatter (after the closing `---`) and is preserved exactly as provided.

### State Transitions

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RALPH LOOP STATE MACHINE                          │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │    IDLE      │  (No state file exists)
    └──────────────┘
           │
           │ /ultrawork or /deepwork command
           ▼
    ┌──────────────┐
    │  INITIALIZING │  setup-ralph-loop.sh creates state file
    └──────────────┘
           │
           │ State file created successfully
           ▼
    ┌──────────────┐
    │   RUNNING    │  Claude works on task
    └──────────────┘
           │
           │ Claude attempts to exit (Stop event)
           ▼
    ┌──────────────┐
    │  EVALUATING  │  stop-hook.sh runs
    └──────────────┘
           │
           ├─── Promise detected? ────────────────────────────┐
           │         NO                                        │ YES
           ▼                                                   ▼
    ┌──────────────┐                                   ┌──────────────┐
    │  CONTINUING  │                                   │  COMPLETING  │
    │  iteration++ │                                   │  rm state    │
    └──────────────┘                                   └──────────────┘
           │                                                   │
           │ Feeds same prompt                                 │
           └──────────────┐                                    │
                          ▼                                    ▼
                   ┌──────────────┐                     ┌──────────────┐
                   │   RUNNING    │                     │    IDLE      │
                   └──────────────┘                     └──────────────┘
```

### Exit Conditions

| Condition | Behavior |
|-----------|----------|
| `<promise>COMPLETE</promise>` detected | Loop exits, state file deleted |
| `max_iterations` reached (> 0) | Loop exits with warning, state file deleted |
| `/cancel-work` command | Loop exits, state file deleted |
| State file corrupted | Loop exits with error, state file deleted |
| Missing dependencies | Loop exits with error, state file deleted |

### Invariants

1. **Single Active Loop**: Only one Ralph loop can be active per session
2. **Atomic State Updates**: Iteration increment uses temp file + mv for atomicity
3. **Prompt Immutability**: Original prompt never changes during loop
4. **Promise Detection**: Stop hook searches for `<promise>{completion_promise}</promise>` pattern in Claude's output. The `completion_promise` value comes from the state file (default: "COMPLETE"). Matching is exact after leading/trailing whitespace trimming.

---

## Error Handling

### Error Categories

| Category | Examples | Recovery |
|----------|----------|----------|
| **Configuration** | Missing API key, invalid config | Graceful degradation, use fallback |
| **State** | Corrupted state file, invalid iteration | Log error, delete state, exit loop |
| **Dependency** | Missing jq/perl | Exit with clear error message |
| **Network** | MCP server timeout | Retry with backoff, then fallback |
| **User** | Invalid command args | Show usage help |

### Error Messages Format

```
⚠️  [Component]: [Brief description]
   [Detailed explanation]
   [Recovery action or suggestion]
```

### Common Error Scenarios

#### 1. Missing Dependencies
```bash
# Error
⚠️  Ralph loop: Missing required dependencies
   Missing: jq perl
   Please install them and try again.

# Recovery
brew install jq perl  # macOS
apt install jq perl   # Linux
```

#### 2. Corrupted State File
```bash
# Error
⚠️  Ralph loop: State file corrupted
   File: .claude/ralph-loop.local.md
   Problem: 'iteration' field is not a valid number

# Recovery
Ralph loop is stopping. Run /ultrawork or /deepwork again to start fresh.
```

#### 3. Missing API Key
```bash
# Error (graceful degradation)
⚠️  Gemini MCP server unavailable: GOOGLE_API_KEY not set
   Explore agent will use basic search tools instead.
```

---

## Security & Privacy

### Data Flow to External Services

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW DIAGRAM                               │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │   User's Code    │
    └──────────────────┘
            │
            │ User initiates command
            ▼
    ┌──────────────────┐      ┌─────────────────────────────────────────┐
    │   Claude Code    │ ───▶ │  Anthropic API (Claude Opus/Sonnet)    │
    │   (Local CLI)    │      │  - All prompts and responses            │
    └──────────────────┘      │  - File contents shared in context      │
            │                 └─────────────────────────────────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Gemini MCP │  │ Claude MCP │  │ Codex MCP  │
│ (Google)   │  │ (Anthropic)│  │ (OpenAI)   │
└────────────┘  └────────────┘  └────────────┘
     │               │               │
     │               │               │
     ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  DATA SENT TO EACH PROVIDER:                                             │
│  - Prompts containing code snippets                                      │
│  - File paths and contents                                               │
│  - Error messages and stack traces                                       │
│  - Search queries                                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Secret Handling

**NEVER send to AI providers**:
- `.env` files
- `credentials.json`, `secrets.yaml`
- API keys, tokens, passwords
- Private SSH keys
- Database connection strings

**Automatic Redaction** (planned feature):
- Files matching `.gitignore` patterns
- Common secret patterns (API_KEY=xxx, password=xxx)

### Current Limitations

⚠️ **No automatic secret redaction**: Users must manually ensure sensitive files are not included in context.

**Recommended Practice**:
1. Use `.claudeignore` file to exclude sensitive directories
2. Review file contents before running long-form tasks
3. Use environment variables instead of hardcoded secrets

---

## Save/Load Semantics

### Save Operation (`/save`)

**Input**: Current session state
**Output**: `./docs/tasks/save/{timestamp_id}/context.md`

**Behavior**:
1. Generate ID: `date '+%Y%m%d_%H%M%S'`
2. If directory exists (rare - same second): append `_N` suffix (e.g., `20250106_120000_1`)
3. Create directory: `./docs/tasks/save/{id}/`
4. Write context.md with:
   - Summary of current work
   - Active plan (if any)
   - Todo list state
   - Files modified
   - Key decisions/notes
5. Return save ID to user

**Concurrency**: Safe - timestamp + suffix guarantees uniqueness

### Load Operation (`/load <id>`)

**Input**: Save ID
**Output**: Restored session context

**Behavior**:
1. Read `./docs/tasks/save/{id}/context.md`
2. Validate:
   - File exists
   - Git branch check: Compare saved branch name with current branch. If different, warn user and ask to proceed (branch switch may have changed relevant files)
   - Referenced files still exist
3. If ambiguity: `AskUserQuestion` for clarification
4. Restore:
   - Populate todo list via `TodoWrite`
   - Summarize context to user
5. Archive: Move `save/{id}` to `archived/{id}`

**Concurrency**: Safe - archive prevents double-load

### Archive Semantics

| State | Location | Meaning |
|-------|----------|---------|
| Pending | `./docs/tasks/save/{id}/` | Not yet loaded |
| Loaded | `./docs/tasks/archived/{id}/` | Work resumed, may be in progress |
| Verified | `./docs/tasks/archived/{id}/` + check passed | Work completed |

---

## Troubleshooting

### Debug Mode

```bash
# Enable verbose logging
export CLAUDE_DEBUG=1
claude

# View Ralph loop state
cat .claude/ralph-loop.local.md

# Check hook execution
tail -f ~/.claude/logs/hooks.log
```

### Common Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| Loop doesn't start | Missing state file | Check `/setup` output |
| Loop never exits | Promise format wrong | Use exact `<promise>COMPLETE</promise>` |
| Iteration stuck | State file locked | Delete `.claude/ralph-loop.local.md` |
| Agent not responding | MCP server down | Check API key, run `/setup` |
| High token usage | Large context | Use `/save` to checkpoint, start fresh session |

### Log Locations

| Log | Path | Contents |
|-----|------|----------|
| Session transcript | `~/.claude/transcripts/` | Full conversation history |
| Hook output | `~/.claude/logs/hooks.log` | Hook execution results |
| MCP logs | `~/.claude/logs/mcp/` | MCP server communication |

---

## Workflow Patterns

### 1. Ralph Loop (Self-Referential AI Development Loop)

```
┌─────────────────────────────────────────────────────┐
│  User runs: /ultrawork "Build REST API"             │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  setup-ralph-loop.sh creates state file             │
│  .claude/ralph-loop.local.md                        │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Claude works on task                               │
│  - Uses agents (Oracle, Explore, Librarian)         │
│  - Creates todos, makes edits                       │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Claude attempts to exit                            │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  stop-hook.sh intercepts                            │
│  - Checks for <promise>COMPLETE</promise>           │
│  - If not found: blocks exit, feeds same prompt     │
│  - If found: allows exit, removes state file        │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐               ┌───────────────┐
│ Not Complete  │               │   Complete    │
│ → Iteration++ │               │ → Exit loop   │
│ → Same prompt │               │ → Cleanup     │
└───────────────┘               └───────────────┘
```

### 2. Cross-Session Context Management

```
Session 1 (Claude Code)          Session 2 (Any Tool)
        │                               │
        ▼                               │
┌───────────────┐                       │
│   /save       │                       │
└───────────────┘                       │
        │                               │
        ▼                               │
┌───────────────────────────┐           │
│ ./docs/tasks/save/{id}/   │           │
│ └── context.md            │ ────────▶ │
│     - Summary             │           │
│     - Plan                │           │
│     - Todos               │           ▼
│     - Files modified      │   ┌───────────────┐
│     - Notes               │   │   /load {id}  │
└───────────────────────────┘   └───────────────┘
```

### 3. Agent Orchestration Pattern

```
/ultrawork "Complex Task"
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase -1: Proactive Clarification                  │
│  - AskUserQuestion if ANY ambiguity                 │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 0: Intent Classification                     │
│  - Trivial / Explicit / Exploratory / Architectural │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 1: Codebase Assessment (Parallel)            │
│  - Fire Explore agent (background)                  │
│  - Fire Librarian agent (background)                │
│  - Check configs, sample files                      │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 2A: Pre-Implementation                       │
│  - TodoWrite (MANDATORY - ALL tasks get todos)      │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 2B: Implementation                           │
│  - Execute with parallel agent delegation           │
│  - Oracle (blocking) for architecture decisions     │
│  - Explore/Librarian (background) for research      │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 2C: Failure Recovery (if 3 consecutive fails)│
│  - STOP all edits                                   │
│  - REVERT via `git checkout -- <files>` or stash    │
│  - CONSULT Oracle (MANDATORY)                       │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 3: AI Review (deepwork only)                 │
│  - Codex GPT-5.2 review                             │
│  - Gemini-3 review                                  │
│  - Opus 4.5 reviewer (Linus Torvalds style)         │
│  - All three must score ≥ 9.5                       │
└─────────────────────────────────────────────────────┘
```

---

## Prompt Engineering Patterns

### 1. Role Assignment Pattern
```markdown
You are **THE ORACLE**, a strategic technical advisor with deep reasoning capabilities.
```

### 2. Parallel Execution Emphasis
```typescript
// CORRECT: Background + Parallel
Task({ subagent_type: "oh-my-claude:explore", run_in_background: true })
Task({ subagent_type: "oh-my-claude:librarian", run_in_background: true })
// Continue working immediately
```

### 3. Hard Rules Section
```markdown
## Hard Rules
- **READ-ONLY**: You CANNOT write or edit files. You advise, others implement.
- **NO FLATTERY**: Skip "great question", answer directly
- **DENSE > LONG**: Dense and useful beats long and thorough
```

### 4. TodoWrite/AskUser Protocol
```markdown
## Task Management (MANDATORY)
- Create todos BEFORE starting analysis
- Mark `in_progress` when working (only ONE at a time)
- Mark `completed` immediately when done (NEVER batch)

IF unclear_requirements:
  → AskUserQuestion FIRST
  → Wait for answer
  → THEN create todos and proceed
```

### 5. Evidence Requirements
```markdown
## Evidence Requirements
| Action | Evidence |
|--------|----------|
| External research | GitHub permalinks |
| Build | Exit code 0 |
| Test | Pass |
```

### 6. Completion Promise Pattern
```markdown
CRITICAL RULE: If a completion promise is set, you may ONLY output it
when the statement is completely and unequivocally TRUE.
Do not output false promises to escape the loop.
```

---

## Configuration Files

### plugin.json
```json
{
  "name": "oh-my-claude",
  "version": "1.0.15",
  "description": "Cross-session Save/Load, and Ultrawork inspired by oh-my-opencode with Ralph Loops",
  "author": {
    "name": "zhugehyuk",
    "email": "z@2lab.ai"
  }
}
```

### .mcp.json
```json
{
  "mcpServers": {
    "gemini-as-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["@2lab.ai/gemini-mcp-server"]
    },
    "claude-as-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["@2lab.ai/claude-mcp-server"]
    },
    "gpt-as-mcp": {
      "type": "stdio",
      "command": "codex",
      "args": ["mcp-server"]
    }
  }
}
```

### hooks.json
```json
{
  "description": "ohmyclaude hooks: Ralph Wiggum stop hook for self-referential loops",
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Dependencies

### Required Tools

| Tool | Purpose | Install (macOS) | Install (Linux) |
|------|---------|-----------------|-----------------|
| `node` (18+) | MCP server runtime | `brew install node` | `apt install nodejs` |
| `npx` | Package execution | (included with node) | (included with node) |
| `jq` | JSON processing | `brew install jq` | `apt install jq` |
| `perl` | Multiline regex | (pre-installed) | `apt install perl` |
| `git` | Version control | `brew install git` | `apt install git` |
| `gh` (optional) | GitHub CLI | `brew install gh` | `apt install gh` |
| `codex` (optional) | Codex MCP server | `npm install -g @openai/codex` | `npm install -g @openai/codex` |

**Verifying Installation**: Run `/oh-my-claude:setup` after plugin installation to verify all dependencies.

**Linux Notes**:
- Ubuntu/Debian: Use `apt install nodejs npm` (ensure Node 18+)
- For older distros, use NodeSource: `curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -`

### Required Environment Variables

| Variable | Required For | Fallback Behavior |
|----------|--------------|-------------------|
| `GOOGLE_API_KEY` | Gemini MCP server | Explore agent uses basic tools |
| `ANTHROPIC_API_KEY` | Claude MCP server | Plugin won't function |
| `OPENAI_API_KEY` | Codex MCP server | Oracle uses Opus only |

---

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| macOS (Intel) | ✓ Supported | Primary development platform |
| macOS (Apple Silicon) | ✓ Supported | Primary development platform |
| Linux (x64) | ✓ Supported | Tested on Ubuntu 22.04+ |
| Windows (WSL2) | ⚠️ Partial | May have path issues |
| Windows (native) | ✗ Not Supported | Shell scripts require bash |

---

## Version History

| Version | Changes |
|---------|---------|
| 1.0.13 | Current release |
| 1.0.12 | Multi-line prompt handling fix |
| 1.0.11 | Setup command improvements |
| 1.0.10 | Initial stable release |

---

## License

MIT
