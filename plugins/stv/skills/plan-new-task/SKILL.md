---
name: plan-new-task
description: "Propose new features when all trace scenarios are complete or backlog is too small. Reviews completed work and project context, then applies stv:new-task to create spec + trace for chosen feature."
---

# Plan New Task

## Goal

When there is no meaningful unfinished work in `docs/*/trace.md`, proactively propose new feature work based on completed features and project context, then create structured STV artifacts using `stv:new-task`.

## Sizing Rubric (expected code change, added + deleted)

| Tier   | Lines  | 예시                              |
|--------|--------|-----------------------------------|
| tiny   | ~5     | Config 값, 상수, 문자열 리터럴      |
| small  | ~20    | 한 함수, 한 파일, 로컬 리팩터       |
| medium | ~50    | 여러 파일, 인터페이스 변경           |
| large  | ~100   | 횡단 관심사, 스키마 마이그레이션      |
| xlarge | ~500   | 아키텍처 전환, 프레임워크 교체        |

## Workflow

1. **Confirm backlog status**
   - Glob for `docs/*/trace.md` in the project
   - Read Implementation Status from each trace.md
   - Confirm no meaningful unfinished scenarios exist
   - If tiny/medium leftovers exist, list them separately as carryover

2. **Review completed work**
   - Scan `docs/*/` directories for completed features
   - Read spec.md and trace.md summaries
   - Identify patterns: what was built, what's missing, what's the natural next step
   - Check git log for recent work context

3. **Propose next work**
   - Suggest two to four candidate features based on:
     - Completed feature history (natural follow-ups)
     - Visible gaps in the codebase
     - User context and project goals
   - Tie each idea to recent work or visible gaps
   - Estimate size tier for each proposal

4. **Present options**

```text
All trace scenarios are complete. Based on project history, here are good next features:

1) {Idea A} ({estimated tier})
   - {one line reason, tied to recent work}

2) {Idea B} ({estimated tier})
   - {one line reason}

3) {Idea C} ({estimated tier})
   - {one line reason}

Carryover (tiny leftovers, optional):
- docs/{feature}/trace.md — Scenario {n}: {title}

Pick a number or describe a different feature.
I will then break it down with stv:new-task.
```

5. **Plan with stv:new-task**
   - After user picks an idea, invoke `Skill(skill="stv:new-task")`
   - stv:new-task handles: intent understanding → stv:spec → stv:trace → scenario task list

6. **Hand off**
   - After spec + trace are created, suggest using `stv:do-work` to execute

## Integration

- Use `stv:what-to-work` to decide when to enter this flow (it routes here when backlog is empty/small)
- Use `stv:new-task` for feature decomposition into spec + trace
- Use `stv:do-work` after trace scenarios exist
