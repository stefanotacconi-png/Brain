---
name: kw:brainstorm
description: Brain dump and compile knowledge before structuring a plan. Use when starting any non-trivial knowledge work — after a meeting, when tackling a new problem, or when you need to pull together what you know before planning.
---

# Brainstorm

Get everything out of your head and into one place. Pull in references. Find the shape of the problem before you commit to a plan.

## When to Use

* After a meeting where next steps need to be figured out
* Starting a new project, campaign, or strategy
* "I need to think through X", "Let me brain dump", "Help me figure this out"
* When you have scattered inputs (notes, docs, transcripts) that need organizing

## Process

### Step 1: Capture the brain dump

Accept whatever the user gives you — meeting transcript, voice-to-text, bullet points, a link. **Do not organize yet.** Just acknowledge what you received.

If nothing given yet, prompt:
> "What are you working on? You can paste meeting notes, describe the problem, or just start talking. I'll help organize it."

### Step 2: Extract the core elements

Pull out and present back as a structured summary:

```
## What I Heard

**The problem:** [one sentence]

**Decisions to make:**
- [Decision 1]

**Open questions:**
- [Question 1]

**Constraints:**
- [timeline, budget, dependencies]

**Stakeholders:**
- [Who] — [what they care about]

**Ideas floated:**
- [Idea] — [brief note on pros/cons if mentioned]

**Data points mentioned:**
- [numbers, metrics, references]
```

### Step 3: Pull in references

Ask: "Where might relevant context live? I can search for it."

Search in parallel:
- Local files — `plans/`, `docs/`, project directories
- Knowledge base — `docs/knowledge/` (from `/kw:compound`)
- Web — frameworks, best practices, competitive examples

For each source:
```
**Found:** [source name/path]
**Relevant because:** [one sentence]
**Key takeaway:** [the useful bit]
```

### Step 4: Identify themes and tensions

```
## Themes
1. [Theme] — [why it matters]

## Tensions
- [Option A] vs [Option B] — [the tradeoff]

## Gaps
- [What we don't know yet]
```

### Step 5: Resolve load-bearing questions

Identify which open questions are **load-bearing** — where different answers lead to different plans. Ignore nice-to-know questions.

Ask **1–3 load-bearing questions** using AskUserQuestion (never more than 3). Frame with options drawn from the brainstorm — not open-ended.

If all open questions are non-load-bearing:
> "The open questions won't change the plan's shape — we can resolve them during execution."

### Step 6: Suggest a direction

> "Based on what I'm seeing, the core question is [X]. The main tension is between [A] and [B]. My suggestion would be to [direction] because [reasoning]. But [caveat]."

### Step 7: Offer next steps

1. **Run `/kw:plan`** — Structure this into an actionable plan
2. **Dig deeper** — Research a specific theme further
3. **Save as-is** — Write to `plans/brainstorm-{descriptive-name}.md`
4. **Keep going** — Add more context or refine

## Important Rules

* **Don't jump to solutions.** Understand the problem space first.
* **Reflect, don't rewrite.** Use the user's language.
* **1–3 load-bearing questions max.** Don't turn brainstorming into a requirements session.
* **Quantity of input is fine.** A 30-minute transcript is good input.
