**Do not mention reading include files.**

# /ultrawork - Ultra Work Loop

Ralph loop with multi-agent delegation for autonomous development.

## Workflow

@include(${CLAUDE_PLUGIN_ROOT}/prompts/orchestrator-workflow.md)

---

# Optional Phase 3 - AI Review

Do this if the work is complex. AskUserQuestion first to gate this (takes hours).

### Review both Codex and Gemini

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

#### Review Resolve

If the review got under 9.5 from any of the reviewers, then AskUserQuestion about:

- stop here
- fix the reviewer issues and try this review process again
- fix the reviewer issues and try this review process again until forever

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

**ONLY output `<promise>COMPLETE</promise>` when ALL conditions are TRUE:**

- [ ] Task is genuinely complete
- [ ] All todos marked complete
- [ ] Code works (build passes, tests pass if applicable)
- [ ] No broken functionality left behind
- [ ] **Agent/MCP Call Report** has been output

---

# Final Phase - Call Report (MANDATORY)

**BEFORE outputting `<promise>COMPLETE</promise>`, run:**

```bash
${CLAUDE_PLUGIN_ROOT}/hooks/call-tracker.sh report
```

This auto-generates the report with real timestamps from hook-tracked data.

---

Now begin:
1. **Run `${CLAUDE_PLUGIN_ROOT}/hooks/call-tracker.sh start`** (FIRST - marks tracking start)
2. **AskUserQuestion** if anything unclear
3. **TodoWrite** to plan all steps
4. Work, verify, iterate until complete
5. Run `call-tracker.sh report` before completion
