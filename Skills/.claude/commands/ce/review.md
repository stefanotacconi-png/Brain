---
name: ce:review
description: Exhaustive multi-agent code review using parallel agents, deep analysis, and Git worktrees. Use before merging any non-trivial PR.
---

# Review

Perform a deep code review using parallel AI agents and structured analysis. Covers security, performance, architecture, and quality.

## When to Use

* Before merging a PR
* "Review this PR", "Check my code", "Is this ready to merge?"
* After `/ce:work` completes on a complex change

## Process

### Step 1: Setup & target

Identify the review target:
- PR number or GitHub URL
- Branch name
- File path for focused review

Ensure the correct code is checked out before analysis begins.

### Step 2: Parallel agent execution

Run review agents simultaneously:
- Security sentinel — vulnerabilities, injection, auth issues
- Performance oracle — bottlenecks, N+1 queries, memory leaks
- Architecture reviewer — patterns, coupling, separation of concerns
- Test coverage checker — missing tests, edge cases
- Accessibility reviewer (always runs)
- Pattern researcher (always runs)
- Database migration reviewer (activates if schema changes detected)

### Step 3: Deep analysis

Structured review through multiple lenses:
- **Technical excellence** — correctness, edge cases, error handling
- **Business value** — does it solve the right problem?
- **Risk management** — what could go wrong post-deploy?
- **Team dynamics** — readability, maintainability, knowledge transfer

### Step 4: Findings synthesis

1. Consolidate all agent findings
2. Remove duplicates
3. Assign severity:
   - **P1** — Blocks merge. Must fix. (security issues, data loss risk, broken functionality)
   - **P2** — Should fix before merge. (performance issues, missing error handling)
   - **P3** — Nice to fix. (style, minor improvements)
4. Write structured todo file to `todos/`

### Step 5: Summary

Present comprehensive findings report. Offer testing options based on project type (browser or Xcode).

## Critical Protections

`docs/plans/*.md` and `docs/solutions/*.md` are **never** flagged for deletion. Such recommendations are discarded during synthesis.

## P1 Policy

Any P1 finding **blocks merge approval**. Must be resolved before the PR is accepted.
