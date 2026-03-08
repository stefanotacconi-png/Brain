---
name: ce:plan
description: Create a detailed implementation plan from a feature idea, bug report, or improvement. Use before writing any code. Produces a plan file in docs/plans/.
---

# Plan

Transform a feature description, bug report, or improvement idea into a well-structured markdown project plan. NEVER CODE during this command — only research and document.

## When to Use

* Starting any non-trivial feature or fix
* "Plan X", "I want to build Y", "Help me think through Z"
* Before running `/ce:work`

## Process

### Step 0: Check for existing brainstorm

Look for relevant files in `docs/brainstorms/`. If found and recent (≤14 days), use as foundation and skip refinement questions.

### Step 1: Local research (parallel)

Run in parallel:
- **repo-research**: Understand existing patterns, file structure, conventions
- **learnings-research**: Search `docs/solutions/` for documented solutions to similar problems

### Step 2: External research decision

Determine if external research is needed based on:
- Security or payments involved → always research
- Unfamiliar framework or library → research
- High uncertainty → research

### Step 3: Consolidate research

Document:
- Relevant file paths
- Institutional learnings from `docs/solutions/`
- External URLs if researched
- CLAUDE.md conventions that apply

### Step 4: Choose detail level

| Level | When |
|-------|------|
| MINIMAL | Quick bugs, small improvements (<1 hour) |
| MORE | Standard features (1 day) |
| A LOT | Major features, architectural changes (multi-day) |

### Step 5: Write the plan

Filename: `docs/plans/YYYY-MM-DD-<type>-<descriptive-name>-plan.md`

Include:
- **Goal** — What we're building and why
- **Background** — Relevant context from research
- **Implementation tasks** — Ordered checklist
- **Files to modify** — Specific paths
- **Testing approach** — How to verify it works
- **Open questions** — Unknowns to resolve during work

### Step 6: Present options

After writing the plan:
1. Start `/ce:work` — begin execution
2. Run `/ce:review` — review the plan first
3. Refine — adjust the plan
4. Run `/deepen-plan` — add more technical depth

## Critical Constraint

**NEVER CODE during planning.** Research and document only. If you catch yourself writing implementation code, stop and put it in the plan as a task instead.
