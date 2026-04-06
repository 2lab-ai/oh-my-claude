---
name: stv-verify
description: Triggers on "check the PR", "is it implemented per the issue", "compare spec vs implementation", "compare JIRA and PR", "verify", "validate". Final checkpoint before PR merge using 3-dimensional verification (Completeness, Correctness, Coherence).
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

### 0. Determine Verification Dimensions

Before proceeding with detailed checks, determine which verification dimensions apply based on the artifacts available for this feature.

**Three Dimensions:**

| Dimension | What it Verifies | Required Artifacts |
|-----------|-----------------|-------------------|
| **Completeness** | Every task/requirement has corresponding code | Tasks or issue checklist |
| **Correctness** | Implementation matches spec intent + scenario tests exist | Spec/issue + PR |
| **Coherence** | Design decisions from spec/trace are reflected in code | Full STV artifacts (spec.md + trace.md + code) |

**Graceful Degradation:**

```
Available Artifacts → Dimensions Applied:
- Issue only (no spec/trace)     → Completeness only
- Issue + spec.md                → Completeness + Correctness
- Issue + spec.md + trace.md     → Completeness + Correctness + Coherence (full 3D)
```

The verifier MUST:
1. Detect which artifacts exist (check for docs/{feature}/spec.md, docs/{feature}/trace.md)
2. Announce which dimensions will be applied
3. Apply only the appropriate dimensions

### 3. Gap Detection (Ouroboros Check)

This step contributes to the **Correctness** dimension.

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

### 4. Spec vs Implementation Comparison (3-Dimensional)

Apply the dimensions determined in Step 0. Report results per dimension.

#### Completeness Check (always applied)
- Every acceptance criterion from issue → has corresponding code change
- Every task checkbox → has implementation
- Count: N/M requirements covered
- **Scope**: Does the PR contain changes outside the issue scope?

#### Correctness Check (only if spec.md exists)
- **Coverage**: Are all acceptance criteria from the issue spec implemented in the PR?
- **Accuracy**: Does the implementation match the spec's intent? (No over-implementation or omissions?)
- **Scenario-level test coverage**: Each spec scenario has at least one test
- Gap Detection results (from Step 3) feed into this dimension

#### Coherence Check (only if trace.md exists)
- Design decisions in spec.md Auto-Decisions section → reflected in code
- Architecture choices in trace.md Layer Flow → matches actual implementation structure
- Parameter transformation arrows in trace → verified in code
- Trade-offs documented in spec → honored in implementation

### 5. Verdict

- **PASS**: All items match, no gaps → ready to merge
- **PARTIAL**: Some omissions or mismatches → specify missing items, additional work required
- **GAP_DETECTED**: Implementation drifts from original intent → list gaps with correction instructions, rework required
- **FAIL**: Core spec not implemented or implementation direction misaligned → rework required

**Verdict priority**: `GAP_DETECTED` > `FAIL` > `PARTIAL` > `PASS`

#### Dimensional Assessment

Include per-dimension scores in the verdict:

```markdown
### Dimensional Assessment
| Dimension | Score | Notes |
|-----------|-------|-------|
| Completeness | ✅/⚠️/❌ | {N}/{M} requirements covered |
| Correctness | ✅/⚠️/❌/N/A | {detail} |
| Coherence | ✅/⚠️/❌/N/A | {detail} |
```

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

### Dimensional Assessment
| Dimension | Score | Notes |
|-----------|-------|-------|
| Completeness | ✅/⚠️/❌ | {N}/{M} requirements covered |
| Correctness | ✅/⚠️/❌/N/A | {detail} |
| Coherence | ✅/⚠️/❌/N/A | {detail} |

### Spec Coverage
| Spec Item | Status | Notes |
|-----------|--------|-------|
| [item] | ✅/❌/⚠️ | [detail] |

### Verdict: [PASS | PARTIAL | GAP_DETECTED | FAIL]
### Action Required: [None | List of specific fixes]
```
