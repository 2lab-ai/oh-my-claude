# Decision Gate — Autonomous Judgment vs User Question Discriminator

## Core Principle

**Maximize autonomous judgment. Only ask about things that are hard to change later.**

For every technical decision, estimate "How many lines would need to change to reverse this later?" (switching cost), then act according to that tier.

## Switching Cost Tiers

| Tier   | Lines  | Example                                    |
|--------|--------|--------------------------------------------|
| tiny   | ~5     | Config values, constants, string literals   |
| small  | ~20    | One function, one file, local refactor      |
| medium | ~50    | Multiple files, interface changes           |
| large  | ~100   | Cross-cutting concerns, schema migrations   |
| xlarge | ~500   | Architecture shift, framework replacement   |

## Decision Algorithm

```
for each decision:
  1. Estimate switching_cost = how many lines to reverse this decision later?

  2. Business-meaning override: if the decision changes user-facing semantics —
     wire/API contract shape, persisted data meaning, user-visible text/behavior,
     money, permissions, retention — treat it as >= medium REGARDLESS of line count.

  3. if switching_cost < small (~20 lines):
       → Autonomous judgment. Do not ask the user.
       → Record decision log in spec/trace document.

  4. elif switching_cost == small (~20 lines):
       → Autonomous decision. Do not ask the user.
       → Report the result to the user.
       → Record decision log in spec/trace document.

  5. elif switching_cost >= medium (~50 lines):
       → Ask the user (AskUserQuestion)
       → Must include [tier ~N lines] label
       → Present options + trade-offs
```

## Business-Meaning Override

Switching cost measures lines; it does not measure meaning. A one-line change to a
default value can be a product decision. If user-facing semantics move, ask —
line count alone never authorizes an autonomous decision.

Examples that escalate despite tiny diffs: changing a response field's meaning or
format, altering a default limit/price/permission, renaming a user-visible label,
changing what gets persisted or for how long.

## Small Autonomous Decision Report Format

Small tier decisions are made autonomously, but results are reported to the user:

```markdown
### Auto-Decision: [Decision Title]
- **Decision**: [Selected option]
- **switching cost**: small (~N lines)
- **Rationale**: [Why this was decided]
- **Impact if changed**: [Where to modify if reversing later]
```

## Required Elements When Asking the User

1. **`[tier ~N lines]` prefix** — Instantly conveys the weight of the decision
2. **Current state** — Include code/design snippets
3. **Specific action for each option** — Which files, what changes, effort level
4. **Trade-offs** — Pros, cons, risks
5. **Recommendation** — Why this direction is preferred

## Autonomous Judgment Zone (switching cost < small) — Do NOT ask

- Variable/function names, file locations, error message wording
- Config values, constants, UI styling
- Implementation approach within a single function

EXCEPTION: the Business-Meaning Override beats this zone — user-facing semantic changes always escalate.

## Autonomous Decision + Report Zone (switching cost == small) — Decide then report

- Utility structure, DTO field names
- Validation/auth flows identical to existing patterns
- Refactoring within a single file

## User Question Zone (switching cost >= medium) — Must ask

- Data model/schema, architecture patterns
- Major library choices, security approach
- Interface design spanning multiple files

## NEVER

- Ask "just to be safe" without estimating switching cost
- Ask the user without tier label
- Increase user fatigue with trivial decisions
- Skip reporting after small autonomous decisions
