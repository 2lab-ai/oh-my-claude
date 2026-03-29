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

### 3. Gap Detection (Ouroboros Check)

**Before** comparing spec vs implementation, run the 5-type gap analysis. This catches directional problems that per-item checklists miss.

| Gap Type | What to Check |
|----------|--------------|
| `assumption_injection` | Does the PR add behavior/logic the issue never mentioned? (e.g., auth, caching, logging frameworks not in spec) |
| `scope_creep` | Does the PR implement features beyond the issue scope? (e.g., admin panel when only API was requested) |
| `direction_drift` | Is the overall architectural approach aligned with the issue's intent? (e.g., issue says "simple script" but PR builds a framework) |
| `missing_core` | Are ALL core deliverables from the issue actually present in the PR? |
| `over_engineering` | Is the abstraction level proportional to the problem? (e.g., DI container for a 3-endpoint CRUD) |

**For each gap found, report:**
```
- `[gap_type]`: [what was expected] → [what was implemented] → [correction needed]
```

### 4. Spec vs Implementation Comparison

Check each item below and report the results to the user:

- **Coverage**: Are all acceptance criteria from the issue spec implemented in the PR?
- **Accuracy**: Does the implementation match the spec's intent? (No over-implementation or omissions?)
- **Tests**: Do tests exist for the spec's core scenarios?
- **Scope**: Does the PR contain changes outside the issue scope?

### 5. Verdict

- **PASS**: All items match, no gaps → ready to merge
- **PARTIAL**: Some omissions or mismatches → specify missing items, additional work required
- **GAP_DETECTED**: Implementation drifts from original intent → list gaps with correction instructions, rework required
- **FAIL**: Core spec not implemented or implementation direction misaligned → rework required

**Verdict priority**: `GAP_DETECTED` > `FAIL` > `PARTIAL` > `PASS`

A gap is more severe than a quality issue — wrong direction wastes all effort. If gaps AND quality issues exist, report `GAP_DETECTED` and include quality issues as secondary findings.

When mismatches are found, be specific: "X exists in the issue but is missing from the PR" or "Y was done in the PR but is not in the issue spec."

If a bug is suspected in a FAIL or PARTIAL verdict → suggest switching to the **stv:debug skill**.

### Report Format

```markdown
## STV Verify Report

### Issue: [issue key/title]
### PR: [PR URL]

### Gap Analysis
- **Gaps Found**: [None | List]
  - `[gap_type]`: [expected] → [actual] → [correction]
- **Intent Alignment**: [ALIGNED | DRIFTED | MISSING_CORE]

### Spec Coverage
| Spec Item | Status | Notes |
|-----------|--------|-------|
| [item] | ✅/❌/⚠️ | [detail] |

### Verdict: [PASS | PARTIAL | GAP_DETECTED | FAIL]
### Action Required: [None | List of specific fixes]
```
