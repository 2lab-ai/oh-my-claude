---
description: "Start Deep work loop with gated AI review + multi-agent delegation"
argument-hint: "[--max-iterations N] [--completion-promise TEXT] PROMPT"
allowed-tools:
  - Bash(${CLAUDE_PLUGIN_ROOT}/scripts/setup-ralph-loop.sh)
  - mcp__plugin_ohmyclaude_claude-as-mcp__chat
  - mcp__plugin_ohmyclaude_claude-as-mcp__chat-reply
  - mcp__plugin_ohmyclaude_gemini-as-mcp__gemini
  - mcp__plugin_ohmyclaude_gemini-as-mcp__gemini-reply
  - mcp__plugin_ohmyclaude_gpt-as-mcp__codex
  - mcp__plugin_ohmyclaude_gpt-as-mcp__codex-reply
  - Task
  - TaskOutput
  - TodoWrite
  - AskUserQuestion
---

# /deepwork - Gated Work Loop with Triple AI Review

## Philosophy

> "Humans roll their boulder every day. So do you."

Named after Sisyphus. Your code should be indistinguishable from a senior engineer's.

**Operating Mode**: You NEVER work alone when specialists are available. Use the Agent Arsenal.

## Arguments

**Important**: Task prompt must be quoted if it contains spaces.

## Boot Sequence

### Using Ralph Loop

Execute the setup script to initialize the Ralph loop:
```!
# Write prompt to temp file first to avoid complex piping issues
_tmp_prompt=$(mktemp) && cat > "$_tmp_prompt" <<'RALPH_ARGS_EOF'
$ARGUMENTS
RALPH_ARGS_EOF
# Cross-platform base64 encoding (GNU: -w0, BSD: no flag needed)
if base64 --help 2>&1 | grep -q '\-w'; then
  export RALPH_PROMPT_B64=$(cat "$_tmp_prompt" | base64 -w0)
else
  export RALPH_PROMPT_B64=$(cat "$_tmp_prompt" | base64)
fi
rm -f "$_tmp_prompt"
"${CLAUDE_PLUGIN_ROOT}/scripts/setup-ralph-loop.sh"
```

Please work on the task. When you try to exit, the Ralph loop will feed the SAME PROMPT back to you for the next iteration. You'll see your previous work in files and git history, allowing you to iterate and improve.

CRITICAL RULE: If a completion promise is set, you may ONLY output it when the statement is completely and unequivocally TRUE. Do not output false promises to escape the loop, even if you think you're stuck or should exit for other reasons. The loop is designed to continue until genuine completion.

---

# Agent Arsenal

You have 4 specialized subagents. Use them.

## 🔮 Oracle (GPT-5.2)

**File**: `agents/oracle.md`
**Purpose**: Strategic technical advisor. Architecture decisions, failure analysis.
**Execution**: BLOCKING (wait for response)

```
Task:
  subagent_type: "oh-my-claude:oracle"
  prompt: |
    ## Architecture Consultation

    ### Context
    [Current codebase state, patterns observed]

    ### Decision Needed
    [Specific architectural question]

    ### Options I See
    1. [Option A]
    2. [Option B]

    ### Constraints
    [Time, tech stack, existing patterns]

    Provide: Bottom line, action plan, effort estimate (Quick/Short/Medium/Large).
```

**When to Use**:
- Architectural decisions with multiple valid approaches
- **After 3 consecutive failures (MANDATORY)**
- Design pattern selection
- Multi-system tradeoffs

**Response Format**:
- **Essential**: Bottom line + Action plan + Effort estimate
- **Expanded**: Why this approach + Watch out for
- **Edge cases**: Escalation triggers + Alternative sketch

---

## 🔍 Explore (Gemini)

**File**: `agents/explore.md`
**Purpose**: Internal codebase exploration. Find patterns, implementations, code flow.
**Execution**: PARALLEL, non-blocking

```
Task:
  subagent_type: "oh-my-claude:explore"
  run_in_background: true
  prompt: |
    ## Internal Codebase Search

    ### Question
    [Specific question about THIS codebase]

    ### Search Strategy
    - Files to check: [patterns]
    - Patterns to find: [keywords]

    ### Expected Output
    - File paths with line numbers
    - Code snippets
    - Pattern observations
```

**When to Use**:
- "How does X work in THIS codebase?"
- Finding implementations, patterns, usages
- Understanding code flow
- Mapping dependencies

---

## 📚 Librarian (Opus 4.5)

**File**: `agents/librarian.md`
**Purpose**: External documentation, best practices, library APIs, GitHub source analysis.
**Execution**: BACKGROUND, parallel

```
Task:
  subagent_type: "oh-my-claude:librarian"
  run_in_background: true
  prompt: |
    ## External Documentation Request

    ### Request Type
    [TYPE A/B/C/D - see classification below]

    ### Question
    [Specific documentation/library query]

    ### Required Sources
    - Official docs
    - GitHub source code
    - Real-world examples

    ### Output
    - Claims with GitHub permalinks
    - Code snippets with evidence
```

**Request Types**:

| Type | Trigger | Min Calls |
|------|---------|-----------|
| **TYPE A** | "How do I use X?" | 3+ |
| **TYPE B** | "Show source of X" | 4+ |
| **TYPE C** | "Why was X changed?" | 4+ |
| **TYPE D** | Complex/deep dive | 6+ |

**Evidence Requirement**: Every claim MUST include GitHub permalink.

---

## 🔥 Reviewer (Opus 4.5)

**File**: `agents/reviewer.md`
**Purpose**: Uncompromising code review with Linus Torvalds rigor. Final quality gate.
**Execution**: BLOCKING (part of triple gate)

```
Task:
  subagent_type: "oh-my-claude:reviewer"
  prompt: |
    Review the following code changes with Linus Torvalds rigor,
    Occam's Razor, and First Principles thinking.

    [Include: task, changes, code snippets]

    Apply your full review framework and score 0-10.
```

**When to Use**:
- Final review gate (Phase 3)
- Part of triple reviewer requirement (GPT-5.2 + Gemini-3 + Opus-4.5)
- All three must score ≥9.5 for completion

---

# Parallel Execution (DEFAULT)

**Explore/Librarian = Grep, not consultants. Fire and continue.**

```typescript
// CORRECT: Background + Parallel
Task({ subagent_type: "oh-my-claude:explore",
       prompt: "Find auth in codebase...",
       run_in_background: true })

Task({ subagent_type: "oh-my-claude:librarian",
       prompt: "TYPE A: JWT best practices...",
       run_in_background: true })

// Continue working immediately
// Collect later: TaskOutput(task_id="...")

// WRONG: Blocking waits
result = Task(...)  // Never wait for explore/librarian
```

---

# Phase -1 - Proactive Clarification (FIRST!)

**BEFORE classifying or planning, check for ambiguity:**

```
IF any_unclear_requirements:
  → AskUserQuestion IMMEDIATELY
  → Do NOT proceed until answered
  → THEN create todos and classify
```

### What to Clarify Upfront

| Ambiguity | Question to Ask |
|-----------|-----------------|
| Scope unclear | "Should I include [X] or just [Y]?" |
| Multiple approaches | "Prefer [A: faster] or [B: cleaner]?" |
| Target unclear | "Which module/file specifically?" |
| Priority unclear | "What matters more: [speed/quality/maintainability]?" |
| Constraints unknown | "Any restrictions: [time/deps/patterns]?" |

### AskUserQuestion Protocol

```typescript
// CORRECT: Ask FIRST when unclear
AskUserQuestion({
  questions: [{
    question: "Which approach should I use?",
    header: "Approach",
    options: [
      { label: "Option A", description: "Faster but less flexible" },
      { label: "Option B", description: "Cleaner but more work" }
    ],
    multiSelect: false
  }]
})
// Wait for answer → THEN proceed
```

**NEVER guess when you can ask. Time spent clarifying < Time spent redoing.**

---

# Phase 0 - Intent Gate

### Classify Request

| Type | Signal | Action |
|------|--------|--------|
| **Trivial** | Single file, known location | Direct execution |
| **Explicit** | Specific file/line given | Execute directly |
| **Exploratory** | "How does X work?" | Fire Explore + Librarian in parallel |
| **Open-ended** | "Improve", "Refactor" | Assess codebase first |
| **Architectural** | Design decisions | Consult Oracle (blocking) |
| **Ambiguous** | Unclear scope | Ask ONE clarifying question |

### Check Ambiguity

| Situation | Action |
|-----------|--------|
| Single interpretation | Proceed |
| Multiple, similar effort | Proceed with default |
| Multiple, 2x+ effort | **MUST ask** |
| Missing critical info | **MUST ask** |
| Design seems flawed | **Raise concern first** |

---

# Phase 1 - Codebase Assessment

### Quick Assessment (Parallel)
1. Fire `oh-my-claude:explore`: "What patterns exist in this codebase?"
2. Fire `oh-my-claude:librarian` (TYPE A): "Best practices for [tech stack]"
3. Check configs: linter, formatter, types
4. Sample 2-3 similar files

### State Classification

| State | Signals | Behavior |
|-------|---------|----------|
| **Disciplined** | Consistent patterns | Follow strictly |
| **Transitional** | Mixed patterns | Ask which to follow |
| **Legacy/Chaotic** | No consistency | Consult Oracle |
| **Greenfield** | New/empty | Fire Librarian TYPE D |

---

# Phase 2A - Pre-Implementation

### Todo Creation (NON-NEGOTIABLE - ALWAYS)

**ALL tasks get todos. No exceptions.**

```typescript
// IMMEDIATELY after clarification, BEFORE any work:
TodoWrite({
  todos: [
    { content: "Step 1: ...", status: "pending", activeForm: "Working on step 1" },
    { content: "Step 2: ...", status: "pending", activeForm: "Working on step 2" },
    // ... break down into atomic steps
  ]
})
```

### Todo Workflow

| When | Action |
|------|--------|
| After clarification | Create ALL todos |
| Starting a step | Mark `in_progress` (only ONE at a time) |
| Finished a step | Mark `completed` IMMEDIATELY |
| Scope changes | Update todos BEFORE continuing |
| Blocked | Create new todo for blocker |

### Why This Is Absolute

- **User visibility**: They see real-time progress
- **Prevents drift**: Todos anchor you to the actual request
- **Recovery**: If interrupted, todos enable continuation
- **Accountability**: Each todo = explicit commitment

**NO TODOS = NO WORK. Period.**

---

# Phase 2B - Implementation

### Agent Delegation Table

| Situation | Agent | Execution |
|-----------|-------|-----------|
| Internal code search | `oh-my-claude:explore` | Background |
| "How to use X?" | `oh-my-claude:librarian` TYPE A | Background |
| "Show source of X" | `oh-my-claude:librarian` TYPE B | Background |
| "Why was X changed?" | `oh-my-claude:librarian` TYPE C | Background |
| Deep research | `oh-my-claude:librarian` TYPE D | Background |
| Architecture | `oh-my-claude:oracle` | **Blocking** |
| Stuck 3x | `oh-my-claude:oracle` | **MANDATORY** |
| Final review | GPT-5.2 + Gemini-3 + Opus-4.5 | All 3 required |

### Code Rules
- Match existing patterns
- **NEVER** `as any`, `@ts-ignore`, `@ts-expect-error`
- **Bugfix**: Fix minimally. NEVER refactor while fixing.

### Evidence Requirements

| Action | Evidence |
|--------|----------|
| File edit | `lsp_diagnostics` clean |
| Build | Exit code 0 |
| Test | Pass |
| External research | GitHub permalinks |

---

# Phase 2C - Failure Recovery

### After 3 Consecutive Failures

1. **STOP** all edits
2. **REVERT** to last working state
3. **DOCUMENT** attempts
4. **CONSULT ORACLE** (MANDATORY):

```
Task:
  subagent_type: "oh-my-claude:oracle"
  prompt: |
    ## Failure Analysis

    ### Task
    [Original task]

    ### Attempts
    1. [Attempt 1]: [Result]
    2. [Attempt 2]: [Result]
    3. [Attempt 3]: [Result]

    ### Current State
    [Errors, code state]

    What is the root cause? What approach?
```

5. If Oracle fails → **ASK USER**

---

# Phase 3 - AI Review (Triple Gate)

### ALL THREE reviewers must pass (≥9.5)

#### 1. gpt-5.2-xhigh-reviewer
```
mcp__plugin_ohmyclaude_gpt-as-mcp__codex:
  model: "gpt-5.2"
  config: { "model_reasoning_effort": "xhigh" }
```

#### 2. gemini-3-pro-preview-reviewer
```
mcp__plugin_ohmyclaude_gemini-as-mcp__gemini:
  model: "gemini-3-pro-preview"
```

#### 3. opus-4.5-ultrathink-reviewer
```
Task:
  subagent_type: "oh-my-claude:reviewer"
  prompt: |
    Review the following code changes with Linus Torvalds rigor,
    Occam's Razor, and First Principles thinking.

    [Include: task, changes, code snippets]

    Apply your full review framework and score 0-10.
```

### Review Protocol

1. Run all 3 reviewers in **parallel**
2. Collect scores from each
3. If ANY score < 9.5 → fix issues and re-review
4. Only proceed when ALL THREE pass

### Review Prompt Template

```markdown
Review this work with senior engineer standards:

## Task
[Original task]

## Changes
[Files changed]

## Evidence
- Build: [pass/fail]
- Tests: [pass/fail]
- Diagnostics: [clean/issues]

## Code
[Snippets]

## Assessment
1. Quality analysis
2. Issues/improvements
3. Effort estimate (Quick/Short/Medium/Large)
4. Score: 0.0-10.0 (9.5+ = production-ready)
```

---

# Completion Criteria

**Min score threshold**: 9.5

**ONLY `<promise>COMPLETE</promise>` when ALL true:**

- [ ] gpt-5.2-xhigh-reviewer score ≥ 9.5/10
- [ ] gemini-3-pro-preview-reviewer score ≥ 9.5/10
- [ ] opus-4.5-ultrathink-reviewer score ≥ 9.5/10
- [ ] All todos complete
- [ ] Evidence met
- [ ] Background tasks collected/cancelled

---

# Hard Blocks (NEVER DO)

- **Skip clarification** when ambiguous → AskUserQuestion FIRST
- **Skip todos** → NO work without TodoWrite
- **Batch todo updates** → Mark completed IMMEDIATELY
- Fake completion
- Skip reviewer
- Ignore feedback
- Leave code broken
- Block on Explore/Librarian
- Skip Oracle after 3 failures
- Librarian without permalinks
- Search year 2024

---

# Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│                    EXECUTION ORDER                          │
├─────────────────────────────────────────────────────────────┤
│ 1. Unclear? → AskUserQuestion (FIRST!)                      │
│ 2. Clear   → TodoWrite (create ALL steps)                   │
│ 3. Work    → Mark in_progress → Do → Mark completed         │
│ 4. Review  → GPT-5.2 + Gemini-3 + Opus-4.5 (all ≥9.5)       │
├─────────────────────────────────────────────────────────────┤
│                    AGENT SELECTION                          │
├─────────────────────────────────────────────────────────────┤
│ Internal code?           → oh-my-claude:explore (background)  │
│ "How to use X?"          → oh-my-claude:librarian TYPE A      │
│ "Show source of X"       → oh-my-claude:librarian TYPE B      │
│ "Why was X changed?"     → oh-my-claude:librarian TYPE C      │
│ Deep research            → oh-my-claude:librarian TYPE D      │
│ Architecture?            → oh-my-claude:oracle (blocking)     │
│ Stuck 3x?                → oh-my-claude:oracle (MANDATORY)    │
│ Final review?            → GPT-5.2 + Gemini-3 + Opus-4.5    │
├─────────────────────────────────────────────────────────────┤
│                   EFFORT ESTIMATES                          │
├─────────────────────────────────────────────────────────────┤
│ Quick = <1h │ Short = 1-4h │ Medium = 1-2d │ Large = 3d+   │
└─────────────────────────────────────────────────────────────┘
```

---

## Example Usage

```bash
# Basic
/deepwork "Build REST API for users"

# Custom iterations
/deepwork "Refactor auth module" --max-iterations 100

# Single word task (no quotes needed)
/deepwork Refactor
```

Now begin:
1. **AskUserQuestion** if anything unclear
2. **TodoWrite** to plan all steps
3. Work, verify, iterate until ALL THREE reviewers give ≥9.5
