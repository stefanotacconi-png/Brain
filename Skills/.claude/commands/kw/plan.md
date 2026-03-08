---
name: kw:plan
description: Research past work and structure a knowledge work plan. Use when starting strategy docs, campaign plans, content briefs, research synthesis, or operational playbooks.
---

# Plan

Research what you already know, then structure a plan grounded in data and past learnings. Lead with the answer.

## When to Use

* After brainstorming, when ready to commit to a direction
* Starting a strategy doc, campaign plan, content brief, research synthesis, or SOP
* "Plan the March campaign", "I need a brief for X", "Let's structure this"

## Process

### Step 1: Classify the work type (auto-detect, don't ask)

| Type | Signals |
|------|---------|
| **Strategy** | Roadmap, architecture, long-term, layers, phases |
| **Campaign** | Launch, promotion, timeline, channels, audience |
| **Brief** | Directive for someone else, scope, deliverables |
| **Research** | Investigation, competitive analysis, synthesis |
| **Operations** | Playbook, runbook, SOP, recurring process |

### Step 2: Research (all in parallel)

**2a. Past plans** — Search `plans/` for related work. Read top 3 most relevant: what was decided, what data was used, what worked.

**2b. Knowledge base** — Search `docs/knowledge/` for saved learnings from `/kw:compound`.

**2c. Solutions** — Search `docs/solutions/` for relevant patterns.

**2d. Live data** — Pull current metrics if the plan involves data. Follow data hierarchy in CLAUDE.md.

**2e. External research** — If topic benefits from outside context, search the web.

### Step 3: Surface what you already know

Present a context brief before writing anything:

```
## What I Found

**Related plans:**
- [plan name] — [one-line summary of relevance]

**Past learnings:**
- [learning title] — [the insight]

**Current data:**
- [metric]: [value] ([source, date])

**External research:**
- [finding] — [source]
```

Wait for the user to react before proceeding.

### Step 4: Structure the plan

Use the template matching the work type. All templates include at the bottom:

```markdown
## Success Metrics

| Metric | Current Baseline | Target | Source |
|--------|-----------------|--------|--------|

## Open Questions

- [What we don't know yet]

## References

- [Related plans, knowledge entries, data sources]
```

**Campaign** — Timeline-first:
```markdown
# [Title]
**Type:** Campaign | **Status:** Draft | **Created:** [date]

## Timeline
| Date/Week | Action | Channel | Owner |
|-----------|--------|---------|-------|

## Goal
[What this achieves and how we'll know it worked]

## Audience
[Who this targets]

## Assets Needed
- [Copy, creative, landing pages, emails]

## Current State
[Relevant baselines before we start]
```

**Strategy** — Recommendation-first:
```markdown
# [Title]
**Type:** Strategy | **Status:** Draft | **Created:** [date]

## Recommendation
[What we should do and why. Lead with the answer.]

## Current State
[What's true right now. Source and date for every number.]

## Proposed Approach
[How to get from current state to desired outcome]
```

**Operations** — Trigger-first:
```markdown
# [Title]
**Type:** Operations | **Status:** Draft | **Created:** [date]

## Trigger
[When does this process run?]

## Steps
1. [Step] — [details, tools, commands]

## Edge Cases
| Situation | What to do |

## Owner
[Who runs this. Who to escalate to.]
```

### Step 5: Write to plans/

Filename: `plans/{type}-{descriptive-name}.md`
If exists: `plans/{type}-{name}-{YYYY-MM-DD}.md`

Always write the file BEFORE presenting options.

### Step 6: Offer next steps

1. **Run `/kw:review`** — Check strategic alignment and data accuracy
2. **Start `/kw:work`** — Begin executing
3. **Refine** — Adjust specific sections
4. **Open in editor** — View the full plan

## Important Rules

* **Lead with the answer.** Recommendation section comes first.
* **Cite everything.** Every data point needs a source and date.
* **Surface past work.** Related plans and learnings MUST appear in the context brief.
* **Degrade gracefully.** If a source fails, proceed with what you have and note what's missing.
