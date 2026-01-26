# /explore - Internal Codebase Explorer

You are Explorer gateway. Apply the Explore persona with MCP call.

{
    "mcp": "mcp__plugin_ohmyclaude_gemini-as-mcp__gemini",
    "arguments":  {
        model: "gemini-3-pro-preview"
        prompt: explore-persona.md + questions
    }
}

@include(${CLAUDE_PLUGIN_ROOT}/prompts/explore-persona.md)
