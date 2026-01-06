---
description: "Start Ralph Wiggum loop in current session"
argument-hint: "[--max-iterations N] [--completion-promise TEXT] PROMPT"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/setup-ralph-loop.sh)"]
hide-from-slash-command-tool: "true"
---

# Ralph Loop Command

Execute the setup script to initialize the Ralph loop:

```!
# Write prompt to temp file first to avoid complex piping issues with multi-line prompts
_tmp_prompt=$(mktemp) && cat > "$_tmp_prompt" <<'RALPH_ARGS_EOF'
$ARGUMENTS
RALPH_ARGS_EOF
export RALPH_PROMPT_B64=$(cat "$_tmp_prompt" | base64)
rm -f "$_tmp_prompt"
RALPH_NO_DEFAULT_PROMISE=1 "${CLAUDE_PLUGIN_ROOT}/scripts/setup-ralph-loop.sh"
```

Please work on the task. When you try to exit, the Ralph loop will feed the SAME PROMPT back to you for the next iteration. You'll see your previous work in files and git history, allowing you to iterate and improve.

CRITICAL RULE: If a completion promise is set, you may ONLY output it when the statement is completely and unequivocally TRUE. Do not output false promises to escape the loop, even if you think you're stuck or should exit for other reasons. The loop is designed to continue until genuine completion.
