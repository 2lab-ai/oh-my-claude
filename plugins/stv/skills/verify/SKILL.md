---
name: stv-verify
description: Triggers on "check the PR", "is it implemented per the issue", "compare spec vs implementation", "compare JIRA and PR", "verify", "validate". Final checkpoint before PR merge.
---

# STV: Verify

Conformance Gate that cross-checks the spec defined in a 'issue'(Jira, Linear, github issue) against actual code changes in a PR.

---

## Input

Collect the following two items from the user:
- **Issue** User should provided issue url or issue contents. If not ask to user provide mcp to get that issue or that issue full contents.
- **PR URL** (e.g., `https://github.com/xxx/yyy/pull/123`)

Do not proceed unless both are provided.

## Verification Procedure

### 1. Extract Spec from Issue

Read the issue and organize the following:
- **AS-IS**: Current state / problem definition
- **TO-BE**: Expected result / implementation goal
- **Implementation Spec**: Acceptance criteria, technical requirements, constraints

If AS-IS/TO-BE are not explicitly stated in the issue, infer them from the issue description and confirm with the user: "This is how I understood it — is this correct?"

### 2. Extract Changes from PR

Read the PR diff via MCP and organize the following:
- **Changed file list** with a summary of changes per file
- **Core logic changes**: Newly added or modified business logic
- **Test changes**: Added/modified test cases

### 3. Spec vs Implementation Comparison

Check each item below and report the results to the user:

- **Coverage**: Are all acceptance criteria from the JIRA spec implemented in the PR?
- **Accuracy**: Does the implementation match the spec's intent? (No over-implementation or omissions?)
- **Tests**: Do tests exist for the spec's core scenarios?
- **Scope**: Does the PR contain changes outside the issue scope?

### 4. Verdict

- **PASS**: All items match → ready to merge
- **PARTIAL**: Some omissions or mismatches → specify missing items, additional work required
- **FAIL**: Core spec not implemented or implementation direction misaligned → rework required

When mismatches are found, be specific: "X exists in JIRA but is missing from the PR" or "Y was done in the PR but is not in the JIRA spec."

If a bug is suspected in a FAIL or PARTIAL verdict → suggest switching to the **stv:debug skill**.
