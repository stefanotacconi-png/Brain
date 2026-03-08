---
name: ce:work
description: Execute a plan. Read the plan, set up a branch/worktree, implement tasks, run tests, and ship. Use after /ce:plan.
---

# Work

Execute a work plan efficiently while maintaining quality. 80% planning and review, 20% execution — but when it's time to execute, move fast.

## When to Use

* After `/ce:plan` — the plan is ready
* "Start working", "Execute the plan", "Let's build this"
* When you have a clear plan file in `docs/plans/`

## Process

### Phase 1: Quick Start

1. Read the plan completely
2. Clarify any ambiguities upfront — don't start and discover blockers mid-way
3. Set up environment:
   - New feature → create a branch or worktree
   - Bug fix → continue on existing branch or create fix branch
   - Confirm with user if unclear

### Phase 2: Execute

Task loop:
1. Mark task in-progress
2. Implement following existing patterns (check CLAUDE.md for conventions)
3. Run system-wide test check — verify no callbacks or middleware broken
4. Write tests for the change
5. Commit when a logical unit is complete (don't batch everything into one commit)
6. Mark task complete, move to next

**Principles:**
- Follow existing code patterns — don't invent new approaches
- Test after each change, not just at the end
- Commit incrementally — small commits are easier to review and revert
- Mark all tasks completed before moving on

### Phase 3: Quality Check

1. Run full test suite and linting
2. For large refactors, security changes, or complex logic → invoke reviewer agents
3. Prepare operational validation plan (what to monitor post-deploy)

### Phase 4: Ship It

1. Create conventional commit: `type(scope): description`
2. Capture screenshots for any UI changes
3. Create pull request with monitoring details
4. Update plan status to `completed`

## Optional: Swarm Mode

For plans with 5+ independent tasks, spawn coordinated subagents to work in parallel with dependency management. Only use when tasks are truly independent.

## Key Principles

- Start fast: clarify upfront, then execute without overthinking
- Use reviewer agents selectively — large refactors, security, complex logic only
- "Mark all tasks completed before moving on" — no partial features
