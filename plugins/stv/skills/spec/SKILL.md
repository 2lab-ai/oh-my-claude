---
name: spec
description: "STV Phase 1: Proposal (WHY) -> Feature interview -> spec.md. PRD + Architecture decisions in one pass. Uses decision-gate to minimize questions. Supports non-linear flow (Actions not Phases) and Update vs New decision tree."
---

# STV Spec — Feature Spec Interview

> STV Phase 1: Feature interview → `docs/{feature}/spec.md`
> PRD (what to build) + Architecture (how to build) confirmed in a single pass.

---

## Decision Gate (MANDATORY)

**Read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` and apply it to every decision in this workflow.**

**Apply this gate to every decision. switching cost < small → autonomous judgment, == small → autonomous decision + report, >= medium → ask the user.**

---

## Step 0: Proposal — "Why are we doing this?"

Before diving into the spec interview, establish the WHY in 60 seconds. This prevents direction drift on complex features.

**Output a brief Proposal block (inline, not a separate file):**

```markdown
### Proposal
- **Why**: {1-2 sentences — the problem or opportunity that motivates this change}
- **What Changes**: {bullet list of what will be different}
- **Capabilities**: {new or modified capabilities this enables}
- **Impact**: {affected code areas, APIs, dependencies. BREAKING changes flagged}
```

**Rules:**
- If the user already provided a clear WHY → extract it, confirm, move on
- If WHY is unclear or absent → ask ONE question: "What problem does this solve, or what opportunity does this create?"
- Proposal is embedded in spec.md Section 1 (Overview), not a separate artifact
- Proposal takes < 1 minute. If it takes longer, the problem isn't understood yet → suggest `stv:explore` first

---

## Step 1-0: Input Analysis

1. **Interpret argument**:
   - File path → read and analyze
   - Feature name/description → use as starting point
   - Existing spec found → **update mode** (see Update vs New below)

2. **Explore codebase** (Agent:Explore):
   - Identify related existing code
   - Understand existing patterns, conventions, architecture
   - Map areas affected by this feature

### Update vs New Decision Tree

When an existing spec is detected, decide whether to UPDATE or create NEW:

```
Is the intent the same problem/goal?
├── YES → Is the scope still manageable?
│   ├── YES → UPDATE existing spec
│   └── NO (scope explosion) → NEW spec (link to original)
└── NO (intent changed) → NEW spec
    └── Can original spec be independently "completed"?
        ├── YES → Complete original, then NEW
        └── NO → Deprecate original, start NEW
```

**UPDATE mode**: Modify existing spec.md in-place. Record changes in a `## Spec Changelog` section.
**NEW mode**: Create a new `docs/{feature-v2}/spec.md`. Reference the original.

## Step 1-1: Business Interview — "What are we building?"

**Interview via AskUserQuestion.** Apply Decision Gate:
- **Can be decided autonomously** (clear pattern from existing code, tiny/small switching cost) → record in spec without asking
- **Needs user confirmation** (medium+ switching cost) → ask

Bundle 2-4 related questions into a single AskUserQuestion:

**Must cover:**
- User stories / core scenarios
- Acceptance Criteria
- Scope boundaries (In-Scope / Out-of-Scope)
- Non-functional requirements (performance, security, scalability)

**Decision Gate applied:**
- Clear patterns from existing code → autonomous decision + record in spec
- Business rules, user experience → ask the user

## Step 1-2: Architecture Interview — "How are we building it?"

**Must cover:**
- Layer structure (Controller → Handler → Service → DB)
- DB schema / Entity design
- API endpoint list + HTTP methods
- Integration points with existing code
- Error handling strategy
- Authentication/authorization model

**Decision Gate applied:**
- Following existing architecture patterns → autonomous decision
- Introducing new patterns, schema changes → ask with [Tier N ~N lines] label

### Interview Guidelines

**DO:**
- Bundle 2-4 questions into a single AskUserQuestion to minimize question count
- Ask specific questions based on codebase exploration results (include file names, function names)
- Provide a recommendation for each question (so user can just say "OK")
- Record autonomous decisions in the `### Auto-Decisions` section

**DON'T:**
- Ask things that can be answered from the codebase
- Ask more than 5 questions at once
- Ask Yes/No questions — present options instead

## Step 1-3: Spec Writing

After interview is complete (user confirmed or all dimensions covered):

### Output: `docs/{feature-name}/spec.md`

```markdown
# {Feature Name} — Spec

> STV Spec | Created: {date}

## 1. Overview

### Proposal
- **Why**: {1-2 sentences — the problem or opportunity}
- **What Changes**: {bullet list}
- **Capabilities**: {new/modified capabilities}
- **Impact**: {affected areas, BREAKING if applicable}

{1-2 paragraphs expanding on the above}

## 2. User Stories
- As a {actor}, I want {action}, so that {outcome}
- ...

## 3. Acceptance Criteria
- [ ] {criterion 1}
- [ ] {criterion 2}
- ...

## 4. Scope
### In-Scope
- ...
### Out-of-Scope
- ...

## 5. Architecture

### 5.1 Layer Structure
{Controller → Handler → Service → DB flow overview}

### 5.2 API Endpoints
| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| POST | /api/... | ...Create | ... |
| GET | /api/... | ...List | ... |
| ... | ... | ... | ... |

### 5.3 DB Schema
{Entity list + key fields}

### 5.4 Integration Points
{Connection points with existing systems}

## 6. Non-Functional Requirements
- Performance: ...
- Security: ...
- Scalability: ...

## 7. Auto-Decisions
{Content autonomously decided via Decision Gate. Includes tier and rationale}

| Decision | Tier | Rationale |
|----------|------|-----------|
| ... | tiny | ... |
| ... | small | ... |

## 8. Open Questions
{Remaining unresolved items. "None" if empty}

## 9. Spec Changelog
{Change history when spec is updated. Empty on initial creation.}

## 10. Next Step
→ Proceed with Vertical Trace via `stv:trace`
```

## Phase 1 Checklist

- [ ] User stories and acceptance criteria written per scenario
- [ ] Scope IN/OUT boundaries are clear
- [ ] DB schema defined at table/column/FK/index level
- [ ] API endpoints defined with method, path, request/response schema
- [ ] All decisions with switching cost >= medium (50+ lines) have human approval

## Actions, Not Phases

STV phases (spec → trace → work) are NOT a one-way waterfall. Going back is normal and expected.

**When to return to spec from later phases:**
- During `stv:trace`: discovered a missing scenario or ambiguous requirement → update spec
- During `stv:work`: implementation reveals a spec assumption was wrong → update spec
- After `stv:verify`: gap detected that traces back to a spec error → update spec

**How to return:**
1. Re-invoke `stv:spec` with the existing spec path
2. Update vs New decision tree applies
3. Spec Changelog records what changed and why
4. Downstream artifacts (trace.md, tests) are flagged for re-verification

**This is not failure. This is the Feedback Loop invariant in action.**

## Completion

1. Save spec.md to `docs/{feature-name}/spec.md`
2. Present spec summary + next step guidance to user
3. If Proposal WHY is weak or missing → warn user before proceeding
4. **Next skill guidance**: `Skill(skill="stv:trace")` or guide user to use `stv:trace docs/{feature-name}/spec.md`
