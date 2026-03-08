---
name: kw:work
description: Execute a knowledge work plan. Break it into tasks, do the work, and track what happened. Use after /kw:plan or /kw:review to actually produce the deliverables.
---

# Work

You have a plan. Now execute it. Break it into tasks, do them, track what happened.

## When to Use

* After `/kw:plan` or `/kw:review` — the plan is ready
* "Start working on this", "Execute the plan", "Let's do this"
* When you have a clear plan and need to produce deliverables

## Process

### Step 1: Load the plan

Read the plan file. If none specified:
1. Check most recently modified file in `plans/`
2. Ask: "Which plan should I execute? Point me to a file."

### Step 2: Break into tasks

Extract concrete deliverables. Present the task list:

```
## Tasks

- [ ] [Task 1] — [what needs to be produced]
- [ ] [Task 2] — [what needs to be produced]
```

> "I see [N] deliverables. Here's how I'd break them down. Want to adjust before I start?"

### Step 3: Group tasks by dependency

```
## Execution Plan

### Batch 1 (parallel) — no dependencies
- [ ] [Task A]
- [ ] [Task B]

### Batch 2 (parallel) — depends on Batch 1
- [ ] [Task C] — needs output from Task A

### Batch 3 (sequential) — needs user direction
- [ ] [Task D] — depends on user feedback
```

### Step 4: Execute batch by batch

For each batch:
1. Announce: "Starting Batch 1: [task names]"
2. Launch independent tasks in parallel using Task agents
3. Show all outputs together
4. Get feedback: "Good? Or adjust before Batch 2?"
5. Mark complete, move to next batch

**When to parallelize:**

| Situation | Approach |
|-----------|----------|
| 2+ independent deliverables | Launch as parallel Task agents |
| Single deliverable | Execute inline |
| Deliverable needs back-and-forth | Execute inline, don't delegate |

**Execution principles:**
- Use available MCP tools, APIs, skills — don't recreate what exists
- Follow CLAUDE.md for style guides, data sources, tool preferences
- Show, don't describe — produce the actual deliverable
- Check in after batches, not after every task
- Fall back to sequential if unsure about dependencies

### Step 5: Handle blockers

* **Missing information** — Ask. Be specific about what you need.
* **Missing access** — Note it, move to next task, return when unblocked.
* **Scope creep** — Flag it: "This is turning into its own project. Add as separate plan?"
* **Quality concern** — Say so: "I produced this but I'm not confident about [X]."

### Step 6: Track what happened

```
## Work Log

### [Task 1] ✅
- **Produced:** [what was created]
- **Location:** [file path or link]
- **Notes:** [decisions made, things discovered]

### [Task 2] ⏳ Blocked
- **Blocker:** [what's preventing completion]
- **Next step:** [what needs to happen]
```

### Step 7: Wrap up

```
## Execution Summary

**Plan:** [plan name]
**Tasks completed:** [N] of [total]
**Deliverables produced:**
- [deliverable] — [location]

**Still open:**
- [blocked task] — [blocker]

**Discoveries:**
- [anything worth noting for /kw:compound]
```

### Step 8: Offer next steps

1. **Run `/kw:review`** — Quality check the outputs
2. **Run `/kw:compound`** — Save learnings from this session
3. **Continue working** — Pick up blocked tasks or add new ones
4. **Ship it** — Done, move on

## Important Rules

* **Produce, don't plan.** If you find yourself writing another plan, use `/kw:plan`.
* **Show your work.** After each task, show the actual output.
* **Respect scope.** If something isn't in the plan, ask before adding it.
* **Track everything.** The work log feeds `/kw:compound` with concrete results.
* **Check in between batches.** Knowledge work is subjective — don't produce everything and hope it's right.
