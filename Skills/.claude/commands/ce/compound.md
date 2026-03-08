---
name: ce:compound
description: Document a recently solved problem while context is fresh. Creates structured solution docs in docs/solutions/ for future reuse. Auto-triggers when you say "that worked", "it's fixed", or "problem solved".
---

# Compound

Capture problem solutions while context is fresh. Creates searchable documentation in `docs/solutions/` so the team never solves the same problem twice.

## When to Use

* After fixing a tricky bug
* After figuring out a non-obvious integration
* When you say "that worked", "it's fixed", or "problem solved"
* After any session where something was learned that's worth preserving

**Auto-triggers** when phrases like "that worked", "it's fixed", or "problem solved" are detected.

## Usage

```
/ce:compound                    # Document most recent fix
/ce:compound [context]          # With additional context about what was solved
```

## Process

### Phase 1: Parallel analysis (5 simultaneous agents)

Each agent returns text data only — no files created yet:

1. **Context agent** — What was the problem? What environment/stack?
2. **Solution agent** — What was the fix? Why did it work?
3. **Documentation agent** — Are there related docs to link or update?
4. **Prevention agent** — How could this be caught earlier next time?
5. **Category agent** — Which folder does this belong in?

### Phase 2: Write the solution doc

Orchestrator collects all agent results and writes ONE final file:

**Path:** `docs/solutions/{category}/{descriptive-slug}.md`

**Categories:**
- `performance-issues/`
- `security-issues/`
- `test-failures/`
- `database-issues/`
- `integration-issues/`
- `build-deploy-issues/`
- `ui-ux-issues/`
- `data-issues/`

**File format:**
```markdown
# [Problem Title]

**Category:** [category]
**Date:** [YYYY-MM-DD]
**Tags:** [searchable keywords]

## Problem

[What was happening and why it was hard to solve]

## Root Cause

[The actual underlying issue]

## Solution

[Exactly what fixed it — code, commands, config changes]

## Why It Works

[The explanation — useful for next time]

## Prevention

[How to catch this earlier: tests, linting rules, code review checklist items]

## References

[Links to PRs, issues, docs, Stack Overflow]
```

### Phase 3: Optional enhancement

Based on problem type, specialized reviewers may enhance the doc:
- Performance oracle (for perf issues)
- Security sentinel (for security issues)

## Key Constraint

Only **ONE file** is written — the final documentation. Subagents provide text data; they never create intermediate files.
