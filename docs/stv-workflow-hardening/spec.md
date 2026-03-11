# STV Workflow Hardening — Spec

> STV Spec | Created: 2026-03-06

## 1. Overview

The STV plugin's core methodology is coherent, but the orchestration layer has contract drift between the README, routing skills, execution skills, and the decision prompt. The current gaps are practical rather than philosophical: selected work scope can widen during handoff, small and medium leftovers can get deprioritized into new-task planning, status table shapes differ across documents, and host-specific commands are presented as if they were universal.

This feature hardens the STV workflow by aligning the documentation and skill contracts that govern routing, execution scope, verification status, trace granularity, and portability. The goal is to make an agent that follows the docs behave predictably without needing hidden environment knowledge or ad hoc reinterpretation.

## 2. User Stories

- As a maintainer, I want unfinished small and medium scenarios to remain executable work, so that the backlog tail does not get abandoned behind new feature planning.
- As a user selecting a work bundle, I want the selected trace path and scenario scope to stay intact through execution, so that the agent does not silently widen the job.
- As a maintainer, I want README examples and skill outputs to share one status schema, so that agents interpret progress consistently.
- As a user invoking STV in different environments, I want methodology guidance separated from plugin-specific invocation guidance, so that the workflow remains portable.
- As a maintainer, I want the spec template, trace rules, and decision gate to agree on required depth, so that planning artifacts do not contradict their own quality bar.

## 3. Acceptance Criteria

- [ ] `what-to-work` routes to execution whenever unfinished scenarios exist; `plan-new-task` is reserved for an empty backlog or explicit follow-up planning.
- [ ] `what-we-have-to-work` emits an explicit bundle contract that includes `trace_path`, `scenario_ids`, size, and rationale.
- [ ] `do-work` accepts an explicit bundle input and skips global trace rescans when bundle scope is already provided.
- [ ] `work` supports targeted scenario execution and does not force full-trace execution when a narrower bundle is selected.
- [ ] README, `trace`, and `work` use the same `Implementation Status` schema: `Scenario | Trace | Tests | Verify | Status`.
- [ ] README and `trace` share one trace granularity rule covering full trace vs compact trace.
- [ ] `spec` template depth matches its checklist, including request/response schema expectations and DB detail expectations or explicit `N/A`.
- [ ] `decision-gate` documents a business-meaning override so user-facing semantics are not hidden behind low line-count changes.
- [ ] STV skill descriptions use trigger-oriented `Use when ...` phrasing instead of workflow summaries.
- [ ] README distinguishes plugin-specific slash commands from generic skill invocation guidance.
- [ ] `do-work` treats commit/push and context compaction as optional environment-specific steps, not universal defaults.

## 4. Scope

### In-Scope

- `plugins/stv/README.md`
- `plugins/stv/prompts/decision-gate.md`
- `plugins/stv/skills/spec/SKILL.md`
- `plugins/stv/skills/trace/SKILL.md`
- `plugins/stv/skills/work/SKILL.md`
- `plugins/stv/skills/new-task/SKILL.md`
- `plugins/stv/skills/do-work/SKILL.md`
- `plugins/stv/skills/what-to-work/SKILL.md`
- `plugins/stv/skills/what-we-have-to-work/SKILL.md`
- `plugins/stv/skills/plan-new-task/SKILL.md`
- Frontmatter descriptions and examples that define skill discovery and handoff behavior

### Out-of-Scope

- Runtime engine changes outside the STV plugin documentation and skill files
- New executable test harnesses for skill documents
- Migration to per-scenario trace files in this patch
- Non-STV plugins in this repository

## 5. Architecture

### 5.1 Layer Structure

The hardened workflow uses a documentation-driven control flow:

`README methodology contract -> routing skills -> orchestration skills -> core phase skills -> decision-gate prompt`

- README defines the stable public contract for maintainers and users.
- Routing skills decide whether unfinished work is executed or new work is planned.
- Orchestration skills preserve selected scope and pass it to execution.
- Core phase skills (`spec`, `trace`, `work`) define artifact shapes and verification rules.
- `decision-gate` governs when the agent can decide autonomously and when it must surface a choice.

### 5.2 Invocation Interfaces

No HTTP endpoints are added. This feature changes skill invocation contracts and documentation entry points.

| Invocation | File | Description |
|-----------|------|-------------|
| `what-to-work` | `plugins/stv/skills/what-to-work/SKILL.md` | Routes unfinished work to execution first |
| `what-we-have-to-work` | `plugins/stv/skills/what-we-have-to-work/SKILL.md` | Builds bundles and emits explicit scope |
| `do-work` | `plugins/stv/skills/do-work/SKILL.md` | Executes bundle scope without widening it |
| `work` | `plugins/stv/skills/work/SKILL.md` | Implements only targeted scenarios and updates unified status rows |
| `spec` / `trace` | `plugins/stv/skills/spec/SKILL.md`, `plugins/stv/skills/trace/SKILL.md` | Align artifact depth and trace granularity rules |

### 5.3 State Model

There is no database for this feature. State lives in markdown artifacts and skill files.

| Artifact | Key Fields | Notes |
|----------|------------|-------|
| `docs/{feature}/trace.md` | `Scenario`, `Trace`, `Tests`, `Verify`, `Status` | Canonical task list |
| Bundle contract | `trace_path`, `scenario_ids`, `size`, `rationale` | Passed from bundling to execution |
| Skill frontmatter | `name`, `description` | Discovery contract for agents |

### 5.4 Integration Points

- `plugins/stv/README.md` defines methodology, quick start, and portability guidance.
- `plugins/stv/prompts/decision-gate.md` defines ask-vs-decide behavior.
- `plugins/stv/skills/what-to-work/SKILL.md` and `plugins/stv/skills/what-we-have-to-work/SKILL.md` define backlog routing.
- `plugins/stv/skills/do-work/SKILL.md` and `plugins/stv/skills/work/SKILL.md` define execution scope preservation.
- `plugins/stv/skills/spec/SKILL.md` and `plugins/stv/skills/trace/SKILL.md` define artifact depth and status schema.

## 6. Non-Functional Requirements

- Consistency: README, prompt, and skill outputs must describe the same workflow contract.
- Portability: plugin-specific guidance must be labeled as such; generic guidance must remain executable in plain-skill environments.
- Maintainability: status schema, trace granularity rule, and bundle contract must each have a single canonical definition.
- Auditability: each scenario in the patch plan must map to concrete files and expected documentation outputs.

## 7. Auto-Decisions

| Decision | Tier | Rationale |
|----------|------|-----------|
| Feature folder uses `docs/stv-workflow-hardening/` | tiny | Keeps STV planning artifacts isolated from existing top-level docs |
| This patch keeps the single `docs/{feature}/trace.md` model | small | Matches current skill implementation and avoids a larger scenario-file refactor in the same change |
| Trace scenarios treat skill invocations as entry points | small | The target behavior is documentation-driven, so skill entry points are the correct execution surface |
| No separate executable tests are created in this planning pass | small | The user requested a concrete patch plan, not an implementation pass; the trace carries the verification contract |

## 8. Open Questions

- Follow-up option: split trace files by scenario after contract alignment is complete. This is intentionally deferred from the current patch because it expands scope across every orchestration skill and README example.

## 9. Next Step

→ Proceed with Vertical Trace via `trace`
