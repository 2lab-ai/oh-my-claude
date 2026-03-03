---
name: what-to-work
description: "Decide what to work on next by scanning docs/*/trace.md for unfinished scenarios, then routing to what-we-have-to-work or plan-new-task."
---

# What To Work

## Goal

Provide clear, user-confirmable next work options. Scan `docs/*/trace.md` for unfinished scenarios. If enough work exists, route to `stv:what-we-have-to-work`. If not, route to `stv:plan-new-task`.

## Sizing Rubric (expected code change, added + deleted)

| Tier   | Lines  | 예시                              |
|--------|--------|-----------------------------------|
| tiny   | ~5     | Config 값, 상수, 문자열 리터럴      |
| small  | ~20    | 한 함수, 한 파일, 로컬 리팩터       |
| medium | ~50    | 여러 파일, 인터페이스 변경           |
| large  | ~100   | 횡단 관심사, 스키마 마이그레이션      |
| xlarge | ~500   | 아키텍처 전환, 프레임워크 교체        |

## Workflow

1. **Scan trace files**
   - Glob for `docs/*/trace.md` in the project
   - Read each trace.md's Implementation Status table
   - Collect scenarios where Status != "Complete"
   - Estimate size for each unfinished scenario

2. **Decide if work exists**
   - **Bundle-worthy**: can form at least one large or xlarge bundle from unfinished scenarios
   - **Not enough**: only tiny/medium scenarios remain, or total expected change is below large

3. **Route**
   - If bundle-worthy → `Skill(skill="stv:what-we-have-to-work")` to propose 1-3 bundles
   - If empty or too small → `Skill(skill="stv:plan-new-task")` to propose new features

4. **Present next action**
   - State which route you are using and why
   - Ask for any missing context only if it blocks routing

## Output Template

### Route: what-we-have-to-work

```text
Trace scan complete: {N} features found, {M} unfinished scenarios
Total estimated work: {tier}
Route: what-we-have-to-work
Next step: I'll bundle scenarios into up to three options for you to pick.
```

### Route: plan-new-task

```text
Trace scan complete: {summary}
No meaningful unfinished work found.
Route: plan-new-task
Next step: I'll propose new features based on completed work and project context.
```

## Integration

- Use `stv:what-we-have-to-work` when unfinished scenarios can form a large/xlarge bundle
- Use `stv:plan-new-task` when all scenarios are complete or remaining work is too small
- After user selection, follow `stv:do-work` for execution
