---
name: kw:confidence
description: Gut-check what you know and don't know before proceeding. Use at any point to assess confidence, surface gaps, and decide whether to proceed or dig deeper.
---

# Confidence

Pause and honestly say what you're confident about and what you're not. Then decide whether to proceed or dig deeper.

## When to Use

* Before committing to a plan or starting execution
* When something feels uncertain but you can't pinpoint what
* After research, to verify you have enough to proceed
* As a gut-check during any `/kw:` workflow

## Process

### Step 1: Identify what's being assessed

Scan the conversation:
- Mid-`/kw:work` → assess the current or next task
- Mid-`/kw:plan` → assess the plan being structured
- Plan file exists → read it and assess the approach
- User gave context → assess what they described

If nothing to assess: "What should I assess? Describe what you're working on or point me to a file."

### Step 2: Assess honestly

Consider internally (don't output as a checklist):
- **Task understanding** — Do I know exactly what's being asked?
- **Information sufficiency** — Do I have what I need to do this well?
- **Approach certainty** — Is this approach proven or am I guessing?
- **Risk awareness** — Can I see what could go wrong?

Rules:
- Assess each area independently
- Be specific — name files, numbers, assumptions, unknowns
- Don't hedge on things you're genuinely confident about
- Don't fake confidence on things you're not sure about

### Step 3: Produce the confidence check

Write in plain prose:

```
## Confidence Check

**Confident about:** [What you know and why. Name the files read,
patterns recognized, experience drawn on.]

**Less confident about:** [What you don't know and why it matters.
Name specific gaps — missing data, unverified assumptions.]

**My recommendation:** [One of:
- "Proceed." — confidence is high, no meaningful gaps
- "Proceed, but [caveat]." — mostly confident, one area to watch
- "Pause for [specific thing]." — a gap needs resolving first]
```

If everything is high confidence, keep it short:
> **High confidence.** Task is clear, relevant files read, approach matches established patterns. Ready to proceed.

### Step 4: Offer next steps

1. **Proceed** — Continue with current approach
2. **Increase confidence** — Show specific actions to resolve gaps
3. **Run `/kw:plan`** — Structure a plan if one doesn't exist
4. **Save assessment** — Write to active plan or `plans/confidence-{date}.md`

**If "Increase confidence" selected**, produce a ranked list:

```
## To Increase Confidence

1. [Specific action] — [What gap it closes]
2. [Specific action] — [What gap it closes]

Want me to start with #1?
```

Each action must be immediately executable. "Read `data/q4-results.csv`" not "gather more data."

After executing, reference the improvement:
> "That Q4 data confirms the $50K target is realistic — that was the main gap. Confidence is higher now."

**If "Proceed" selected mid-workflow**, re-anchor explicitly:
> "Resuming `/kw:work` at Task 3."

## Important Rules

* **Never give a number.** No percentages, no 1–10 scales. Write in prose.
* **Be specific.** "Missing Q4 data" not "some information gaps."
* **Don't hedge on what you know.** If you've done the work, say so.
* **Actions must be executable.** Every item must be doable right now.
* **Non-destructive interrupt.** Resume exactly where you left off after.
* **Keep it proportional.** High confidence = 2 sentences. Don't write a wall of text.
* **This is not `/kw:review`.** Confidence assesses your epistemic state. Review assesses whether a finished artifact is good enough.
