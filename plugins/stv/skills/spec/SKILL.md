---
name: spec
description: "STV Phase 1: Feature interview -> spec.md. PRD + Architecture decisions in one pass. Uses decision-gate to minimize questions."
---

# STV Spec — Feature Spec Interview

> STV Phase 1: Feature interview → `docs/{feature}/spec.md`
> PRD (what to build) + Architecture (how to build) confirmed in a single pass.

---

## Decision Gate (MANDATORY)

**Read `${CLAUDE_PLUGIN_ROOT}/prompts/decision-gate.md` and apply it to every decision in this workflow.**

**Apply this gate to every decision. switching cost < small → autonomous judgment, == small → autonomous decision + report, >= medium → ask the user.**

---

## Step 1-0: Input Analysis

1. **Interpret argument**:
   - File path → read and analyze
   - Feature name/description → use as starting point
   - Existing spec found → update mode

2. **Explore codebase** (Agent:Explore):
   - Identify related existing code
   - Understand existing patterns, conventions, architecture
   - Map areas affected by this feature

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
{1-2 paragraphs: what this feature is and why it's needed}

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

## 9. Next Step
→ Proceed with Vertical Trace via `stv:trace`
```

## Phase 1 Checklist

- [ ] User stories and acceptance criteria written per scenario
- [ ] Scope IN/OUT boundaries are clear
- [ ] DB schema defined at table/column/FK/index level
- [ ] API endpoints defined with method, path, request/response schema
- [ ] All decisions with switching cost >= medium (50+ lines) have human approval

## Completion

1. Save spec.md to `docs/{feature-name}/spec.md`
2. Present spec summary + next step guidance to user
3. **Next skill guidance**: `Skill(skill="stv:trace")` or guide user to use `stv:trace docs/{feature-name}/spec.md`
