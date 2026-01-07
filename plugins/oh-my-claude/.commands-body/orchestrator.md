# /orchestrator - Multi-Agent Work Coordinator

Coordinate specialized AI agents for complex tasks. Runs in current context (can use AskUserQuestion).

## Usage

```bash
/orchestrator "Build REST API for users"
/orchestrator "Refactor the auth module"
/orchestrator "Fix the failing tests"
```

## Key Difference from /ultrawork

- **`/orchestrator`**: Runs in current context, can interact with user via `AskUserQuestion`
- **`/ultrawork`**: Runs in Ralph loop, autonomous, no user interaction

## Execution

You ARE the Orchestrator now. Apply the workflow:

@include(${CLAUDE_PLUGIN_ROOT}/prompts/orchestrator-workflow.md)

## Task: $ARGUMENTS

Begin:
1. **AskUserQuestion** if anything unclear
2. **TodoWrite** to plan all steps
3. Work, delegating to agents as needed
