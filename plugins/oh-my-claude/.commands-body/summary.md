# /summary - Advanced Multi-Method Summarization

Stop asking AI to "summarize". Instead, extract maximum value through strategic analysis.

## Core Philosophy

**Simple summarization wastes content potential.** This command implements 8 analysis methods to transform information into actionable intelligence, tailored to specific stakeholders.

---

## The 8 Analysis Methods

| # | Method | Purpose | When to Use |
|---|--------|---------|-------------|
| 1 | **Extract Strategic Insights** | Filter noise → 5 key gems | Decision support |
| 2 | **Turn Information Into Action** | Create 5-step action plan | Execution needed |
| 3 | **Surface Hidden Assumptions** | Reveal blind spots | Argument analysis |
| 4 | **Compare Opposing Views** | Map alignment/differences | Debate analysis |
| 5 | **Distil for Specific Role** | Role-based filtering | Targeted audience |
| 6 | **Build Reusable Model** | Extract repeatable framework | Pattern/process |
| 7 | **Extract Contrarian Takeaways** | Counter-conventional insights | Differentiation |
| 8 | **Identify Leverage Points** | Small effort → big result | ROI optimization |

---

## Phase 1: Content Analysis (DEEP THINKING)

### 1.1 Read and Understand Content

First, thoroughly read and comprehend the input content:

```
IF $ARGUMENTS is file path:
  → Read the file(s)

IF $ARGUMENTS is URL:
  → WebFetch the content

IF $ARGUMENTS is inline text:
  → Process directly
```

### 1.2 Content Type Classification

Classify the content to determine appropriate methods:

| Content Type | Signals | Recommended Methods |
|--------------|---------|---------------------|
| **Research/Report** | Data, findings, conclusions | 1, 6, 8 |
| **Opinion/Essay** | Arguments, claims, reasoning | 3, 4, 7 |
| **Tutorial/Guide** | Steps, instructions, how-to | 2, 6 |
| **Strategy/Plan** | Goals, initiatives, metrics | 1, 2, 5, 8 |
| **Technical Doc** | Architecture, specs, APIs | 5, 6 |
| **Meeting Notes** | Decisions, actions, owners | 2, 8 |
| **News/Analysis** | Events, interpretations | 1, 4, 7 |
| **Mixed/Complex** | Multiple elements | Use ALL appropriate |

### 1.3 Determine Applicable Methods

Based on content type and depth:

```
depth = --depth OR "deep" (default)

IF depth == "quick":
  → Select TOP 3 most relevant methods

IF depth == "deep":
  → Apply ALL applicable methods (typically 4-6)
```

---

## Phase 2: Stakeholder Inference

### 2.1 Identify Stakeholders from Content

Infer who would benefit from this content:

| Content Signals | Primary Stakeholder | Focus |
|-----------------|---------------------|-------|
| Technical architecture | Engineer | Feasibility, Scale |
| Market data, trends | Marketer | Reach, Conversion |
| Revenue, growth, runway | Founder/Executive | Cash flow, Growth |
| User journey, UX | Product Manager | User value |
| Risk, compliance | Legal/Risk | Liability |
| Operations, process | Operations | Efficiency |

### 2.2 Role-Based Lens (Method 5)

If `--role` specified OR inferred:

| Role | Lens | Key Questions |
|------|------|---------------|
| **Engineer** | Feasibility/Scale | "Can we build this? Will it scale?" |
| **Marketer** | Reach/Conversion | "How do we position this? Who buys?" |
| **Founder** | Cash flow/Growth | "Does this make money? Can we grow?" |
| **Product** | User Value | "Does this solve user problems?" |
| **Executive** | Strategic Impact | "How does this affect our position?" |

---

## Phase 3: Parallel Analysis Execution (CRITICAL)

### ⚡ MANDATORY: Run Methods in Parallel via Subagents

**Each analysis method runs as a separate Opus subagent for maximum quality and parallelism.**

```typescript
// CORRECT: Fire all selected methods in parallel
// After determining selected_methods in Phase 1-2:

Task({
  subagent_type: "general-purpose",
  model: "opus",
  description: "Method 1: Strategic Insights",
  prompt: `${METHOD_1_PROMPT}\n\nContent:\n${CONTENT}`,
  run_in_background: true
})

Task({
  subagent_type: "general-purpose",
  model: "opus",
  description: "Method 3: Hidden Assumptions",
  prompt: `${METHOD_3_PROMPT}\n\nContent:\n${CONTENT}`,
  run_in_background: true
})

// ... fire all selected methods simultaneously

// Then collect results:
TaskOutput({ task_id: "method_1_id" })
TaskOutput({ task_id: "method_3_id" })
// ...
```

### Analysis Prompts for Subagents

Each subagent receives a specialized prompt. Below are the exact prompts to use:

---

### Method 1 Subagent: Extract Strategic Insights

```markdown
You are a senior strategy consultant analyzing content for a client.

TASK: Extract the 5 most valuable strategic insights from this content.

For each insight:
1. State the insight clearly (1-2 sentences)
2. Explain its significance (why it matters)
3. Identify what decision or action it informs

OUTPUT FORMAT:
| # | Insight | Significance | Decision It Informs |
|---|---------|--------------|---------------------|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |
| 4 | ... | ... | ... |
| 5 | ... | ... | ... |

CONTENT TO ANALYZE:
{content}
```

---

### Method 2 Subagent: Turn Information Into Action

```markdown
You are an execution-focused project manager.

TASK: Transform this content into a concrete 5-step action plan.

For each step:
1. Define the specific action
2. Identify who should own it (role, not name)
3. Identify a quick win (achievable in <1 week)
4. Define a measurable result (KPI or outcome)

OUTPUT FORMAT:
| Step | Action | Owner | Quick Win | Measurable Result |
|------|--------|-------|-----------|-------------------|
| 1 | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... |
| 4 | ... | ... | ... | ... |
| 5 | ... | ... | ... | ... |

CONTENT TO ANALYZE:
{content}
```

---

### Method 3 Subagent: Surface Hidden Assumptions

```markdown
You are a critical thinker and debate coach.

TASK: Reveal the unstated assumptions and blind spots in this content.

Identify:
1. 3-5 hidden assumptions the argument relies on
2. Evidence (or lack thereof) for each assumption
3. What changes if each assumption is wrong
4. Any blind spots the author seems unaware of

OUTPUT FORMAT:
### Hidden Assumptions
| # | Assumption | Evidence | If Wrong? |
|---|------------|----------|-----------|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |

### Blind Spots Identified
- Blind spot 1: ...
- Blind spot 2: ...

CONTENT TO ANALYZE:
{content}
```

---

### Method 4 Subagent: Compare Opposing Views

```markdown
You are a balanced analyst skilled at dialectical thinking.

TASK: Map this content against opposing perspectives.

1. Identify the main thesis/position
2. Construct the strongest opposing view (steelman)
3. Find where they align (common ground)
4. Find where they conflict (key differences)
5. Determine which context favors each view

OUTPUT FORMAT:
### Main Position
{summarize the content's position}

### Strongest Opposing View
{steelman the counter-argument}

### Alignment (Common Ground)
- Point 1: ...
- Point 2: ...

### Conflict (Key Differences)
| Aspect | This Content | Opposing View | Best Context |
|--------|--------------|---------------|--------------|
| ... | ... | ... | ... |

CONTENT TO ANALYZE:
{content}
```

---

### Method 5 Subagent: Distil for Specific Role

```markdown
You are adapting content for a specific audience.

TASK: Filter this content through the lens of a {ROLE}.

Role Lens:
- Engineer → Feasibility, Scale, Technical Debt
- Marketer → Reach, Conversion, Positioning
- Founder → Cash flow, Growth, Strategic Fit
- Product → User Value, Problem-Solution Fit
- Executive → Strategic Impact, Risk, Opportunity Cost

For the {ROLE}:
1. Identify what matters most to them
2. Translate jargon into their language
3. Highlight actionable items for their domain
4. Provide a key takeaway they can act on immediately

OUTPUT FORMAT:
### {ROLE} View

**Core Priorities**: {what this role cares about}

| Aspect | Relevance to {ROLE} | Action Required |
|--------|---------------------|-----------------|
| ... | ... | ... |

**Key Takeaway for {ROLE}**: {one sentence they can act on}

CONTENT TO ANALYZE:
{content}
```

---

### Method 6 Subagent: Build Reusable Model

```markdown
You are a systems thinker extracting repeatable patterns.

TASK: Extract the underlying framework or process from this content.

Identify:
1. What inputs does this process/framework take?
2. What are the key stages/steps?
3. What outputs does it produce?
4. Where does feedback/iteration occur?

OUTPUT FORMAT:
### Framework: {Name}

**Input**: {what goes in}
**Output**: {what comes out}

| Stage | Input | Process | Output |
|-------|-------|---------|--------|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |

**Feedback Loop**: {where iteration happens}

**When to Use This Framework**: {conditions for applicability}

CONTENT TO ANALYZE:
{content}
```

---

### Method 7 Subagent: Extract Contrarian Takeaways

```markdown
You are a contrarian thinker who challenges conventional wisdom.

TASK: Find insights that would surprise smart peers—credible but unexpected.

Rules:
1. Must be defensible (not just provocative)
2. Must challenge common assumptions
3. Must be expressed as sharp one-liners
4. Explain WHY each is contrarian

OUTPUT FORMAT:
### Contrarian Insights

> 💡 "{insight 1}"
> — Challenges: {what conventional wisdom it opposes}

> 💡 "{insight 2}"
> — Unexpected because: {why people wouldn't expect this}

> 💡 "{insight 3}"
> — Credible yet surprising: {evidence that supports it}

### Why These Matter
{Brief explanation of why contrarian thinking adds value here}

CONTENT TO ANALYZE:
{content}
```

---

### Method 8 Subagent: Identify Leverage Points

```markdown
You are a systems dynamics expert finding high-leverage interventions.

TASK: Identify 3 leverage points where small actions create outsized results.

For each leverage point:
1. Name the specific intervention point
2. Describe the small action required
3. Explain the expected outsized impact
4. Justify why this particular point has leverage

OUTPUT FORMAT:
### Leverage Points

| # | Leverage Point | Small Action | Expected Impact | Why It Matters |
|---|----------------|--------------|-----------------|----------------|
| 1 | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... |

### Leverage Analysis
{Brief explanation of why these points have disproportionate impact}

CONTENT TO ANALYZE:
{content}
```

---

## Phase 3B: Apply Analysis Methods (Reference)

### Method 1: Extract Strategic Insights

**Prompt**: Act like a strategy consultant. Identify the 5 most valuable insights and explain what decisions each one informs.

```markdown
### Strategic Insights

| # | Insight | Significance | Decision It Informs |
|---|---------|--------------|---------------------|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |
| 4 | ... | ... | ... |
| 5 | ... | ... | ... |
```

### Method 2: Turn Information Into Action

**Prompt**: Translate this into a 5-step plan with clear owners, quick wins, and measurable results.

```markdown
### Action Plan

| Step | Action | Owner | Quick Win | Measurable Result |
|------|--------|-------|-----------|-------------------|
| 1 | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... |
| 4 | ... | ... | ... | ... |
| 5 | ... | ... | ... | ... |
```

### Method 3: Surface Hidden Assumptions

**Prompt**: Reveal the unstated assumptions or blind spots shaping this argument—and what changes if they're wrong.

```markdown
### Hidden Assumptions

| # | Assumption | Evidence | If Wrong? |
|---|------------|----------|-----------|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |

### Blind Spots Identified
- ...
```

### Method 4: Compare Opposing Views

**Prompt**: Map this idea against two competing perspectives. Show where they align, where they differ, and which context fits each.

```markdown
### Perspective Analysis

```
┌─────────────────┐          ┌─────────────────┐
│  Perspective A  │          │  Perspective B  │
│                 │          │                 │
│  - Point 1      │   🟢     │  - Point 1      │
│  - Point 2      │ Aligned  │  - Point 2      │
└────────┬────────┘          └────────┬────────┘
         │                            │
         │      ┌───────────┐         │
         └──────┤ Conflict  ├─────────┘
                │  Points   │
                └───────────┘
```

| Aspect | View A | View B | Best Context |
|--------|--------|--------|--------------|
| ... | ... | ... | ... |
```

### Method 5: Distil for Specific Role

**Prompt**: Filter this through the lens of a [role]. Focus on their priorities.

```markdown
### {Role} View

**Core Priorities**: ...

| Aspect | Relevance to {Role} | Action Required |
|--------|---------------------|-----------------|
| ... | ... | ... |

**Key Takeaway for {Role}**: ...
```

### Method 6: Build Reusable Model

**Prompt**: Extract the repeatable framework hidden in this text. Label each stage, its input, and output.

```markdown
### Extracted Framework

```
        ┌─────────┐
        │  INPUT  │
        └────┬────┘
             │
    ┌────────▼────────┐
    │    PROCESS      │
    │  ┌───────────┐  │
    │  │ Stage 1   │  │
    │  └─────┬─────┘  │
    │        │        │
    │  ┌─────▼─────┐  │      ┌──────────┐
    │  │ Stage 2   │──┼──────► FEEDBACK │
    │  └─────┬─────┘  │      └──────────┘
    │        │        │
    │  ┌─────▼─────┐  │
    │  │ Stage 3   │  │
    │  └───────────┘  │
    └────────┬────────┘
             │
        ┌────▼────┐
        │ OUTPUT  │
        └─────────┘
```

| Stage | Input | Process | Output |
|-------|-------|---------|--------|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |
```

### Method 7: Extract Contrarian Takeaways

**Prompt**: Find insights that would challenge smart peers—still credible, but unexpected. Write each as a sharp one-liner.

```markdown
### Contrarian Insights

> 💡 "..." — challenges: conventional wisdom about X
>
> 💡 "..." — unexpected because: Y
>
> 💡 "..." — credible yet surprising: Z

### Why These Challenge Conventional Wisdom
- ...
```

### Method 8: Identify Leverage Points

**Prompt**: Highlight the 3 leverage points where small actions could create outsized results. Explain why each one matters.

```markdown
### Leverage Points

```
  Small Effort ─────────► BIG IMPACT
       │                       │
       ●                       ★
    Point 1               Result 1

       ●                       ★
    Point 2               Result 2

       ●                       ★
    Point 3               Result 3
```

| # | Leverage Point | Small Action | Expected Impact | Why It Matters |
|---|----------------|--------------|-----------------|----------------|
| 1 | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... |
```

---

## Phase 4: Synthesize Executive Summary

### 4.1 Output Format Selection

Based on `--output` flag:

| Flag | Format | Best For |
|------|--------|----------|
| `executive` (default) | Executive Summary | Decision makers |
| `action` | Action Plan Focus | Implementation teams |
| `role` | Role-Specific | Targeted stakeholders |

### 4.2 Executive Summary Template (Default)

```markdown
# Executive Summary: {Title}

> **Source**: {file/URL/description}
> **Analysis Depth**: {quick|deep}
> **Methods Applied**: {list of # methods used}
> **Primary Stakeholder**: {inferred role}

---

## TL;DR

{2-3 sentences capturing the essence}

---

## Strategic Insights (Method 1)

{Top 5 gems from the content}

---

## Recommended Actions (Method 2)

{5-step action plan if applicable}

---

## Critical Assumptions (Method 3)

{Hidden assumptions and blind spots}

---

## Stakeholder Perspectives (Methods 4 & 5)

### For {Primary Role}
{Role-specific analysis}

### Opposing Views Considered
{If applicable}

---

## Reusable Framework (Method 6)

{If a framework was extracted}

---

## Contrarian Takeaways (Method 7)

{Sharp one-liners that challenge conventional wisdom}

---

## Leverage Points (Method 8)

{3 high-ROI opportunities}

---

## Next Steps

1. [ ] {Immediate action}
2. [ ] {Short-term action}
3. [ ] {Strategic follow-up}

---

*Generated: {YYYY-MM-DD}*
*Methods: {list of applied methods}*
```

---

## Phase 5: Output Handling

### Save Location

Default: `./docs/summaries/{sanitized-title}-{YYYY-MM-DD}.md`

```bash
mkdir -p ./docs/summaries
```

### Completion Message

```
Summary saved to: ./docs/summaries/{filename}.md

Applied Methods:
- [1] Extract Strategic Insights ✓
- [2] Turn Information Into Action ✓
- [5] Distil for Specific Role (Engineer) ✓
- [8] Identify Leverage Points ✓

Primary Stakeholder: {Role}
Depth: {quick|deep}
```

---

## Execution Flow

### Task: $ARGUMENTS

1. **Parse arguments** - identify content source and options
2. **Read content** - fetch and understand the material
3. **Classify content type** - determine what kind of content
4. **Select methods** - pick 3-6 most relevant methods
5. **Infer stakeholders** - identify who benefits
6. **Apply methods** - run each selected analysis
7. **Synthesize** - combine into executive summary
8. **Save output** - write to ./docs/summaries/

### Decision Points

```
IF content unclear:
  → AskUserQuestion for clarification

IF --role specified:
  → Prioritize Method 5 (Distil for Role)

IF content is argumentative:
  → Prioritize Methods 3, 4, 7

IF content is instructional:
  → Prioritize Methods 2, 6

IF no output path given:
  → Save to ./docs/summaries/
```

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                    /summary QUICK GUIDE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  USAGE:                                                         │
│    /summary path/to/file.md                                     │
│    /summary --role=founder business-plan.pdf                    │
│    /summary --depth=quick --output=action meeting-notes.txt     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  OPTIONS:                                                       │
│    --output   executive | action | role                         │
│    --role     engineer | marketer | founder | product | exec    │
│    --depth    quick (3 methods) | deep (4-6 methods)            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  8 METHODS:                                                     │
│    1. Strategic Insights    5. Role Distillation                │
│    2. Action Plan           6. Reusable Framework               │
│    3. Hidden Assumptions    7. Contrarian Takeaways             │
│    4. Opposing Views        8. Leverage Points                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  AUTO-SELECTION:                                                │
│    Research/Report → 1, 6, 8                                    │
│    Opinion/Essay   → 3, 4, 7                                    │
│    Tutorial/Guide  → 2, 6                                       │
│    Strategy/Plan   → 1, 2, 5, 8                                 │
│    Technical Doc   → 5, 6                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
