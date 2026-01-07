---
description: "Start Deep work loop with gated AI review + multi-agent delegation"
argument-hint: "[--max-iterations N] [--completion-promise TEXT] PROMPT"
allowed-tools:
  - Bash(${CLAUDE_PLUGIN_ROOT}/scripts/start-ralph-loop.sh)
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

Ralph loop with triple AI review gate. All 3 reviewers must score ≥9.5.

## Boot Sequence

Execute the setup script to initialize the Ralph loop:
```!
# Auto-inject --completion-promise COMPLETE if not already specified
# Write prompt to temp file first to avoid complex piping issues
_tmp_prompt=$(mktemp) && cat > "$_tmp_prompt" <<'RALPH_ARGS_EOF'
$ARGUMENTS
RALPH_ARGS_EOF
_prompt_content=$(cat "$_tmp_prompt")
if [[ ! "$_prompt_content" =~ --completion-promise ]]; then
  _prompt_content="$_prompt_content --completion-promise COMPLETE"
fi
# Cross-platform base64 encoding (GNU: -w0, BSD: no flag needed)
if base64 --help 2>&1 | grep -q '\-w'; then
  export RALPH_PROMPT_B64=$(printf '%s' "$_prompt_content" | base64 -w0)
else
  export RALPH_PROMPT_B64=$(printf '%s' "$_prompt_content" | base64)
fi
rm -f "$_tmp_prompt"
"${CLAUDE_PLUGIN_ROOT}/scripts/setup-ralph-loop.sh"
```

## Workflow

@include(${CLAUDE_PLUGIN_ROOT}/prompts/orchestrator-workflow.md)

---

# Phase 3 - AI Review (Triple Gate) - MANDATORY

### ALL THREE reviewers must pass (≥9.5)

#### 1. GPT-5.2 Reviewer
```
mcp__plugin_ohmyclaude_gpt-as-mcp__codex:
  model: "gpt-5.2"
  config: { "model_reasoning_effort": "xhigh" }
```

#### 2. Gemini-3 Reviewer
```
mcp__plugin_ohmyclaude_gemini-as-mcp__gemini:
  model: "gemini-3-pro-preview"
```

#### 3. Opus-4.5 Reviewer
```
Task:
  subagent_type: "oh-my-claude:reviewer"
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

## Assessment
1. Quality analysis
2. Issues/improvements
3. Score: 0.0-10.0 (9.5+ = production-ready)
```

---

# Completion Criteria

```
╔══════════════════════════════════════════════════════════════════╗
║  TO EXIT THIS LOOP, OUTPUT EXACTLY:                              ║
║                                                                  ║
║     <promise>COMPLETE</promise>                                  ║
║                                                                  ║
║  WITH THE XML TAGS. THE TAGS ARE REQUIRED.                       ║
╚══════════════════════════════════════════════════════════════════╝
```

**Min score threshold**: 9.5

**ONLY output `<promise>COMPLETE</promise>` when ALL conditions are TRUE:**

- [ ] Task is genuinely complete
- [ ] All todos marked complete
- [ ] Code works (build passes, tests pass if applicable)
- [ ] No broken functionality left behind
- [ ] gpt-5.2-xhigh reviewer score ≥ 9.5/10
- [ ] gemini-3-pro-preview reviewer score ≥ 9.5/10
- [ ] opus-4.5 reviewer score ≥ 9.5/10

---

Now begin:
1. **AskUserQuestion** if anything unclear
2. **TodoWrite** to plan all steps
3. Work, verify, iterate until ALL THREE reviewers give ≥9.5
