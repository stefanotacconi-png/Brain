---
name: kw:review
description: Quality check a knowledge work artifact — plan, brief, strategy doc, or campaign. Two parallel reviewers check strategic alignment and data accuracy. Use before sharing or executing.
---

# Review

Run two parallel reviewers on a finished knowledge work artifact to catch errors, unsourced claims, and strategic misalignment before it ships.

## When to Use

* After `/kw:plan` — before executing or sharing
* "Review this plan", "Is this ready to share?", "Check my brief"
* Any external-facing doc before it goes out

## Process

### Step 1: Identify what to review

Check in this order:
1. Output from the most recent `/kw:` command in this session
2. A file the user referenced
3. Content the user pasted directly

If unclear: "What should I review? Point me to a file or paste the content."

### Step 2: Parallel review (two agents simultaneously)

**Reviewer 1 — Strategic alignment:**
- Is the goal clear and measurable?
- Does the approach logically lead to the goal?
- Is scope proportional to the problem?
- Are success metrics falsifiable?
- Does the recommendation lead, not trail?

**Reviewer 2 — Data accuracy:**
- Is every data point sourced?
- Are sources cited with dates?
- Is any data older than 7 days for fast-moving metrics?
- Are claims verifiable or flagged as estimates?
- Are numbers consistent throughout the doc?

**Reviewer 3 — Editorial (external-facing content only):**
- Tone consistent with brand/audience?
- AI writing patterns that should be humanized?
- Clarity and readability?

### Step 3: Categorize findings

| Severity | Definition | Examples |
|----------|------------|---------|
| **P1** | Blocks sharing/executing | Factual error, missing goal, unsourced claim presented as fact |
| **P2** | Should fix before proceeding | Missing citation, stale data (7+ days), unclear success metric |
| **P3** | Nice to fix | Minor wording, formatting, optional improvements |

> "A factual error in a strategy doc is worse than a typo."

### Step 4: Present findings

```
## Review Summary

**Artifact:** [name/path]
**Reviewed:** [date]

### P1 — Must Fix
- [Finding]: [specific issue and location in doc]

### P2 — Should Fix
- [Finding]: [specific issue]

### P3 — Nice to Fix
- [Finding]: [specific suggestion]

**Verdict:** [Ready to proceed / Fix P1s first / Significant revision needed]
```

### Step 5: Offer next steps

1. **Fix findings** — Address P1s and P2s now
2. **Start `/kw:work`** — Proceed to execution (only if no P1s)
3. **Run `/kw:compound`** — Save learnings from this review
4. **Proceed anyway** — Acknowledge issues and ship

## Important Rules

* **P1 findings block execution.** Don't start `/kw:work` until P1s are resolved.
* **Be specific.** "Claim on line 3 has no source" not "missing citations."
* **Proportional feedback.** A short brief needs a short review. Don't invent problems.
* **Data freshness matters.** Stale numbers in a strategy doc undermine credibility.
