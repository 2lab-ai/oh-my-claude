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

**Always read commands body** even if you knew it.**

**ALWAYS Verify all @include files are read recursively before proceeding. Nested @includes must also be read.**

# Boot Sequence

Execute the setup script to initialize the Ralph loop with auto-completion:
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
@include(${CLAUDE_PLUGIN_ROOT}/.commands-body/deepwork.md)

**ALWAYS Verify all @include files are read recursively before proceeding. Nested @includes must also be read.**
