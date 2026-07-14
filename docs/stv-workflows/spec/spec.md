# stv:spec — Workflow Spec

> STV Spec (workflow reference) | Created: 2026-07-14 | Source: plugins/stv/skills/spec/SKILL.md

## 1. Overview (Proposal)

STV Phase 1: a feature interview that confirms PRD (what to build) + Architecture (how to build) in
a single pass, emitting `docs/{feature}/spec.md` (SKILL.md:6-9). WHY: an interview run on
unexplored territory asks what the code already answers and misses what matters — so spec front-loads
a Proposal (the WHY) and a mandatory exploration before any question (SKILL.md:23, 45). Handles both
a new feature interview and updating an existing spec (Update vs New) (SKILL.md:3).

## 2. Trigger Contract

**Use when** (SKILL.md:3): requirements and architecture need explicit definition before tracing —
a new feature interview, OR updating an existing `spec.md` (Update vs New decision). Feeds `stv:trace`
(SKILL.md:215, 249). Actions-not-Phases: also re-entered from later phases (§5, SKILL.md:231-234).

## 3. Workflow Trace

```
Step 0 Proposal (WHY, <1min inline block; weak/absent → 1 question or suggest stv:explore) (SKILL.md:21-39)
 → Step 0.5 Explore First (MANDATORY): run stv:explore, build unknowns map — known knowns / known
     unknowns / unknown knowns / unknown unknowns; all 4 quadrants always present (may compress to a
     line, never disappear) (SKILL.md:43-55)
 → Step 1-0 Input Analysis: interpret arg (file→read / name→seed / existing spec→UPDATE mode) +
     Agent:Explore extends (not restarts) the unknowns map; Update-vs-New decision tree (SKILL.md:59-88)
 → Step 1-1 Business Interview (What): user stories, acceptance criteria, scope IN/OUT, NFRs (SKILL.md:90-106)
 → Step 1-2 Architecture Interview (How): layer structure, client surface, DB schema, API endpoints,
     integration points, error handling, auth model (SKILL.md:108-121)
 → Step 1-3 Spec Writing → docs/{feature}/spec.md (SKILL.md:136-216)
 → Next Step: stv:trace (SKILL.md:214-215, 249)
```

**Decision Gate (MANDATORY, SKILL.md:13-17):** applied to EVERY question — switching cost < small →
autonomous judgment; == small → autonomous + report; >= medium → ask user. Bundle 2-4 related
questions into one AskUserQuestion; never ask what the codebase/map already closed; present options
not Yes/No; give a recommendation per question (SKILL.md:96, 123-134). Every interview question must
trace to a known-unknown (or unknown-known probe) on the map (SKILL.md:53).

**Actions-not-Phases backtrack entry points (SKILL.md:227-242):** re-invoke `stv:spec` with the
existing spec path — from `stv:trace` (missing/ambiguous scenario), `stv:work` (spec assumption
wrong), or after `stv:verify` (gap traces to a spec error). Update-vs-New tree applies; Delta Log
records the change; downstream trace.md/tests flagged for re-verification.

## 4. Artifacts & Side Effects

`docs/{feature-name}/spec.md` (SKILL.md:140-216), sections: 1 Overview (embeds Proposal block) · 2
User Stories · 3 Acceptance Criteria · 4 Scope IN/OUT · **5 Architecture** · 6 NFRs · 7 Auto-Decisions
(decision/tier/rationale table) · 8 Open Questions · 9 Delta Log · 10 Next Step. Architecture detail:
- **§5.1 Layer Structure** — Client/UI → Controller → Handler → Service → DB, naming the full round
  trip *including how the response returns to the client* (SKILL.md:174-175).
- **§5.2 Client Surface** — entry screens/components, user actions firing each API call, what renders
  from each response; CDC boundary if client is a separate repo; `N/A (no client surface)` for
  pure-backend (SKILL.md:177-178).
- **§5.3 API Endpoints** — table with Method/Path/Handler/**Request schema/Response schema**/Description;
  request/response schema REQUIRED per endpoint (or explicit `N/A`) — trace §2/§6 derive from it (SKILL.md:180-187).
- **§5.4 DB Schema** — table/column/FK/index level, or explicit `N/A (no persistence)` (SKILL.md:189-190).
- **§5.5 Integration Points** (SKILL.md:192-193).

UPDATE mode edits spec.md in-place + records in `## Delta Log`; NEW mode creates `docs/{feature-v2}/
spec.md` referencing the original (SKILL.md:87-88). Auto-Decisions capture Decision-Gate autonomous
calls (SKILL.md:200-206).

## 5. Error Paths & NEVER

- **Weak/absent Proposal WHY** → warn the user before proceeding; if WHY takes >1min it isn't
  understood yet → suggest `stv:explore` first (SKILL.md:39, 248).
- **Skipping the unknowns map is NOT an option** — depth shrinks, quadrants never disappear (SKILL.md:55).
- **Interview questions must trace to the unknowns map** — never ask what the map/codebase already
  settled; don't ask Yes/No or >5 questions at once (SKILL.md:53, 131-134).

## 6. Acceptance Checklist

- [ ] User stories + acceptance criteria per scenario; scope IN/OUT clear (SKILL.md:220-221).
- [ ] DB schema at table/column/FK/index level (or explicit N/A) (SKILL.md:222).
- [ ] API endpoints with method/path/request/response schema (SKILL.md:223).
- [ ] Client surface defined (screens/actions → endpoints → rendered response) or explicit N/A (SKILL.md:224).
- [ ] All decisions with switching cost >= medium (50+ lines) have human approval (SKILL.md:225).

## 7. Improvement Delta (2026-07-14)

- Template depth aligned to the Phase 1 checklist: §5.3 endpoint table gained Request/Response schema
  columns (required or explicit N/A); §5.4 DB pinned at table/column/FK/index or explicit N/A.
- Added §5.2 Client Surface; §5.1 layer overview now names the full round trip incl. the response
  returning to the client; Step 1-2 interview must cover client surface.
- Skill `description` made trigger-based (Use-when: new interview vs Update-vs-New) (SKILL.md:3).
