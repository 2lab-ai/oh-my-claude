# /pr-summary - Multi-Perspective PR Executive Summary Generator

Generate comprehensive, production-quality executive summaries for Pull Requests.
Output is saved to `./docs/pr-summary/{PR_NUMBER}-{sanitized-title}.md`

## Core Philosophy

**Stakeholders are INFERRED, not predefined.** The type of code changes determines who needs to know what.

---

## Phase 1: Data Collection

### 1.1 Parse Arguments

```
PR_IDENTIFIER = $ARGUMENTS (PR number or full URL)
```

### 1.2 Fetch PR Data

Execute these commands to gather PR information:

```bash
# Extract PR number from URL if needed
PR_NUM=$(echo "$PR_IDENTIFIER" | grep -oE '[0-9]+$' || echo "$PR_IDENTIFIER")

# Get PR metadata (JSON)
gh pr view $PR_NUM --json number,title,author,baseRefName,headRefName,state,createdAt,additions,deletions,files,body,commits,url

# Get full diff
gh pr diff $PR_NUM
```

### 1.3 Ensure Output Directory

```bash
mkdir -p ./docs/pr-summary
```

---

## Phase 2: Change Classification

### 2.1 Detection Rules

Classify each changed file using these patterns:

| Category | File Patterns | Content Signals | Criticality |
|----------|---------------|-----------------|-------------|
| **API/Controller** | `*Controller*`, `controller/`, `routes/`, `api/`, `endpoints/` | `[HttpGet]`, `[HttpPost]`, `@Get`, `router.` | 2.5 |
| **Entity/Model** | `*.entity.*`, `entities/`, `models/`, `domain/` | `public class`, `@Entity`, `interface` | 1.5 |
| **Store/Repository** | `*Store*`, `*Repository*`, `repository/`, `dao/`, `store/` | `async Task`, `SELECT`, `INSERT` | 2.0 |
| **Service/UseCase** | `*Service*`, `service/`, `usecase/`, `application/` | Business logic | 1.5 |
| **Processing/Handler** | `*Module*`, `*Handler*`, `*Processor*`, `handlers/` | Event handling, async processing | 2.0 |
| **Migration/Schema** | `migration/`, `*.sql`, `schema` | `CREATE TABLE`, `ALTER TABLE`, `ADD COLUMN` | 2.5 |
| **Config/Infra** | `.env*`, `config/`, `docker*`, `k8s/`, `*.yaml` | Environment variables | 1.5 |
| **Contract/DTO** | `*Request*`, `*Response*`, `*Dto*`, `contracts/` | API contracts | 2.0 |
| **Test** | `test/`, `spec/`, `*.test.*`, `*.spec.*` | `describe`, `it`, `Test` | 0.5 |
| **Documentation** | `*.md`, `docs/`, `swagger/`, `openapi` | Markdown, API docs | 0.5 |

### 2.2 Stakeholder Inference

Based on classified changes, determine relevant stakeholders:

| Change Profile | Primary View | Secondary Views |
|----------------|--------------|-----------------|
| API + Entity + Store | Implementation Developer | API Consumer |
| API only (new endpoints) | API Consumer | Implementation Developer |
| Internal refactor (Service/Store) | Implementation Developer | - |
| Migration + Entity | Implementation Developer | DevOps (deployment order) |
| Config/Infra changes | DevOps | Implementation Developer |
| Security (auth/guard) | Security + Implementation | API Consumer |

---

## Phase 3: Document Generation

### 3.1 Output File

Save to: `./docs/pr-summary/{PR_NUMBER}-{sanitized-title}.md`

Example: `./docs/pr-summary/583-crypto-deposit-bonus.md`

### 3.2 Required Document Structure

Generate the following structure. **Quality must match the example level.**

```markdown
# {TICKET-ID}: {Feature Title} - Executive Summary

> **PR**: [#{number}]({url})
> **Branch**: `{head}` → `{base}`
> **Status**: {Open|Merged|Closed}
> **Created**: {YYYY-MM-DD}

---

## Table of Contents

- [TL;DR](#tldr)
- [1. Implementation Developer View](#1-implementation-developer-view)
- [2. API Consumer View](#2-api-consumer-view) (if API changes)
- [3. Code-Level View](#3-code-level-view)
- [Summary](#summary)

---

## TL;DR

| Item | Description |
|------|-------------|
| **What** | {One sentence - specific, no jargon} |
| **Why** | {Business/technical justification} |
| **How** | {Key technical approach - mention patterns used} |
| **Impact** | +{additions} / -{deletions} lines, {N} files |
| **Quality** | {Review status or score if available} |

### Quick Flow
```
{Source} → {Action 1} → {Action 2} → {Result}
     │           │            │           │
     └─ detail   └─ detail    └─ detail   └─ detail
```

---

## 1. Implementation Developer View

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         {Feature Name} Flow                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Phase 1: {Name}]                                                      │
│  ┌──────────────┐              ┌───────────────────┐                    │
│  │ {Component}  │ ──────────►  │ {Component}       │                    │
│  └──────────────┘              └─────────┬─────────┘                    │
│                                          │                              │
│                                          ▼                              │
│                        ┌────────────────────────────────────┐           │
│                        │ {Key Data Structure/Table}         │           │
│                        │ ├─ field1 = value                  │           │
│                        │ └─ field2 = value                  │           │
│                        └────────────────────────────────────┘           │
│                                                                         │
│  [Phase 2: {Name}]                                                      │
│  ...                                                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Core Design Principles

#### 1. {Pattern Name} (e.g., CAS, Idempotency, Locking)
```{language}
// Code example showing the pattern
```

#### 2. {Another Pattern}
- Description of the pattern
- Why it's used

#### 3. {Validation/Safety Checks}
| Check | Purpose |
|-------|---------|
| `condition1` | Reason |
| `condition2` | Reason |

### Key Files & Responsibilities

| File | Role | Lines Changed |
|------|------|---------------|
| `path/to/file.ext` | Brief description | +N/-M |
| `path/to/file2.ext` | Brief description | +N/-M |

---

## 2. API Consumer View

(Include this section if API changes are detected)

### API Changes

#### Affected Endpoints

| Service | Endpoint |
|---------|----------|
| {ServiceName} | `{METHOD} /api/path` |

#### New Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `paramName` | `type` | Yes/No | Description |

#### New Response Fields

```json
{
  "existingField": "...",

  // ✅ NEW: {Feature Name}
  "newField1": "type - description",
  "newField2": "type - description"
}
```

### Usage Scenarios

#### Scenario 1: {Happy Path}
```http
{METHOD} /api/path?param=value
Authorization: Bearer <token>
```

**Response (200)**:
```json
{ "result": "..." }
```

#### Scenario 2: {Edge Case}
```http
{METHOD} /api/path?param=edgeValue
```

**Result**: {Description of behavior}

### Input Validation

| Input | Behavior |
|-------|----------|
| Valid value | Normal processing |
| Edge case | Specific handling |
| Invalid | Error response |

### State Lifecycle (if applicable)

```
┌────────────────────────────────────────────────────────────────────┐
│                       {Feature} Lifecycle                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  [1. State A]         [2. State B]         [3. State C]            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │ Component   │     │ Component   │     │ Component   │           │
│  │ .field      │────►│ .field      │────►│ .field      │           │
│  └─────────────┘     └─────────────┘     └─────────────┘           │
│        │                   │                   │                   │
│        │ (trigger)         │ (trigger)         │ (trigger)         │
│        ▼                   ▼                   ▼                   │
│    {Action}            {Action}            {Action}                │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Important Considerations

- {Caching behavior}
- {Idempotency guarantees}
- {Error handling}

---

## 3. Code-Level View

### A. Entity Layer

#### `{filename}.{ext}` (+N lines)
```{language}
/// <summary>
/// Description
/// </summary>
public Type PropertyName { get; set; }
```

### B. Store/Repository Layer

#### `{filename}.{ext}` (+N lines)

**{Method Name}** - {Purpose}
```{language}
public async Task<ResultType> MethodName(params)
{
    // Key implementation with comments
}
```

### C. Service/Processing Layer

#### `{filename}.{ext}` (+N/-M lines)

**{Method} Changes**
```{language}
// Before: {brief description}
// After: {brief description with key change}

await NewMethodCall(...);
```

### D. API/Controller Layer

#### `{filename}.{ext}` (+N/-M lines)
```{language}
[HttpGet("endpoint")]
public async Task<ActionResult<ResponseType>> MethodName(
    Type existingParam,
    Type? newParam)  // ✅ New parameter
{
    // Key logic
}
```

### Database Schema Changes

#### {table_name}
| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `new_column` | `type` | NULL | Purpose |

---

## Summary

### Change Statistics

| Layer | Files | Additions | Deletions |
|-------|-------|-----------|-----------|
| Entity | N | +X | -Y |
| Store | N | +X | -Y |
| Service | N | +X | -Y |
| Controller | N | +X | -Y |
| **Total** | **N** | **+X** | **-Y** |

### Quality Metrics

| Metric | Value |
|--------|-------|
| Key Patterns | {List patterns used} |
| Test Coverage | {If available} |

### Remaining Work

- [ ] {Any TODOs found in code}
- [ ] {Follow-up items}

---

*Generated: {YYYY-MM-DD}*
```

---

## Phase 4: Quality Requirements

### ASCII Diagram Standards

Use these characters for clean diagrams:
- Box: `┌ ┐ └ ┘ ─ │ ├ ┤ ┬ ┴ ┼`
- Arrows: `→ ← ↑ ↓ ► ▼ ▲ ◄`
- Max width: 80 characters

### Code Snippet Standards

1. Include language identifier
2. Add inline comments for complex logic
3. Show only KEY changes, not entire files
4. Use `// ✅ NEW` or `// 🔄 MODIFIED` markers
5. Include method signatures with parameter types

### Content Standards

1. **Be specific**: Exact file names, method names, line counts
2. **Show patterns**: Identify and explain design patterns (CAS, idempotency, etc.)
3. **Include validation**: Document all validation/safety checks
4. **Lifecycle diagrams**: For stateful features, show state transitions
5. **Code examples**: Real snippets from the diff, not pseudo-code

---

## Phase 5: Save Output

After generating the summary:

1. Create filename: `{PR_NUMBER}-{sanitized-title}.md`
   - Sanitize: lowercase, replace spaces with `-`, remove special chars
   - Example: `583-crypto-deposit-bonus.md`

2. Save to: `./docs/pr-summary/`

3. Confirm: Output the file path when complete

```bash
# Example output
echo "Summary saved to: ./docs/pr-summary/583-crypto-deposit-bonus.md"
```

---

## Execution

### Task: $ARGUMENTS

1. **Fetch PR data** using gh CLI commands
2. **Classify changes** by file patterns and content
3. **Infer stakeholders** based on change profile
4. **Generate document** matching the quality standards above
5. **Save to file** in `./docs/pr-summary/`
6. **Report completion** with file path

If PR identifier is unclear, use AskUserQuestion first.
