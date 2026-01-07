# oh-my-claude Plugin Analysis Report

> **Plugin Version**: 1.0.23
> **Source Commit**: d4b3f79
> **Generated**: 2026-01-07
> **Author**: Claude Opus 4.5 Analysis

---

## Quick Start

Before diving into the architecture, ensure you have the prerequisites:

```bash
# Install dependencies (macOS)
brew install node gh jq
brew install --cask codex
brew install gemini-cli

# Authenticate services
codex login       # OpenAI/Codex authentication
gh auth login     # GitHub CLI authentication
# Gemini: Set GOOGLE_API_KEY or follow gemini-cli auth prompts

# Verify setup (run in Claude Code)
/oh-my-claude:setup
```

See [Section 11: Installation & Safety](#11-installation--safety) for complete setup details.

---

## Executive Summary

**oh-my-claude** is a sophisticated Claude Code plugin that implements a multi-agent work coordination system with self-referential development loops (Ralph Loops), cross-session state persistence, and automated quality gates.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Ralph Loops** | Self-referential work loops that iterate until completion |
| **Multi-Agent System** | 5 specialized agents (Oracle, Explore, Librarian, Reviewer, Orchestrator) |
| **Multi-Model Integration** | GPT-5.2, Gemini-3, Claude Opus via MCP servers |
| **Work Persistence** | Save/Load context across sessions |
| **Quality Gates** | Triple AI review with ≥9.5/10 threshold |

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Plugin Structure](#2-plugin-structure)
3. [Agent System](#3-agent-system)
4. [Command Registry](#4-command-registry)
5. [MCP Server Integration](#5-mcp-server-integration)
6. [Workflow Patterns](#6-workflow-patterns)
7. [Ralph Loop System](#7-ralph-loop-system)
8. [Quality Assurance](#8-quality-assurance)
9. [Key Design Patterns](#9-key-design-patterns)
10. [Technical Specifications](#10-technical-specifications)
11. [Installation & Safety](#11-installation--safety)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         oh-my-claude Plugin                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐           │
│  │   Commands    │    │    Agents     │    │  MCP Servers  │           │
│  │  (14 total)   │────│   (5 total)   │────│   (3 total)   │           │
│  └───────────────┘    └───────────────┘    └───────────────┘           │
│          │                   │                    │                     │
│          │                   │                    │                     │
│          ▼                   ▼                    ▼                     │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │                   Ralph Loop Engine                      │           │
│  │  ┌──────────────────────────────────────────────────┐   │           │
│  │  │  State File: .claude/ralph-loop.local.md         │   │           │
│  │  │  - iteration: N                                   │   │           │
│  │  │  - max_iterations: M                              │   │           │
│  │  │  - completion_promise: "TEXT"                     │   │           │
│  │  └──────────────────────────────────────────────────┘   │           │
│  └─────────────────────────────────────────────────────────┘           │
│          │                                                              │
│          ▼                                                              │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │                   Stop Hook (hooks.json)                 │           │
│  │  - Intercepts session exit                              │           │
│  │  - Feeds output back as input                           │           │
│  │  - Increments iteration counter                          │           │
│  │  - Checks completion promise                             │           │
│  └─────────────────────────────────────────────────────────┘           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Core Philosophy

> "Your code should be indistinguishable from a senior engineer's."

The plugin operates on these principles:
1. **Never work alone** - Always delegate to specialized agents
2. **Ask first** - Clarify requirements before acting
3. **Track everything** - Mandatory TodoWrite for all work
4. **Quality gates** - Triple AI review before completion
5. **Evidence-based** - GitHub permalinks for all claims

---

## 2. Plugin Structure

```
plugins/oh-my-claude/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata (v1.0.23)
├── .mcp.json                    # MCP server definitions
│
├── commands/                    # 14 command definitions
│   ├── deepwork.md             # Ralph loop + triple review
│   ├── ultrawork.md            # Ralph loop + optional review
│   ├── orchestrator.md         # Multi-agent coordinator
│   ├── explore.md              # Codebase search
│   ├── oracle.md               # Architecture advisor
│   ├── librarian.md            # External docs expert
│   ├── save.md                 # Save work context
│   ├── load.md                 # Load saved context
│   ├── status.md               # Ralph loop status
│   ├── check.md                # Verify archived saves
│   ├── list-saves.md           # List all saves
│   ├── cancel-work.md          # Stop Ralph loop
│   ├── setup.md                # Install dependencies
│   └── pr-summary.md           # PR executive summary
│
├── .commands-body/              # Command execution bodies
│   └── [matching .md files]    # Loaded via @include()
│
├── agents/                      # 5 agent definitions
│   ├── orchestrator.md         # Central coordinator
│   ├── oracle.md               # GPT-5.2 advisor
│   ├── explore.md              # Gemini searcher
│   ├── librarian.md            # Docs specialist
│   └── reviewer.md             # Quality gate
│
├── prompts/                     # Agent personas
│   ├── orchestrator-workflow.md
│   ├── oracle-persona.md
│   ├── explore-persona.md
│   ├── librarian-persona.md
│   └── reviewer-persona.md
│
├── scripts/
│   └── setup-ralph-loop.sh     # Ralph loop initializer
│
└── hooks/
    ├── hooks.json              # Hook registration
    └── stop-hook.sh            # Loop continuation hook
```

---

## 3. Agent System

### Agent Overview

| Agent | Model | Execution | Color | Purpose |
|-------|-------|-----------|-------|---------|
| **Orchestrator** | Opus | Autonomous | #FF6B35 | Multi-agent coordination |
| **Oracle** | Opus/GPT-5.2 | BLOCKING | #FFD700 | Architecture decisions |
| **Explore** | Opus/Gemini | PARALLEL | #00CED1 | Internal codebase search |
| **Librarian** | Opus | PARALLEL | #9370DB | External documentation |
| **Reviewer** | Opus | BLOCKING | #DC143C | Quality gate |

### 3.1 Oracle Agent

**Role**: Strategic Technical Advisor

**Invocation**: `subagent_type: "oh-my-claude:oracle"`

**When to Use**:
- Architecture decisions with multiple valid approaches
- After 3 consecutive failures (MANDATORY)
- Design pattern selection
- Security/performance concerns

**Tools**: Read, Grep, Glob, WebSearch, WebFetch, TodoWrite, AskUserQuestion, GPT-5.2 Codex

**Framework**:
- Bias toward simplicity
- Leverage existing code
- One clear path recommendation
- Effort signals: Quick(<1h) / Short(1-4h) / Medium(1-2d) / Large(3d+)

**Response Structure**:
```
- Bottom line (2-3 sentences)
- Action plan (numbered steps)
- Effort estimate
- Why this approach (when relevant)
- Watch out for (risks)
```

### 3.2 Explore Agent

**Role**: Internal Codebase Explorer

**Invocation**: `subagent_type: "oh-my-claude:explore"`

**When to Use**:
- "How does X work in THIS codebase?"
- Finding implementations
- Understanding patterns
- Mapping code flow

**Tools**: Read, Grep, Glob, TodoWrite, AskUserQuestion, Gemini MCP

**Protocol**:
1. Fire multiple searches in parallel
2. Use Gemini for complex questions
3. Report with file:line references

**Key Rules**:
- INTERNAL ONLY (this codebase)
- PARALLEL FIRST (fire multiple, don't wait)
- SPECIFIC LOCATIONS (always file:line)
- FAST (like grep, not a consultant)

### 3.3 Librarian Agent

**Role**: External Documentation Specialist

**Invocation**: `subagent_type: "oh-my-claude:librarian"`

**When to Use**:
- "How do I use [library]?"
- Best practices for frameworks
- GitHub source analysis
- Library API questions

**Tools**: Read, Grep, Glob, Bash, WebSearch, WebFetch, TodoWrite, AskUserQuestion, Context7

**Request Types**:

| Type | Trigger | Min Calls |
|------|---------|-----------|
| TYPE A: Conceptual | "How do I...", "Best practice..." | 3+ |
| TYPE B: Implementation | "Show me source of..." | 4+ |
| TYPE C: Context | "Why was this changed?" | 4+ |
| TYPE D: Comprehensive | Complex, deep dive | 6+ |

**Critical Rule**: ALWAYS provide GitHub permalinks as evidence

### 3.4 Reviewer Agent

**Role**: Uncompromising Code Critic (Linus Torvalds style)

**Invocation**: `subagent_type: "oh-my-claude:reviewer"`

**Tools**: Read, Grep, Glob (read-only)

**Three Principles**:
1. **Linus Torvalds' Rigor** - Zero tolerance for unjustified complexity
2. **Occam's Razor** - Simplest solution that works
3. **First Principles** - Question every assumption

**Scoring**:
| Score | Meaning |
|-------|---------|
| 0-2 | Fundamentally broken |
| 3-4 | Major issues |
| 5-6 | Works but has problems |
| 7-8 | Good with improvements |
| 9.0-9.4 | Minor fixes needed |
| 9.5-10 | **Production-ready** |

**Must Reject** (Score < 5.0):
- Over-engineered solutions
- Premature abstractions
- "Clever" code
- Security vulnerabilities
- Dead code

### 3.5 Orchestrator Agent

**Role**: Central Multi-Agent Coordinator

**Invocation**: `subagent_type: "oh-my-claude:orchestrator"`

**Tools**: All tools + all MCP servers

**Key Difference**: When run as subagent, NO AskUserQuestion available

**Workflow Phases**:
1. Phase -1: Proactive clarification
2. Phase 0: Intent gate (classify request)
3. Phase 1: Codebase assessment
4. Phase 2A: Pre-implementation (TodoWrite)
5. Phase 2B: Implementation (agent delegation)
6. Phase 2C: Failure recovery

---

## 4. Command Registry

### Work Execution Commands

#### `/deepwork`
- **Purpose**: Ralph loop with mandatory triple AI review
- **Arguments**: `[--max-iterations N] [--completion-promise TEXT] PROMPT`
- **Review Gate**: ALL THREE must score ≥9.5/10
- **Exit**: `<promise>COMPLETE</promise>` when all conditions met

#### `/ultrawork`
- **Purpose**: Ralph loop with optional review
- **Arguments**: `[--max-iterations N] [--completion-promise TEXT] PROMPT`
- **Review Gate**: Optional (gated by AskUserQuestion)
- **Exit**: `<promise>COMPLETE</promise>`

### Agent Commands

| Command | Agent | Description |
|---------|-------|-------------|
| `/orchestrator` | Orchestrator | Multi-agent coordinator (current context) |
| `/explore` | Explore | Internal codebase search |
| `/oracle` | Oracle | Architecture advice |
| `/librarian` | Librarian | External documentation |

### State Management Commands

| Command | Purpose |
|---------|---------|
| `/save` | Save work context to `./docs/tasks/save/{id}/` |
| `/load` | Load saved context (validates, archives) |
| `/status` | Show Ralph loop progress |
| `/cancel-work` | Stop active Ralph loop |
| `/list-saves` | List available saves |
| `/check` | Verify archived task completion |

### Utility Commands

| Command | Purpose |
|---------|---------|
| `/setup` | Install dependencies (codex, gemini-cli) |
| `/pr-summary` | Generate multi-stakeholder PR summary |

---

## 5. MCP Server Integration

### Server Definitions

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

### Tool Naming Convention

Pattern: `mcp__plugin_ohmyclaude_<server>__<tool>`

| Tool | Purpose |
|------|---------|
| `mcp__plugin_ohmyclaude_gemini-as-mcp__gemini` | Start Gemini session |
| `mcp__plugin_ohmyclaude_gemini-as-mcp__gemini-reply` | Continue Gemini session |
| `mcp__plugin_ohmyclaude_claude-as-mcp__chat` | Start Claude session |
| `mcp__plugin_ohmyclaude_claude-as-mcp__chat-reply` | Continue Claude session |
| `mcp__plugin_ohmyclaude_gpt-as-mcp__codex` | Start GPT-5.2 session |
| `mcp__plugin_ohmyclaude_gpt-as-mcp__codex-reply` | Continue GPT session |
| `mcp__plugin_context7_context7__resolve-library-id` | Resolve library ID |
| `mcp__plugin_context7_context7__query-docs` | Query documentation |

### Agent-Server Mapping

| Agent | Primary Server | Use Case |
|-------|---------------|----------|
| Oracle | GPT-5.2 (Codex) | Deep reasoning, architecture |
| Explore | Gemini | Fast parallel search |
| Librarian | Context7 | Documentation queries |
| Orchestrator | All three | Multi-model coordination |
| Reviewer | None (read-only) | Code analysis only |

---

## 6. Workflow Patterns

### 6.1 Orchestrator Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    EXECUTION ORDER                          │
├─────────────────────────────────────────────────────────────┤
│ 1. Unclear? → AskUserQuestion (FIRST!)                      │
│ 2. Clear   → TodoWrite (create ALL steps)                   │
│ 3. Work    → Mark in_progress → Do → Mark completed         │
├─────────────────────────────────────────────────────────────┤
│                    AGENT SELECTION                          │
├─────────────────────────────────────────────────────────────┤
│ Internal code?           → oh-my-claude:explore (background)│
│ "How to use X?"          → oh-my-claude:librarian TYPE A    │
│ "Show source of X"       → oh-my-claude:librarian TYPE B    │
│ Architecture?            → oh-my-claude:oracle (blocking)   │
│ Stuck 3x?                → oh-my-claude:oracle (MANDATORY)  │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Parallel vs Blocking Execution

**PARALLEL (Fire and Continue)**:
```typescript
Task({
  subagent_type: "oh-my-claude:explore",
  prompt: "Find auth patterns...",
  run_in_background: true
})
// Continue working immediately
// Collect later: TaskOutput(task_id="...")
```

**BLOCKING (Wait for Response)**:
```typescript
Task({
  subagent_type: "oh-my-claude:oracle",
  prompt: "Review architecture decision..."
})
// Waits for Oracle response before continuing
```

### 6.3 Failure Recovery

After 3 consecutive failures:
1. **STOP** all edits
2. **REVERT** to last working state
3. **DOCUMENT** what was attempted
4. **CONSULT ORACLE** (MANDATORY)
5. If Oracle fails → **ASK USER**

---

## 7. Ralph Loop System

### Concept

Ralph Loops create self-referential development iterations where Claude's output is fed back as the next input, enabling autonomous refinement until a completion condition is met.

### State File Format

```markdown
---
active: true
iteration: 1
max_iterations: 0
completion_promise: "COMPLETE"
started_at: "2026-01-07T12:00:00Z"
---

[Original prompt text...]
```

### Loop Flow

```
┌────────────────────────────────────────────────────────────────────┐
│                         Ralph Loop Flow                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  [1. Setup]              [2. Work]              [3. Exit Check]    │
│  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐     │
│  │ Create      │        │ Claude      │        │ Stop Hook   │     │
│  │ State File  │───────►│ Executes    │───────►│ Triggered   │     │
│  └─────────────┘        └─────────────┘        └─────────────┘     │
│                                                       │             │
│                              ┌────────────────────────┼─────────┐   │
│                              │                        │         │   │
│                              ▼                        ▼         │   │
│                     ┌─────────────┐         ┌─────────────┐     │   │
│                     │ Promise     │   YES   │ Max Iter    │     │   │
│                     │ Found?      │────────►│ Reached?    │     │   │
│                     └─────────────┘         └─────────────┘     │   │
│                              │                   │    │         │   │
│                           NO │                NO │ YES│         │   │
│                              │                   │    │         │   │
│                              ▼                   ▼    ▼         │   │
│                     ┌─────────────┐         ┌─────────────┐     │   │
│                     │ Increment   │         │    EXIT     │     │   │
│                     │ Iteration   │         │    LOOP     │     │   │
│                     └─────────────┘         └─────────────┘     │   │
│                              │                                      │
│                              └──────────────────────────────────────┘
│                                         (Re-feed prompt)            │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Stop Hook Logic

```bash
# Pseudocode
if [ ! -f ".claude/ralph-loop.local.md" ]; then
    exit 0  # No loop, allow exit
fi

if [ $iteration -ge $max_iterations ] && [ $max_iterations -gt 0 ]; then
    rm ".claude/ralph-loop.local.md"
    exit 0  # Max reached, allow exit
fi

if output_contains "<promise>$COMPLETION_PROMISE</promise>"; then
    rm ".claude/ralph-loop.local.md"
    exit 0  # Promise fulfilled, allow exit
fi

# Block exit, re-feed prompt
echo '{"decision": "block", "reason": "$PROMPT"}'
```

---

## 8. Quality Assurance

### Triple Review Gate (deepwork)

```
╔══════════════════════════════════════════════════════════════════╗
║                    TRIPLE REVIEW PROTOCOL                        ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           ║
║  │   GPT-5.2    │  │  Gemini-3    │  │  Opus-4.5    │           ║
║  │   (Codex)    │  │   (Preview)  │  │  (Reviewer)  │           ║
║  │              │  │              │  │              │           ║
║  │ xhigh effort │  │   parallel   │  │  subagent    │           ║
║  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           ║
║         │                 │                 │                    ║
║         ▼                 ▼                 ▼                    ║
║      Score 1           Score 2           Score 3                 ║
║         │                 │                 │                    ║
║         └────────────────┼────────────────┘                     ║
║                          │                                       ║
║                          ▼                                       ║
║                 ┌─────────────────┐                              ║
║                 │  ALL ≥ 9.5/10?  │                              ║
║                 └─────────────────┘                              ║
║                    │           │                                 ║
║                  YES         NO                                  ║
║                    │           │                                 ║
║                    ▼           ▼                                 ║
║               ┌────────┐  ┌────────────┐                         ║
║               │ PASS   │  │ FIX ISSUES │                         ║
║               └────────┘  │ RE-REVIEW  │                         ║
║                           └────────────┘                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### Completion Criteria

- [ ] Task is genuinely complete
- [ ] All todos marked complete
- [ ] Code works (build passes, tests pass)
- [ ] No broken functionality
- [ ] GPT-5.2 reviewer score ≥ 9.5/10
- [ ] Gemini-3 reviewer score ≥ 9.5/10
- [ ] Opus-4.5 reviewer score ≥ 9.5/10
- [ ] Agent/MCP Call Report output

### Call Tracking Protocol

Every agent/MCP call must be logged:

```
⏱️ #{seq} {agent_or_mcp} | {description} | ~{duration}s | {status}
```

**Status Values**: `ok` | `error` | `timeout` | `cancelled`

**Final Report Format**:
```markdown
═══════════════════════════════════════════════════════════
                    AGENT/MCP CALL REPORT
═══════════════════════════════════════════════════════════

## Summary
- Total calls: {count}
- Successful: {success_count} | Failed: {error_count}
- Sum of durations: ~{total}s
- Longest call: {type} (~{duration}s)

## Breakdown by Type
| Type | Calls | Sum Duration | Success |
|------|-------|--------------|---------|
| oh-my-claude:explore | 3 | ~180s | 3/3 |
| oh-my-claude:oracle | 1 | ~120s | 1/1 |
...
```

---

## 9. Key Design Patterns

### 9.1 Command-Body Separation

```
commands/deepwork.md          # Metadata + @include
  └─ @include(${CLAUDE_PLUGIN_ROOT}/.commands-body/deepwork.md)
     └─ .commands-body/deepwork.md  # Actual content
```

**Benefit**: Token optimization - metadata cached, body loaded on demand

### 9.2 Persona Injection

```
agents/explore.md             # Agent definition
  └─ @include(${CLAUDE_PLUGIN_ROOT}/prompts/explore-persona.md)
     └─ prompts/explore-persona.md  # Behavior definition
```

**Benefit**: Shared personas, consistency, easy updates

### 9.3 State File Pattern

```
.claude/ralph-loop.local.md
├── YAML frontmatter (configuration)
└── Body (prompt text)
```

**Benefit**: Human-readable, git-ignorable (.local), structured

### 9.4 Hook-Based Loop Control

```
hooks.json → Stop event → stop-hook.sh
  └─ Intercept exit
  └─ Parse transcript
  └─ Re-inject prompt
```

**Benefit**: Non-invasive loop continuation

### 9.5 Multi-Model Delegation

```
Orchestrator
├─ Explore (Gemini) - Fast search
├─ Oracle (GPT-5.2) - Deep reasoning
└─ Librarian (Opus) - Documentation
```

**Benefit**: Specialized models for specialized tasks

---

## 10. Technical Specifications

### File Statistics

| Category | Count | Notes |
|----------|-------|-------|
| Commands | 14 | In `/commands/` |
| Command Bodies | 14 | In `/.commands-body/` |
| Agents | 5 | In `/agents/` |
| Prompts | 5 | In `/prompts/` |
| Scripts | 1 | Ralph loop setup |
| Hooks | 1 | Stop hook |
| Config Files | 3 | plugin.json, .mcp.json, hooks.json |

### Dependencies

- **Codex CLI**: For GPT-5.2 access (`codex mcp-server`)
- **Gemini CLI**: For Gemini access (`@2lab.ai/gemini-mcp-server`)
- **Claude MCP**: For Claude access (`@2lab.ai/claude-mcp-server`)
- **Context7**: For library documentation
- **jq, perl, sed, awk**: For stop-hook.sh parsing

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `CLAUDE_PLUGIN_ROOT` | Plugin installation path |
| `RALPH_PROMPT_B64` | Base64-encoded prompt for cross-platform safety |
| `RALPH_NO_DEFAULT_PROMISE` | Disable default completion promise |

### File Locations

| File | Purpose |
|------|---------|
| `.claude/ralph-loop.local.md` | Active Ralph loop state |
| `./docs/tasks/save/{id}/context.md` | Saved work contexts |
| `./docs/tasks/archived/{id}/` | Archived (loaded) saves |
| `./docs/pr-summary/{id}.md` | Generated PR summaries |

---

## 11. Installation & Safety

### Prerequisites

| Dependency | Required For | Installation |
|------------|--------------|--------------|
| **Node.js + npm** | MCP servers | `brew install node` |
| **Homebrew** | Package management (macOS) | See https://brew.sh |
| **Codex CLI** | GPT-5.2 access | `brew install --cask codex` |
| **Gemini CLI** | Gemini access | `brew install gemini-cli` |
| **GitHub CLI (gh)** | `/pr-summary` command | `brew install gh` |
| **jq** | Stop hook parsing | `brew install jq` |

### Setup Command

Run `/setup` to install and verify dependencies:

```bash
# What /setup does:
brew install --cask codex
brew install gemini-cli

# Verification
gemini "what's your name"
codex exec "what's your name"
```

### Security Considerations

**Commands with External API Calls**:

| Command | External API | Data Sent |
|---------|--------------|-----------|
| `/deepwork` | OpenAI (GPT-5.2), Google (Gemini), Anthropic | Task context, code snippets for review |
| `/ultrawork` | OpenAI (GPT-5.2), Google (Gemini), Anthropic | Task context, code snippets |
| `/orchestrator` | OpenAI (GPT-5.2), Google (Gemini), Anthropic | Task delegation, code context |
| `/explore` | Google (Gemini) | Codebase search queries |
| `/oracle` | OpenAI (GPT-5.2) | Architecture questions, code context |
| `/librarian` | Context7, GitHub API | Library documentation queries |
| `/pr-summary` | OpenAI (GPT-5.2), Google (Gemini), GitHub API (via gh) | PR diff, commit messages |
| `/setup` | npm registry (via npx) | Package download requests |

**Data Exposure Risks**:
- MCP servers send code context to external AI providers (Google, OpenAI, Anthropic)
- Ralph loops may iterate autonomously for extended periods
- `/pr-summary` fetches PR data which may contain sensitive information
- Saved contexts (`./docs/tasks/save/`) may contain sensitive code - add to `.gitignore`

**Token Cost Awareness**:
- Ralph loops can consume significant API tokens
- Triple review gate runs 3 AI model calls per review cycle
- Set `--max-iterations` to limit token burn
- Consider `/ultrawork` (optional review) for cost-sensitive tasks

**Operational Safety**:
- Ralph loops run **autonomously** until completion promise or max iterations
- Use `/cancel-work` to stop active loops
- Monitor with `/status` to track iteration progress
- State file (`.claude/ralph-loop.local.md`) can be manually deleted to stop loops

### Permissions Required

The plugin requires Claude Code's YOLO mode or explicit permissions for:
- File system access (Read, Write, Edit)
- Shell execution (Bash)
- Network access (WebFetch, WebSearch)
- External tool execution (MCP servers)

---

## Appendix: Hard Rules

### NEVER DO

- Skip clarification when ambiguous
- Skip TodoWrite
- Batch todo updates
- Fake completion
- Skip reviewer
- Ignore feedback
- Leave code broken
- Block on Explore/Librarian
- Skip Oracle after 3 failures
- Librarian without permalinks
- Search year 2024 (always use current year)
- Use `as any`, `@ts-ignore`, `@ts-expect-error`

### ALWAYS DO

- Ask first if unclear
- Create todos before work
- Mark completed immediately
- Provide evidence (file:line, permalinks)
- Track all agent/MCP calls
- Output call report before completion

---

## Source File References

This report was generated by analyzing the following key source files:

| File | Purpose | Lines |
|------|---------|-------|
| `.claude-plugin/plugin.json` | Plugin metadata | 9 |
| `.mcp.json` | MCP server configuration | 19 |
| `hooks/hooks.json` | Hook registration | 15 |
| `hooks/stop-hook.sh` | Ralph loop continuation | 197 |
| `scripts/setup-ralph-loop.sh` | Loop state setup | 245 |
| `agents/orchestrator.md` | Orchestrator agent definition | 46 |
| `agents/oracle.md` | Oracle agent definition | 43 |
| `agents/explore.md` | Explore agent definition | 37 |
| `agents/librarian.md` | Librarian agent definition | 47 |
| `agents/reviewer.md` | Reviewer agent definition | 12 |
| `prompts/orchestrator-workflow.md` | Orchestrator behavior | 363 |
| `prompts/oracle-persona.md` | Oracle behavior | 75 |
| `prompts/explore-persona.md` | Explore behavior | 79 |
| `prompts/librarian-persona.md` | Librarian behavior | 155 |
| `prompts/reviewer-persona.md` | Reviewer behavior | 132 |
| `commands/*.md` | 14 command definitions | ~300 |
| `.commands-body/*.md` | 14 command bodies | ~1500 |

**Total Files in Plugin**: 43
**Plugin Root**: `plugins/oh-my-claude/`

---

*Report generated by Claude Opus 4.5 with multi-agent analysis*
