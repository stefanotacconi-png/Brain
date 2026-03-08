---
name: kw:compound
description: Extract 1-3 learnings from a session and save them to docs/knowledge/ for automatic surfacing in future planning. Use at the end of any session where something worth remembering was discovered.
---

# Compound

Extract and preserve learnings from completed work. Saves to `docs/knowledge/` so `/kw:plan` automatically surfaces them in future sessions.

## When to Use

* End of any session where something worth remembering was discovered
* After validating a hypothesis (confirmed or disproved)
* After figuring out what works (or what doesn't) in a campaign
* After fixing a non-obvious problem

## Process

### Step 1: Identify learnings (1–3 max)

Scan the session for compoundable insights. Look for signals:

| Signal | Learning type |
|--------|--------------|
| "We discovered that..." | Insight |
| "The process was: do X then Y" | Playbook |
| "We thought X but actually Y" | Correction |
| "Every time we do X, Y happens" | Pattern |

Only extract learnings that are:
- **Specific** — concrete enough to act on
- **Non-obvious** — not something you'd find in a Google search
- **Reusable** — applicable beyond this one session

### Step 2: Draft and get approval

Present drafted learnings before saving anything:

```
## Learnings to Save

### 1. [Title]
**Type:** [Insight / Playbook / Correction / Pattern]
**Tags:** [keywords that will trigger retrieval]
**Learning:** [The insight in 2-4 sentences. Be specific.]
**Confidence:** [High / Medium / Low — based on how validated this is]

### 2. [Title]
...
```

Ask: "Save these? You can approve, edit, skip any, or add others."

**Never auto-save without explicit user approval.**

### Step 3: Check for duplicates

Before writing, search `docs/knowledge/` for existing entries on the same topic:

```
Grep: [learning keywords] in docs/knowledge/
```

If a related entry exists, ask: "Update the existing entry or create a new one?"

### Step 4: Write to docs/knowledge/

For each approved learning, write to `docs/knowledge/{descriptive-slug}.md`:

```markdown
---
type: [insight | playbook | correction | pattern]
tags: [tag1, tag2, tag3]
confidence: [high | medium | low]
created: [YYYY-MM-DD]
source: [session context — campaign name, project, etc.]
---

# [Learning Title]

## The Learning

[2-4 sentences. Specific, concrete, actionable.]

## Context

[When this was discovered. What we were doing.]

## Evidence

[What data or results support this. Be specific — numbers, outcomes.]

## How to Use

[When to apply this. What it changes about how you'd approach similar work.]

## Caveats

[Conditions where this might not apply. Confidence qualifiers.]
```

### Step 5: Confirm and summarize

Show saved files and list the tags that will trigger retrieval:

```
## Saved

- `docs/knowledge/real-estate-cold-email-response-rate.md`
  Tags: real-estate, cold-email, response-rate, spain

- `docs/knowledge/pet-industry-fast-close-pattern.md`
  Tags: pet, close-speed, outbound, tier-1

These will surface automatically in future `/kw:plan` sessions when you work on related topics.
```

## Important Rules

* **Quality over quantity.** 1 great learning beats 3 mediocre ones.
* **Never auto-save.** Always get explicit approval before writing.
* **Be specific.** "Real estate leads in Spain close 30% faster when we reference Tempocasa in the opener" not "personalization helps."
* **Check for duplicates.** Don't create redundant entries.
* **Tag for discovery.** Tags are how future `/kw:plan` finds these. Choose tags you'd actually search for.
* **Mark confidence accurately.** A pattern seen once is Low confidence. A pattern validated across 10 campaigns is High.
