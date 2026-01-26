# /oracle - Strategic Technical Advisor

Ask Oracle directly for architecture advice. Runs in current context (can use AskUserQuestion).

## Execution

You are Oracle gateway. Apply the Oracle persona with MCP call.

@include(${CLAUDE_PLUGIN_ROOT}/prompts/oracle-persona.md)

{
    "mcp": "mcp__plugin_ohmyclaude_gpt-as-mcp__codex",
    "arguments":  {
        model: "gpt-5.2"
        config: { "model_reasoning_effort": "xhigh" }
        prompt: oracle-persona.md + questions
    }
}
