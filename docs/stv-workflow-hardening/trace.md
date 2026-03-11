# STV Workflow Hardening — Vertical Trace

> STV Trace | Created: 2026-03-06
> Spec: docs/stv-workflow-hardening/spec.md

## Table of Contents

1. [Scenario 1 — Leftover Work Routes to Execution](#scenario-1--leftover-work-routes-to-execution)
2. [Scenario 2 — Bundle Scope Persists End-to-End](#scenario-2--bundle-scope-persists-end-to-end)
3. [Scenario 3 — Targeted Work Uses One Status Schema](#scenario-3--targeted-work-uses-one-status-schema)
4. [Scenario 4 — Planning Depth Rules Align](#scenario-4--planning-depth-rules-align)
5. [Scenario 5 — Discovery and Portability Guidance Is Explicit](#scenario-5--discovery-and-portability-guidance-is-explicit)

---

## Scenario 1 — Leftover Work Routes to Execution

### 1. API Entry

- HTTP Method: SKILL
- Path: `what-to-work`
- Auth/AuthZ: None

### 2. Input

- Request payload:
  ```json
  {
    "traceFiles": "docs/*/trace.md",
    "unfinishedScenarios": "0..N rows from Implementation Status",
    "estimatedSizes": "tiny|small|medium|large|xlarge"
  }
  ```
- Validation rules:
  - `Implementation Status` rows must be readable from each trace file.
  - Any backlog with at least one unfinished scenario remains execution-eligible.
  - `plan-new-task` is selected only when the unfinished inventory is empty or explicitly bypassed.

### 3. Layer Flow

#### 3a. Controller/Handler

- Entry skill reads `docs/*/trace.md` and extracts unfinished scenarios.
- Transformation rules:
  - `docs/*/trace.md` rows -> `unfinishedInventory[]`
  - `unfinishedInventory[]` -> `routeDecision`

#### 3b. Service

- Routing logic classifies leftovers as executable work, including small and medium tails.
- `what-we-have-to-work` receives the unfinished inventory when any work remains.
- `plan-new-task` receives control only when no unfinished scenarios remain.
- Transformation rules:
  - `unfinishedInventory[]` -> `executionBacklog`
  - `executionBacklog` -> `bundleProposalMode`
  - `emptyInventory` -> `newTaskPlanningMode`

#### 3c. Repository/DB

- File persistence boundary is the STV documentation set.
- Persisted files:
  - `plugins/stv/skills/what-to-work/SKILL.md`
  - `plugins/stv/skills/what-we-have-to-work/SKILL.md`
  - `plugins/stv/skills/plan-new-task/SKILL.md`
  - `plugins/stv/README.md`
- Mapping:
  - `routeDecision` -> routing examples and rules in markdown

### 4. Side Effects

- UPDATE: `plugins/stv/skills/what-to-work/SKILL.md` route criteria
- UPDATE: `plugins/stv/skills/what-we-have-to-work/SKILL.md` leftover sweep guidance
- UPDATE: `plugins/stv/skills/plan-new-task/SKILL.md` empty-backlog precondition
- UPDATE: `plugins/stv/README.md` flow diagram and backlog guidance

### 5. Error Paths

- Missing status table -> fall back to explicit "trace format mismatch" error instead of silent planning
- Inconsistent status labels -> instruct maintainer to normalize schema before routing
- Empty scan result due to glob failure -> do not assume backlog is empty

### 6. Output

- Success status code: N/A
- Response schema:
  ```json
  {
    "route": "what-we-have-to-work | plan-new-task",
    "reason": "unfinished work exists | backlog empty",
    "unfinishedCount": 3
  }
  ```

### 7. Observability [Optional]

- User-facing route summary includes unfinished count and rationale
- README flow diagram matches the routing behavior described in the skill

### Contract Tests (RED)

| Test Name | Category | Trace Reference |
|-----------|----------|-----------------|
| `WhatToWork_RoutesLeftoversToExecution_HappyPath` | Happy Path | Scenario 1, Sections 3 and 6 |
| `WhatToWork_DoesNotPlanNewTaskWhenLeftoversExist_SadPath` | Sad Path | Scenario 1, Section 5 |
| `WhatToWork_UpdatesRoutingDocs_SideEffect` | Side-Effect | Scenario 1, Section 4 |
| `WhatToWork_BacklogRowsToRouteDecision_Contract` | Contract | Scenario 1, Section 3, `docs/*/trace.md` rows -> `routeDecision` |

---

## Scenario 2 — Bundle Scope Persists End-to-End

### 1. API Entry

- HTTP Method: SKILL
- Path: `what-we-have-to-work`
- Auth/AuthZ: None

### 2. Input

- Request payload:
  ```json
  {
    "selectedBundle": {
      "trace_path": "docs/{feature}/trace.md",
      "scenario_ids": ["1", "2"],
      "size": "large",
      "rationale": "shared code area"
    }
  }
  ```
- Validation rules:
  - `trace_path` must resolve to an existing trace file.
  - `scenario_ids` must be non-empty and present in the target trace.
  - `do-work` must prefer provided bundle scope over project-wide scanning.

### 3. Layer Flow

#### 3a. Controller/Handler

- `what-we-have-to-work` presents bundles and captures the selected one.
- Transformation rules:
  - `bundleOption` -> `selectedBundle`
  - `selectedBundle.trace_path` -> `doWorkInput.trace_path`
  - `selectedBundle.scenario_ids` -> `doWorkInput.scenario_ids`

#### 3b. Service

- `do-work` accepts explicit scope and skips global trace discovery when scope is already provided.
- `work` receives the same targeted scope and iterates only selected scenarios.
- Transformation rules:
  - `selectedBundle` -> `doWorkScope`
  - `doWorkScope` -> `workScope`
  - `workScope.scenario_ids` -> `targetedScenarioLoop`

#### 3c. Repository/DB

- Persisted files:
  - `plugins/stv/skills/what-we-have-to-work/SKILL.md`
  - `plugins/stv/skills/do-work/SKILL.md`
  - `plugins/stv/skills/work/SKILL.md`
  - `plugins/stv/README.md`
- Mapping:
  - `selectedBundle` -> examples, preconditions, and invocation contracts in markdown

### 4. Side Effects

- UPDATE: bundle output template to include `trace_path` and `scenario_ids`
- UPDATE: `do-work` preconditions and phase A logic
- UPDATE: `work` input contract to accept targeted scope
- UPDATE: README skill flow diagram and quick start notes

### 5. Error Paths

- Missing `scenario_ids` -> reject bundle handoff
- Scenario id not found in trace -> stop with targeted-scope mismatch error
- `do-work` rescans entire repo despite explicit scope -> contract violation to be fixed in docs

### 6. Output

- Success status code: N/A
- Response schema:
  ```json
  {
    "trace_path": "docs/{feature}/trace.md",
    "scenario_ids": ["1", "2"],
    "mode": "targeted",
    "nextSkill": "work"
  }
  ```

### 7. Observability [Optional]

- User-facing execution report includes selected bundle scope
- Resume guidance echoes the same `trace_path` and `scenario_ids`

### Contract Tests (RED)

| Test Name | Category | Trace Reference |
|-----------|----------|-----------------|
| `SelectedBundle_PersistsThroughDoWork_HappyPath` | Happy Path | Scenario 2, Sections 3 and 6 |
| `SelectedBundle_RejectsUnknownScenarioIds_SadPath` | Sad Path | Scenario 2, Section 5 |
| `SelectedBundle_UpdatesExecutionDocs_SideEffect` | Side-Effect | Scenario 2, Section 4 |
| `SelectedBundle_ToWorkScope_Contract` | Contract | Scenario 2, Section 3, `selectedBundle.scenario_ids` -> `targetedScenarioLoop` |

---

## Scenario 3 — Targeted Work Uses One Status Schema

### 1. API Entry

- HTTP Method: SKILL
- Path: `work`
- Auth/AuthZ: None

### 2. Input

- Request payload:
  ```json
  {
    "trace_path": "docs/{feature}/trace.md",
    "scenario_ids": ["2"],
    "implementation_status": "Scenario | Trace | Tests | Verify | Status"
  }
  ```
- Validation rules:
  - Status rows use the unified five-column schema.
  - `work` can operate on all scenarios when `scenario_ids` is omitted.
  - `work` can operate on targeted scenarios when `scenario_ids` is provided.

### 3. Layer Flow

#### 3a. Controller/Handler

- `work` loads trace metadata and resolves targeted rows.
- Transformation rules:
  - `trace.md` -> `scenarioInventory[]`
  - `scenario_ids[]` -> `targetedRows[]`
  - `targetedRows[]` -> `verifyQueue[]`

#### 3b. Service

- The scenario loop operates on `verifyQueue[]`, not implicitly on all rows.
- Status writes use one schema across `trace` output, `work` updates, and README examples.
- Transformation rules:
  - `verifyQueue[]` -> `greenRows[]`
  - `greenRows[]` -> `statusRows[]`
  - `statusRows[]` -> `Scenario | Trace | Tests | Verify | Status`

#### 3c. Repository/DB

- Persisted files:
  - `plugins/stv/skills/trace/SKILL.md`
  - `plugins/stv/skills/work/SKILL.md`
  - `plugins/stv/README.md`
- Mapping:
  - `statusRows[]` -> markdown tables and examples

### 4. Side Effects

- UPDATE: `trace` output template
- UPDATE: `work` completion template and verify loop guidance
- UPDATE: README `trace.md is the Task List` section

### 5. Error Paths

- Missing `Verify` column -> explicit schema mismatch
- Targeted scenario omitted from status updates -> targeted execution bug
- Verification fails but status becomes `Complete` -> forbidden completion path

### 6. Output

- Success status code: N/A
- Response schema:
  ```json
  {
    "updatedRows": [
      {
        "scenario": "2. Commission plan creation",
        "trace": "done",
        "tests": "GREEN",
        "verify": "Verified",
        "status": "Complete"
      }
    ]
  }
  ```

### 7. Observability [Optional]

- Completion report echoes the same status columns written to `trace.md`
- README sample table matches the skill templates exactly

### Contract Tests (RED)

| Test Name | Category | Trace Reference |
|-----------|----------|-----------------|
| `Work_TargetedScenarioUpdatesUnifiedStatus_HappyPath` | Happy Path | Scenario 3, Sections 3 and 6 |
| `Work_RejectsSchemaMismatch_SadPath` | Sad Path | Scenario 3, Section 5 |
| `Work_RewritesStatusExamples_SideEffect` | Side-Effect | Scenario 3, Section 4 |
| `TargetedRows_ToStatusRows_Contract` | Contract | Scenario 3, Section 3, `scenario_ids[]` -> `statusRows[]` |

---

## Scenario 4 — Planning Depth Rules Align

### 1. API Entry

- HTTP Method: SKILL
- Path: `spec` / `trace`
- Auth/AuthZ: None

### 2. Input

- Request payload:
  ```json
  {
    "featureIdea": "workflow hardening",
    "specChecklist": "DB detail, request/response schema, open questions",
    "traceRule": "full vs compact trace",
    "decisionGate": "switching cost plus business meaning"
  }
  ```
- Validation rules:
  - `spec` template depth matches its checklist or explicitly marks sections as `N/A`.
  - `trace` and README use the same compact-trace rule.
  - `decision-gate` escalates user-facing semantic changes even when line count is small.

### 3. Layer Flow

#### 3a. Controller/Handler

- `spec` collects requirements and emits sections with explicit depth expectations.
- Transformation rules:
  - `featureIdea` -> `specSections`
  - `specChecklist` -> `specTemplateDepth`

#### 3b. Service

- `trace` selects full trace for side effects, branching errors, or transformation chains; compact trace is allowed for simple read-only flows.
- `decision-gate` supplements switching cost with business-meaning risk.
- Transformation rules:
  - `scenarioCharacteristics` -> `traceMode`
  - `decisionContext` -> `askOrDecide`
  - `userFacingSemantics` -> `mustAsk`

#### 3c. Repository/DB

- Persisted files:
  - `plugins/stv/skills/spec/SKILL.md`
  - `plugins/stv/skills/trace/SKILL.md`
  - `plugins/stv/prompts/decision-gate.md`
  - `plugins/stv/README.md`
- Mapping:
  - `traceMode` -> README FAQ and trace skill rules
  - `askOrDecide` -> prompt algorithm text

### 4. Side Effects

- UPDATE: `spec` template and checklist language
- UPDATE: `trace` granularity guidance
- UPDATE: `decision-gate` algorithm and examples
- UPDATE: README FAQ and methodology sections

### 5. Error Paths

- Full trace required but compact trace selected -> missing contract detail
- Compact trace allowed but full trace is forced -> planning overhead without added value
- Business semantic change treated as tiny due only to line count -> incorrect autonomous decision

### 6. Output

- Success status code: N/A
- Response schema:
  ```json
  {
    "specTemplate": "aligned",
    "traceGranularityRule": "shared",
    "decisionGate": "switching-cost-plus-business-risk"
  }
  ```

### 7. Observability [Optional]

- README FAQ examples and skill guidance produce the same answer to the same scenario
- Small autonomous decisions continue to be reported with rationale

### Contract Tests (RED)

| Test Name | Category | Trace Reference |
|-----------|----------|-----------------|
| `PlanningRules_AlignAcrossSpecTraceAndPrompt_HappyPath` | Happy Path | Scenario 4, Sections 3 and 6 |
| `DecisionGate_EscalatesSemanticRisk_SadPath` | Sad Path | Scenario 4, Section 5 |
| `PlanningRules_UpdateSharedDocs_SideEffect` | Side-Effect | Scenario 4, Section 4 |
| `ScenarioCharacteristics_ToTraceMode_Contract` | Contract | Scenario 4, Section 3, `scenarioCharacteristics` -> `traceMode` |

---

## Scenario 5 — Discovery and Portability Guidance Is Explicit

### 1. API Entry

- HTTP Method: SKILL
- Path: skill discovery / README quick start
- Auth/AuthZ: None

### 2. Input

- Request payload:
  ```json
  {
    "skillDescriptions": "frontmatter descriptions",
    "quickStart": "README commands",
    "environmentCapabilities": "plugin slash commands | plain skill names"
  }
  ```
- Validation rules:
  - Descriptions start with `Use when ...` and describe trigger conditions only.
  - README separates methodology guidance from plugin-specific invocation.
  - Host-specific actions such as commit/push or `/compact` are labeled optional and environment-dependent.

### 3. Layer Flow

#### 3a. Controller/Handler

- Discovery layer scans frontmatter descriptions before loading full skills.
- Transformation rules:
  - `frontmatter.description` -> `skillSelection`
  - `quickStartExample` -> `invocationExpectation`

#### 3b. Service

- README and skill docs steer the agent toward the correct environment-specific invocation.
- `do-work` describes quality gates as required, but git finalization and compaction as optional environment steps.
- Transformation rules:
  - `invocationExpectation` -> `pluginSpecificPath | genericPath`
  - `environmentCapabilities` -> `safeNextStep`

#### 3c. Repository/DB

- Persisted files:
  - `plugins/stv/README.md`
  - `plugins/stv/skills/spec/SKILL.md`
  - `plugins/stv/skills/trace/SKILL.md`
  - `plugins/stv/skills/work/SKILL.md`
  - `plugins/stv/skills/new-task/SKILL.md`
  - `plugins/stv/skills/do-work/SKILL.md`
  - `plugins/stv/skills/what-to-work/SKILL.md`
  - `plugins/stv/skills/what-we-have-to-work/SKILL.md`
  - `plugins/stv/skills/plan-new-task/SKILL.md`
- Mapping:
  - `skillSelection` -> frontmatter descriptions
  - `safeNextStep` -> quick start and integration guidance

### 4. Side Effects

- UPDATE: frontmatter descriptions across STV skills
- UPDATE: README quick start and skill reference
- UPDATE: `do-work` environment-specific completion guidance

### 5. Error Paths

- Description summarizes workflow -> agent follows shortcut instead of reading the skill
- Plain-skill environment receives `/stv:*` only -> invocation failure
- `do-work` implies automatic push or `/compact` everywhere -> unsafe or impossible execution

### 6. Output

- Success status code: N/A
- Response schema:
  ```json
  {
    "discoveryMode": "trigger-based",
    "pluginPath": "/stv:*",
    "genericPath": "plain skill names",
    "optionalEnvSteps": ["commit", "push", "compact"]
  }
  ```

### 7. Observability [Optional]

- README quick start shows both plugin and generic usage paths
- Frontmatter descriptions are searchable by symptom and trigger

### Contract Tests (RED)

| Test Name | Category | Trace Reference |
|-----------|----------|-----------------|
| `DiscoveryGuide_PicksCorrectInvocationPath_HappyPath` | Happy Path | Scenario 5, Sections 3 and 6 |
| `DiscoveryGuide_AvoidsWorkflowSummaryDescriptions_SadPath` | Sad Path | Scenario 5, Section 5 |
| `DiscoveryGuide_UpdatesSkillFrontmatter_SideEffect` | Side-Effect | Scenario 5, Section 4 |
| `Description_ToSkillSelection_Contract` | Contract | Scenario 5, Section 3, `frontmatter.description` -> `skillSelection` |

---

## Auto-Decisions

| Decision | Tier | Rationale |
|----------|------|-----------|
| The patch is split into five scenarios instead of one large rewrite | small | Keeps implementation chunks reviewable while still covering the full contract surface |
| The trace treats markdown files as the persistence boundary | small | The feature changes documentation-driven behavior, not runtime database state |
| README updates are included in every affected scenario where the public contract changes | small | README is the public entry point and must not drift behind the skills |

## Implementation Status

| Scenario | Trace | Tests | Verify | Status |
|----------|-------|-------|--------|--------|
| 1. Leftover work routes to execution | done | RED | — | Ready |
| 2. Bundle scope persists end-to-end | done | RED | — | Ready |
| 3. Targeted work uses one status schema | done | RED | — | Ready |
| 4. Planning depth rules align | done | RED | — | Ready |
| 5. Discovery and portability guidance is explicit | done | RED | — | Ready |

## Next Step

→ Implement in scenario order with `work`, starting from routing and scope preservation before schema and wording cleanup.
