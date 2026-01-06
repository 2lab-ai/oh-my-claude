# oh-my-claude User Stories & Workflow Improvement Plan

## Part 1: User Pain Points Research Summary

Based on research from Reddit, Hacker News, Medium, GitHub issues, and developer communities.

### Sources & Key Findings

| Source | Key Finding |
|--------|-------------|
| [Milvus Blog: Grep-Only Retrieval](https://milvus.io/blog/why-im-against-claude-codes-grep-only-retrieval-it-just-burns-too-many-tokens.md) | Token bloat from grep dumps drives up costs |
| [HN: Claude Code Experience](https://news.ycombinator.com/item?id=44596472) | Context loss in long conversations |
| [Medium: 30-Day Journey](https://medium.com/@Pritheeswarar/claude-ai-a-30-day-journey-through-frustrations-and-limitations-b8caf0dc8374) | Random refusals, inconsistent behavior |
| [Letanure Blog: CLI Scripting](https://www.letanure.dev/blog/claude-code-power-user-cli-scripting) | Custom commands stopping randomly |
| [Medium: AI Memory Management](https://medium.com/@nomannayeem/building-ai-agents-that-actually-remember-a-developers-guide-to-memory-management-in-2025-062fd0be80a1) | Need for persistent project memory |
| [GitHub #4274: Hook Types](https://github.com/anthropics/claude-code/issues/4274) | Request for typed hooks integration |
| [GitHub #6981: MCP Hooks](https://github.com/anthropics/claude-code/issues/6981) | Request for hooks in MCP servers |

---

## Part 2: Identified Pain Points

### Category 1: Token & Cost Issues

| Pain Point | Severity | Current oh-my-claude Solution |
|------------|----------|-------------------------------|
| Token bloat from grep dumps | HIGH | Explore agent with parallel targeted searches |
| Costs scale horribly with repo size | HIGH | Agent specialization reduces redundant queries |
| Running out of tokens mid-task | HIGH | /save & /load for session continuity |

**User Quote**: "Every grep dump shovels massive amounts of irrelevant code into the LLM, driving up costs."

### Category 2: Context & Memory Problems

| Pain Point | Severity | Current oh-my-claude Solution |
|------------|----------|-------------------------------|
| Conversations get too long, loses context | CRITICAL | /save for context snapshots |
| Forgotten context mid-conversation | CRITICAL | TodoWrite for progress tracking |
| Inconsistent code generation | HIGH | Agent specialization with specific prompts |
| Random refusals for previously working tasks | MEDIUM | Ralph loop forces completion |

**User Quote**: "Users get into long, rambling conversations with Claude. All that context builds up."

### Category 3: Usage Limits

| Pain Point | Severity | Current oh-my-claude Solution |
|------------|----------|-------------------------------|
| Usage limits shared across ALL Claude apps | HIGH | Efficient agent delegation reduces waste |
| Limits reset every 5 hours | MEDIUM | /save allows pause and resume |
| Abuse prevention throttling | MEDIUM | Not addressed |

### Category 4: Workflow & Productivity

| Pain Point | Severity | Current oh-my-claude Solution |
|------------|----------|-------------------------------|
| Steep learning curve | HIGH | /ultrawork abstracts complexity |
| Requires strong prompt engineering | HIGH | Pre-built agent prompts |
| Multiple CLAUDE.md files causing confusion | MEDIUM | Centralized plugin system |
| Custom commands randomly stopping | MEDIUM | Robust hook implementation |

### Category 5: Extension & Customization

| Pain Point | Severity | Current oh-my-claude Solution |
|------------|----------|-------------------------------|
| MCP servers consume too many tokens | HIGH | Optimized MCP configuration |
| No stateful hooks | MEDIUM | State file pattern (.local.md) |
| Hook boilerplate complexity | MEDIUM | Shell script hooks |
| No centralized admin management | LOW | Plugin marketplace |

---

## Part 3: User Stories (Current Features)

### Epic 1: Autonomous Development Loop

#### US-1.1: Iterative Work Loop
**As a** developer
**I want** Claude to work autonomously in a loop until my task is complete
**So that** I can step away and let the AI iterate on complex tasks

**Acceptance Criteria:**
- [x] `/ultrawork` command initiates Ralph loop
- [x] Loop continues until `<promise>COMPLETE</promise>` is output
- [x] Previous work visible in files and git history
- [x] Max iterations safeguard available

**Edge Cases:**
- [x] Max iterations reached → Loop exits with warning
- [x] State file corrupted → Loop exits with error, cleanup
- [x] Missing dependencies → Exit with clear error message
- [x] Cancellation requested → `/cancel-ralph` cleans up

#### US-1.2: Quality-Gated Work Loop
**As a** developer working on critical code
**I want** mandatory AI review before task completion
**So that** I can ensure high quality output

**Acceptance Criteria:**
- [x] `/deepwork` command with 9.5+ score requirement
- [x] Both Codex and Gemini must approve
- [x] Loop continues until quality threshold met

**Edge Cases:**
- [x] One reviewer unavailable → Retry with backoff, then warn user and ask to proceed with single reviewer
- [x] Score below threshold → Continue loop, don't complete
- [x] Reviewer API failure → Retry with exponential backoff (max 3 attempts)

### Epic 2: Cross-Session Context Management

#### US-2.1: Save Work Context
**As a** developer
**I want** to save my current work context
**So that** I can resume later or continue in another tool

**Acceptance Criteria:**
- [x] `/save` creates timestamped context file
- [x] Captures plan, todos, files modified, notes
- [x] Stores in `./docs/tasks/save/{id}/`

**Edge Cases:**
- [x] No active work → Create minimal context file
- [x] Directory creation fails → Clear error message
- [x] Duplicate timestamps → Append `_N` suffix (e.g., `20250106_120000_1`)

#### US-2.2: Load Work Context
**As a** developer
**I want** to load a previously saved context
**So that** I can seamlessly continue work

**Acceptance Criteria:**
- [x] `/load <id>` restores context
- [x] Validates file existence and branch
- [x] Uses AskUserQuestion for ambiguities
- [x] Archives loaded context to prevent re-load

**Edge Cases:**
- [x] Save not found → List available saves
- [x] Branch mismatch → Warn user, ask to proceed
- [x] Referenced files deleted → List missing files, ask to proceed
- [x] Already archived → Error: already loaded

#### US-2.3: Verify Archived Work
**As a** developer
**I want** to verify that archived saves completed successfully
**So that** I can confirm work was finished and clean up incomplete saves

**Acceptance Criteria:**
- [x] `/check` command verifies archived saves
- [x] Checks referenced files still exist
- [x] Reports completion status (complete/incomplete)
- [x] Lists any missing files or unfinished todos

**Edge Cases:**
- [x] Archived save not found → List available archives
- [x] Referenced files deleted → Report as incomplete with details
- [x] Context file corrupted → Report error, suggest cleanup

#### US-2.4: Cross-Tool Compatibility
**As a** developer using multiple AI tools
**I want** to share work context between Claude Code, Gemini CLI, and Codex
**So that** I can use the best tool for each sub-task

**Acceptance Criteria:**
- [x] Shared save location (`./docs/tasks/save/`)
- [x] `install-cross-session-commands.sh` script
- [x] Commands work in Gemini CLI and Codex

**Edge Cases:**
- [x] Different tool versions → Context format backward compatible
- [x] Concurrent access → Timestamp-based IDs prevent conflicts

### Epic 3: Multi-Agent Orchestration

#### US-3.1: Internal Codebase Search
**As a** developer
**I want** fast parallel searches within my codebase
**So that** I can quickly understand how things work

**Acceptance Criteria:**
- [x] Explore agent with Gemini for fast search
- [x] Parallel execution (non-blocking)
- [x] Returns file:line references

**Edge Cases:**
- [x] Gemini API unavailable → Fallback to basic Grep/Glob
- [x] Very large codebase → Limit search scope

#### US-3.2: External Documentation Research
**As a** developer
**I want** to research library documentation and best practices
**So that** I can implement features correctly

**Acceptance Criteria:**
- [x] Librarian agent with Context7 (MCP documentation tool) + GitHub search
- [x] GitHub permalinks required as evidence
- [x] Background execution

**Edge Cases:**
- [x] No internet connection → Error with clear message
- [x] GitHub rate limited → Graceful degradation

#### US-3.3: Strategic Technical Consultation
**As a** developer facing architectural decisions
**I want** deep analysis and recommendations
**So that** I can make informed choices

**Acceptance Criteria:**
- [x] Oracle agent with Codex GPT-5.2
- [x] Blocking execution (waits for response)
- [x] Mandatory after 3 consecutive failures

**Edge Cases:**
- [x] Codex API unavailable → Use Opus only
- [x] Oracle fails → Escalate to user (AskUserQuestion)

---

## Part 4: User Stories (Future Features)

### Epic 4: LSP Integration

#### US-4.1: On-Demand Diagnostics
**As a** developer
**I want** Claude to query LSP diagnostics before/after edits
**So that** it can fix errors proactively

**Acceptance Criteria:**
- [ ] LSP server integration via MCP
- [ ] On-demand error/warning retrieval (not real-time streaming)
- [ ] Auto-fix suggestions based on diagnostics
- [ ] Support for TypeScript (Phase 1), then Python, Rust, Go

**Edge Cases:**
- [ ] LSP server not installed → Clear setup instructions
- [ ] LSP server crash → Graceful degradation to basic editing
- [ ] Unsupported language → Skip LSP, use basic tools

**Note**: "On-demand" replaces "real-time" since Claude Code is CLI-based and doesn't support push events.

#### US-4.2: Symbol Navigation
**As a** developer
**I want** Claude to navigate to definitions, references, and implementations
**So that** it can understand code relationships accurately

**Acceptance Criteria:**
- [ ] Go to definition
- [ ] Find all references
- [ ] Find implementations
- [ ] Symbol search

**Edge Cases:**
- [ ] Symbol not found → Return empty result with message
- [ ] Multiple definitions → Return all with context

#### US-4.3: Intelligent Completions
**As a** developer
**I want** Claude to leverage LSP completions
**So that** it generates syntactically correct code

**Acceptance Criteria:**
- [ ] Completion suggestions from LSP
- [ ] Type information in context
- [ ] Import suggestions

**Edge Cases:**
- [ ] No completions available → Fall back to model knowledge
- [ ] Too many completions → Filter by relevance

### Epic 5: Enhanced Memory Management

#### US-5.1: Vectorized Context Retrieval
**As a** developer with large codebases
**I want** intelligent context retrieval instead of grep dumps
**So that** only relevant code is loaded into context

**Acceptance Criteria:**
- [ ] Semantic chunking of codebase
- [ ] Vector search for relevant snippets
- [ ] Token-efficient context loading
- [ ] Incremental updates on file changes

**Implementation Approach (Phased)**:
1. **Phase 1**: File-based index with keyword search (no external deps)
2. **Phase 2**: Optional embedding support via API (OpenAI/Voyage)
3. **Phase 3**: Local vector DB (Chroma/Qdrant) for offline use

**Edge Cases:**
- [ ] Embedding API unavailable → Fall back to keyword search
- [ ] Index out of sync → Rebuild on file hash mismatch
- [ ] Very large repo → Incremental indexing, not full rebuild

#### US-5.2: Persistent Project Memory
**As a** developer
**I want** Claude to remember project-specific knowledge across sessions
**So that** I don't have to re-explain context

**Acceptance Criteria:**
- [ ] Project memory bank (`.claude/memory/`)
- [ ] Auto-capture important decisions
- [ ] Retrieval during relevant tasks
- [ ] Manual memory editing

**Edge Cases:**
- [ ] Memory file corrupted → Rebuild from available data
- [ ] Memory too large → Summarize old entries

#### US-5.3: Conversation Summarization
**As a** developer in long sessions
**I want** automatic conversation summarization
**So that** context doesn't bloat and get lost

**Acceptance Criteria:**
- [ ] Auto-summarize after N messages
- [ ] Preserve key decisions and code references
- [ ] Compact hook integration

**Edge Cases:**
- [ ] Summarization loses critical detail → Allow manual override
- [ ] Compact fails → Continue without summarization

### Epic 6: Workflow Automation

#### US-6.1: Pre-commit Quality Gate
**As a** developer
**I want** automated AI review before commits
**So that** code quality is enforced

**Acceptance Criteria:**
- [ ] PreToolUse hook for git commit
- [ ] AI review of staged changes
- [ ] Block commit if issues found
- [ ] Configurable strictness levels
- [ ] Bypass mechanism (`--no-verify` or explicit flag)

**Edge Cases:**
- [ ] Review times out → Allow commit with warning
- [ ] API unavailable → Skip review with warning
- [ ] User wants to bypass → Honor `--force` flag

#### US-6.2: Test-Driven Development Mode
**As a** developer
**I want** a TDD workflow where Claude writes tests first
**So that** implementations are always tested

**Acceptance Criteria:**
- [ ] `/tdd` command
- [ ] Test generation from requirements
- [ ] Red-green-refactor loop
- [ ] Coverage tracking

**Edge Cases:**
- [ ] No test framework detected → Suggest setup
- [ ] Tests won't pass → Maximum retry limit

#### US-6.3: PR Review Assistant
**As a** developer
**I want** AI-assisted PR reviews
**So that** code reviews are thorough and fast

**Acceptance Criteria:**
- [ ] `/review-pr <url>` command
- [ ] Security vulnerability scanning
- [ ] Style and convention checking
- [ ] Suggested improvements

**Edge Cases:**
- [ ] PR too large → Review in chunks
- [ ] Private repo → Require auth token

### Epic 7: Enhanced MCP Integration

#### US-7.1: Stateful Hooks via MCP
**As a** plugin developer
**I want** hooks that can maintain state through MCP servers
**So that** complex workflows are possible

**Acceptance Criteria:**
- [ ] MCP tool type hooks
- [ ] State persistence in MCP server
- [ ] Event-driven hook triggers

**Edge Cases:**
- [ ] MCP server crashes → State recovery mechanism
- [ ] State corruption → Reset to defaults

#### US-7.2: Dynamic MCP Server Loading
**As a** developer
**I want** MCP servers to load on-demand
**So that** token overhead is minimized

**Acceptance Criteria:**
- [ ] Lazy MCP server initialization
- [ ] Conditional loading based on task type
- [ ] Token budget awareness

**Edge Cases:**
- [ ] Server fails to start → Clear error, skip server
- [ ] Multiple servers conflict → Priority ordering

### Epic 8: Team & Enterprise Features

#### US-8.1: Shared Plugin Configuration
**As a** team lead
**I want** to share plugin configurations across my team
**So that** everyone uses consistent workflows

**Acceptance Criteria:**
- [ ] Team plugin repository
- [ ] Centralized settings management
- [ ] Permission controls

**Edge Cases:**
- [ ] User overrides team settings → Local > Team precedence
- [ ] Team settings invalid → Fall back to defaults

#### US-8.2: Usage Analytics
**As a** team lead
**I want** to track AI usage and productivity metrics
**So that** I can optimize workflows

**Acceptance Criteria:**
- [ ] Token usage per task
- [ ] Time savings estimates
- [ ] Agent utilization stats

**Edge Cases:**
- [ ] Opt-out users → Exclude from analytics
- [ ] Data privacy concerns → Anonymize data

---

## Part 5: Prioritized Roadmap

### Phase 1: Foundation (Current - Complete)
- [x] Ralph Loop implementation
- [x] Cross-session save/load
- [x] Multi-agent orchestration
- [x] Basic hooks (stop, auto-title, sound)

### Phase 2: Quality & Reliability (Next)
**Focus**: Make current features more robust before adding new ones

- [ ] **Guardrails & Safety**
  - Max token budget per task
  - Automatic timeout for long-running tasks
  - Better cancellation UX
- [ ] **Enhanced Error Recovery**
  - Better failure detection
  - Auto-revert on broken code
  - Root cause analysis
- [ ] **LSP Support** (TypeScript only first)
  - On-demand diagnostics via MCP
  - Symbol navigation

### Phase 3: Memory & Context
- [ ] **Lightweight Index First** (no external deps)
  - File-based keyword search
  - Prove token savings before vector DB
- [ ] **Project Memory Bank**
  - Persistent knowledge base
  - Cross-session learning
- [ ] **Optional Vector Search** (for power users)
  - Embedding API integration
  - Local vector DB option

### Phase 4: Workflow Automation
- [ ] **Pre-commit Quality Gate**
  - Clear opt-in, performance budgets
  - Bypass mechanisms
- [ ] **TDD Mode**
- [ ] **PR Review Assistant**

### Phase 5: Enterprise & Collaboration
- [ ] **Team Plugin Sharing**
- [ ] **Usage Analytics**
- [ ] **Centralized Management**

---

## Part 6: Technical Implementation Notes

### LSP Support Implementation Approach

```
┌────────────────────────────────────────────────────────────┐
│                    Claude Code                              │
│                        │                                    │
│                        ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              MCP Server: lsp-bridge                   │  │
│  │                                                       │  │
│  │  Tools exposed (ON-DEMAND, not streaming):           │  │
│  │  - lsp_diagnostics(file) → errors, warnings          │  │
│  │  - lsp_definition(file, line, col) → location        │  │
│  │  - lsp_references(symbol) → locations[]              │  │
│  │  - lsp_completions(file, line, col) → suggestions[]  │  │
│  │  - lsp_hover(file, line, col) → type info            │  │
│  └──────────────────────────────────────────────────────┘  │
│                        │                                    │
│                        ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Language Servers                         │  │
│  │  Phase 1: typescript-language-server                  │  │
│  │  Phase 2: pyright, rust-analyzer, gopls               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

**Integration Point**: Call `lsp_diagnostics` after each file edit, before completion.

### Vectorized Context Implementation Approach

```
┌────────────────────────────────────────────────────────────┐
│                    PHASED IMPLEMENTATION                    │
└────────────────────────────────────────────────────────────┘

Phase 1: Keyword Index (No External Dependencies)
┌────────────────────────────────────────────────────────────┐
│  - Simple file-based index (JSON)                          │
│  - Keyword extraction (function names, classes, imports)   │
│  - Fast substring matching                                 │
│  - Prove token savings before investing in embeddings      │
└────────────────────────────────────────────────────────────┘
              │
              ▼ (If Phase 1 shows value)
Phase 2: Optional Embedding API
┌────────────────────────────────────────────────────────────┐
│  - Opt-in embedding via OpenAI/Voyage API                  │
│  - Store embeddings in local JSON/SQLite                   │
│  - Semantic search for similar code                        │
└────────────────────────────────────────────────────────────┘
              │
              ▼ (For power users)
Phase 3: Local Vector DB
┌────────────────────────────────────────────────────────────┐
│  - Optional Chroma/Qdrant for offline use                  │
│  - Full semantic search capabilities                       │
│  - Incremental updates                                     │
└────────────────────────────────────────────────────────────┘
```

---

## Part 7: Success Metrics

### Efficiency Metrics
| Metric | Current | Target | Measurement Method |
|--------|---------|--------|-------------------|
| Tokens per task | ~50k | ~20k | Parse MCP server logs for token counts |
| Context switches per task | 3-5 | 1-2 | Count `/save` + `/load` pairs per task |
| Task completion rate | 70% | 95% | Count loops ending with promise vs max_iterations |

**Implementation**: Add `--metrics` flag to `/deepwork` that writes JSON to `.claude/metrics/{timestamp}.json`:
```json
{"task_id": "...", "tokens": 12345, "iterations": 3, "completed": true, "duration_sec": 600}
```

### Quality Metrics
| Metric | Current | Target | Measurement Method |
|--------|---------|--------|-------------------|
| First-try success rate | 60% | 85% | Check git diff size after first iteration |
| Rework rate | 30% | 10% | Track manual edits within 1 hour post-completion |
| AI review score average | 8.5 | 9.5 | Log scores from `/deepwork` reviews |

**Implementation**: `/deepwork` automatically logs review scores to `.claude/metrics/reviews.jsonl`:
```json
{"timestamp": "...", "codex_score": 9.6, "gemini_score": 9.8, "task": "..."}
```

### User Satisfaction Metrics
| Metric | Current | Target | Measurement Method |
|--------|---------|--------|-------------------|
| Setup time | 15 min | 2 min | Timestamp diff: plugin install → first `/ultrawork` |
| Learning curve | Steep | Moderate | Count unique commands used in first 3 sessions |
| Cross-tool compatibility | 3 tools | 5+ tools | Automated test matrix in CI |

**Note**: Metrics collection is opt-in and stored locally. No data is sent externally.

---

## Appendix: Related Resources

- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Ralph Wiggum Technique](https://ghuntley.com/ralph/)
- [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)
- [Claude Code Plugins Documentation](https://code.claude.com/docs/en/plugins)
- [MCP Specification](https://modelcontextprotocol.io/)
