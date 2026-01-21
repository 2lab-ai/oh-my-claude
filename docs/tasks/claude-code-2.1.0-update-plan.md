# Claude Code 2.1.0 Update Plan for oh-my-claude Plugin

## Executive Summary

Claude Code 2.1.0 introduces significant new features that require oh-my-claude plugin updates for compatibility and feature adoption. This plan outlines a phased approach to address breaking changes, adopt new features, and enhance the plugin architecture.

**Version Target**: oh-my-claude v1.0.25 → v1.1.0
**Backward Compatibility**: v1.1.0 MUST work with Claude Code 2.0.x and 2.1.0

---

## Phase 0: Verification (PREREQUISITE)

### 0.1 Feature Existence Verification
**Status**: CRITICAL - Must complete before Phase 2-3

Before implementing new features, verify they actually exist in Claude Code 2.1.0:

**Action Items**:
- [ ] Verify `context: fork` syntax in skill/command frontmatter
- [ ] Verify agent-scoped hooks API (hooks in frontmatter)
- [ ] Verify `once: true` hook property
- [ ] Verify `updatedInput` return format for PreToolUse hooks
- [ ] Verify YAML list syntax for allowed-tools
- [ ] Document evidence links (changelog, official docs)

**Done Criteria**:
- Each feature has documentation link or test proof
- Features not confirmed are deferred to future version

---

## Phase 1: Compatibility Testing (Immediate Priority)

### 1.1 Allowed-tools Syntax Compatibility Test
**Status**: HIGH - Test before modifying
**Effort**: Low

**Test Matrix**:
| Syntax | File Example | 2.0.x Works | 2.1.0 Works | Action |
|--------|--------------|-------------|-------------|--------|
| Inline | `allowed-tools: Read, Write` | ? | ? | Test |
| JSON Array | `allowed-tools: ["Read", "Write"]` | ? | ? | Test |
| YAML List | `allowed-tools:\n  - Read\n  - Write` | ? | ? | Test |

**Action Items**:
- [ ] Test inline syntax with existing commands (e.g., save.md)
- [ ] Test JSON array syntax (e.g., cancel-work.md)
- [ ] Test YAML list syntax with test command
- [ ] **ONLY convert if specific syntax fails in 2.1.0**

**Done Criteria**:
- All three syntaxes tested on both 2.0.x and 2.1.0
- Decision documented: convert or keep as-is
- Rollback: Revert any syntax changes if 2.0.x breaks

### 1.2 ${CLAUDE_PLUGIN_ROOT} Variable Substitution Verification
**Status**: HIGH - Bug fix in 2.1.0
**Effort**: Low (testing only)

**Test Cases**:
```yaml
# Test in allowed-tools
allowed-tools:
  - Bash(${CLAUDE_PLUGIN_ROOT}/scripts/test.sh)

# Test in hooks.json command field
"command": "${CLAUDE_PLUGIN_ROOT}/hooks/call-tracker.sh"
```

**Action Items**:
- [ ] Test variable substitution in allowed-tools
- [ ] Test variable substitution in hooks.json
- [ ] Document behavior on 2.0.x vs 2.1.0

**Done Criteria**:
- Variable substitution behavior documented
- Workarounds identified for 2.0.x if needed

### 1.3 Agent Model Inheritance Verification
**Status**: MEDIUM - Behavior change
**Effort**: Low (testing only)

**Action Items**:
- [ ] Test subagent without explicit model param
- [ ] Test subagent with explicit model param
- [ ] Verify oracle/explore/librarian get correct models

**Done Criteria**:
- Model inheritance behavior documented
- Explicit model params added to agents if needed

---

## Phase 2: Feature Adoption (Short-term, After Phase 0 Verification)

### 2.1 Add `context: fork` to /summary Command ONLY
**Status**: MEDIUM - New feature adoption (if verified in Phase 0)
**Effort**: Low

**Target Commands**:
- `/summary` ONLY - Long-running analysis that benefits from isolation

**Decision on /orchestrator**:
- **DO NOT fork /orchestrator** - It needs conversation context for coordination
- Orchestrator should fork its *subtasks* (delegated agents), not itself

**Implementation**:
```yaml
---
description: "Advanced summarization"
context: fork  # Isolates long-running analysis
---
```

**Action Items**:
- [ ] Verify `context: fork` exists (Phase 0)
- [ ] Add to summary.md frontmatter only
- [ ] Test that forked execution completes successfully
- [ ] Verify result is returned to main context

**Done Criteria**:
- /summary runs in forked context
- Result visible to user after completion
- No regression on 2.0.x (graceful ignore if unsupported)

**Rollback**: Remove `context: fork` from frontmatter

### 2.2 Implement Agent-Scoped Hooks (If Verified)
**Status**: MEDIUM - New feature adoption
**Effort**: Medium

**IMPORTANT**: Prompt-type Stop hooks cannot enforce - they only remind.
For actual enforcement, use command-type hooks that can exit non-zero.

#### reviewer.md - Quality Reminder (NOT Enforcement)
```yaml
---
description: "Code reviewer"
hooks:
  Stop:
    - type: prompt
      prompt: |
        Reminder: Ensure your response includes:
        1. Score (0.0-10.0)
        2. Issues list if score < 9.5
        3. Actionable feedback
---
```

#### librarian.md - Permalink Logging (NOT Validation)
```yaml
---
description: "Documentation librarian"
hooks:
  PostToolUse:
    - type: command
      command: "${CLAUDE_PLUGIN_ROOT}/hooks/log-permalink.sh"
      matcher: "WebFetch"
---
```

**Action Items**:
- [ ] Verify agent-scoped hooks exist (Phase 0)
- [ ] Add reminder hook to reviewer.md
- [ ] Create log-permalink.sh (logging only, not blocking)
- [ ] Test hook execution in agent context
- [ ] Measure performance impact

**Done Criteria**:
- Hooks fire correctly in agent context
- No performance regression > 200ms per hook
- Graceful degradation on 2.0.x

**Rollback**: Remove hooks from agent frontmatter

### 2.3 Add `once: true` Session Initialization Hook (If Verified)
**Status**: LOW - Nice to have
**Effort**: Low

**Implementation in hooks.json**:
```json
{
  "SessionStart": [{
    "hooks": [{
      "type": "command",
      "command": "${CLAUDE_PLUGIN_ROOT}/hooks/session-init.sh",
      "once": true
    }]
  }]
}
```

**Action Items**:
- [ ] Verify `once: true` property exists (Phase 0)
- [ ] Create session-init.sh (creates .claude/sessions/ log)
- [ ] Test that hook only fires once per session
- [ ] Verify no impact on subsequent tool calls

**Done Criteria**:
- Hook fires exactly once per session
- Session logged to .claude/sessions/

**Rollback**: Remove SessionStart hook from hooks.json

### 2.4 Document Ctrl+B Backgrounding
**Status**: LOW - Documentation only
**Effort**: Low

**Action Items**:
- [ ] Add Ctrl+B note to /deepwork description
- [ ] Add Ctrl+B note to /ultrawork description
- [ ] Add to README.md tips section

**Done Criteria**:
- Documentation updated
- Users aware of Ctrl+B escape hatch

---

## Phase 3: Enhancement (Medium-term, Deferred Until Demand)

### 3.1 Safe Mode Hook - REVISED APPROACH
**Status**: DEFERRED - Implement only if user demand
**Effort**: Medium

**CRITICAL CHANGE**: Do NOT transform commands. Block and explain instead.

**Revised Implementation** (if implemented):
```bash
#!/bin/bash
# Hook that BLOCKS dangerous commands, does NOT transform them

INPUT="$1"
TOOL="$2"

# Block rm -rf (do NOT convert to rm -ri - causes interactive deadlock)
if [[ "$TOOL" == "Bash" && "$INPUT" =~ rm\ -rf ]]; then
  echo '{"decision": "block", "reason": "rm -rf blocked by safe-mode. Use rm with explicit paths."}'
  exit 0
fi

# Block force push
if [[ "$TOOL" == "Bash" && "$INPUT" =~ git\ push.*--force ]]; then
  echo '{"decision": "block", "reason": "git push --force blocked. Use standard push."}'
  exit 0
fi

# Default: allow
echo '{"decision": "allow"}'
```

**Why NOT transform**:
- `rm -ri` prompts on stdin - causes deadlock in non-interactive agent
- Silent transformation surprises users and breaks legitimate commands
- Block and explain is safer and more transparent

**Action Items** (if implemented):
- [ ] Create safe-mode-hook.sh (block, not transform)
- [ ] Add PreToolUse hook for Bash
- [ ] Create /safe-mode toggle command
- [ ] Test blocking behavior

**Rollback**: Remove hook from hooks.json

### 3.2 Create /skills/ Directory
**Status**: DEFERRED - Implement only if needed
**Effort**: Low

**Current Assessment**:
- Commands work fine in /commands/
- /skills/ adds structural overhead without proven benefit
- Defer until specific need arises

**Action Items** (if implemented):
- [ ] Create skills/ directory
- [ ] Move reusable patterns
- [ ] Add `user-invocable: false` to internal skills

### 3.3 Document Selective Agent Disabling
**Status**: LOW - Documentation only
**Effort**: Low

**Add to README**:
```markdown
## Selective Agent Disabling

Disable specific agents if you lack API access:

```bash
# Disable Oracle (requires Codex API)
claude --disallowedTools "Task(oh-my-claude:oracle)"

# Disable Librarian (requires web access)
claude --disallowedTools "Task(oh-my-claude:librarian)"
```
```

**Action Items**:
- [ ] Add "Selective Agent Disabling" section to README
- [ ] Document graceful degradation in orchestrator

---

## Test Matrix

| Command | Syntax Type | 2.0.x Works | 2.1.0 Works | Notes |
|---------|-------------|-------------|-------------|-------|
| /deepwork | YAML inline | ? | ? | Primary workflow |
| /ultrawork | YAML inline | ? | ? | Primary workflow |
| /save | Inline | ? | ? | `Read, Write, Bash(date:*)` |
| /load | Mixed | ? | ? | Test loading |
| /cancel-work | JSON array | ? | ? | `["Bash(...)", "Read"]` |
| /setup | Inline | ? | ? | `Bash(brew:*)` |
| /summary | Will add fork | ? | ? | Test context isolation |

---

## Rollback Triggers

Stop and revert if:
- YAML syntax breaks Claude Code 2.0.x compatibility
- Hook overhead increases Task response time > 200ms
- Forked context causes command failures
- Any regression in existing functionality

---

## Revised Implementation Order

```
Immediate: Phase 0 + Phase 1 (Verification + Compatibility)
├── 0.1 Feature existence verification (PREREQUISITE)
├── 1.1 Allowed-tools syntax compatibility test
├── 1.2 Variable substitution verification
└── 1.3 Model inheritance verification

After Verification: Phase 2 (Feature Adoption)
├── 2.1 context: fork for /summary ONLY
├── 2.2 Agent-scoped hooks (reminder, not enforcement)
├── 2.3 once: true session initialization
└── 2.4 Ctrl+B documentation

Deferred: Phase 3 (Enhancement)
├── 3.1 Safe mode hook (if user demand)
├── 3.2 /skills/ directory (if needed)
└── 3.3 Agent disabling documentation
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Features don't exist | Phase 0 verification before implementation |
| Fork context loss | Only fork /summary, not /orchestrator |
| Hook deadlock | Block dangerous commands, don't transform to interactive |
| Hook performance | Measure latency, rollback if > 200ms |
| 2.0.x regression | Test matrix for both versions |
| Over-engineering | Defer Phase 3 until proven need |

---

## Success Criteria

1. **Phase 0 Complete**: All features verified with evidence
2. **Compatibility**: All commands work with both 2.0.x and 2.1.0
3. **Syntax Validated**: Allowed-tools syntax decision documented
4. **context: fork**: /summary runs isolated (if feature exists)
5. **Documentation**: New features documented in README

---

## Answers to Review Questions

1. **Should /orchestrator also use context: fork?**
   **NO.** Orchestrator needs conversation context for coordination. Fork its subtasks (delegated agents), not the orchestrator itself.

2. **Is the safe-mode hook worth the complexity?**
   **DEFERRED.** If implemented, use block+explain approach, NOT silent transformation. The `rm -ri` approach is dangerous (interactive deadlock).

3. **Granular wildcard patterns?**
   **Use current granularity.** `Bash(git diff *)` vs `Bash(git *)` - maintain current patterns. Block dangerous subcommands via hooks if needed, not regex whitelists.

4. **Phase 2 reorder?**
   **No change needed.** Current order is logical: context:fork → hooks → once:true → docs.

---

## Reviewer Feedback Summary

| Reviewer | Score | Key Feedback |
|----------|-------|--------------|
| GPT-5.2 | 7.8 | Add test matrix, rollback plan, feature flags |
| Gemini-3 | 9.2 | rm -ri is dangerous, keep orchestrator in main context |
| Opus-4.5 | 7.2 | Verify features exist first, test before modify |

**Changes Made**:
1. Added Phase 0 (Feature Verification)
2. Added Test Matrix with 2.0.x and 2.1.0 columns
3. Added Rollback Triggers section
4. Changed safe-mode from transform to block approach
5. Decided: /orchestrator stays in main context
6. Changed 1.1 from "convert all" to "test, convert only if broken"
7. Clarified agent hooks are reminders, not enforcement
8. Added performance threshold (200ms)
9. Added backward compatibility requirement
