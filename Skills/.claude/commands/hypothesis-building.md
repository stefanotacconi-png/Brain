# Hypothesis Building

Generate testable pain hypotheses from CLAUDE.md and your knowledge of the target vertical. No API keys. Pure reasoning from context + conversation. Outputs a hypothesis set that drives list building, segmentation, and email copy.

## What this skill does

Extracts patterns from the ICP, win cases, and product knowledge in CLAUDE.md, then generates 3–7 specific, mechanism-driven hypotheses for a target vertical. Each hypothesis includes a search angle that tells `/apollo-list` and `/list-segmentation` exactly what to look for.

Sits between context knowledge and list building. Use it when entering a new vertical or refining an underperforming campaign.

## Instructions

### Step 1 — Confirm the target vertical

Accept `$ARGUMENTS` as the vertical slug (e.g. `healthcare-italy`, `automotive-spain`), or ask:
"Which vertical and geography are you targeting? (e.g. healthcare-italy, automotive-spain)"

Check if a hypothesis set already exists at `/output/hypothesis_set_[vertical-slug].md`. If yes, enter **Refine Mode** (see below).

### Step 2 — Read CLAUDE.md context

Extract the following from CLAUDE.md:

**From ICP definition:**
- Target company profile (size, revenue, geography, B2C/D2C filter)
- Disqualified company types

**From Target Industries table:**
- Where this vertical sits in priority order
- Whether it's validated (won deals) or hypothesis
- Any notes on deal speed, deal size, or buyer behaviour

**From Won deals / CRM learnings:**
- Specific won deals in or adjacent to this vertical
- What triggered the purchase (the pain that closed the deal)
- Time-to-close benchmarks for this segment

**From Pain → Solution map:**
- The primary pain and solution hook already defined for this vertical (as a starting reference)

**From Buying signals:**
- Which signals are highest priority for this type of company

### Step 3 — Gather vertical knowledge from user

Ask conversationally (skip questions the user already answered):

1. "What do you know about how [vertical] companies operate day-to-day?"
2. "What manual processes or communication failures do you think slow them down most?"
3. "Have you seen any buying signals from this vertical recently? (LinkedIn posts, job postings, competitor use)"
4. "Are there sub-segments within [vertical] that might have different pain intensities? (e.g. independent clinics vs chains, franchise vs independent real estate agencies)"
5. "Any companies you'd like to use as seeds or reference points?"

Keep it conversational — one exchange is enough if the user gives rich context upfront.

### Step 4 — Extract patterns from win cases

For each relevant win case in CLAUDE.md (same or adjacent vertical), extract:

1. **Trigger** — what event or pain made them look for a solution?
2. **Workflow gap** — what were they doing before? What broke?
3. **Value delivered** — what specific outcome did Spoki provide?
4. **Transferability** — does this pattern map to the target vertical?

Map these patterns to candidate hypotheses.

### Step 5 — Draft hypotheses

Generate 3–7 hypotheses. Each must have:

**Short name** — 3-5 word label (e.g. "Portal lead speed", "No-show volume pain")

**Description** — 2-3 sentences:
- The specific pain and why it exists in this vertical
- Why it's costly (lost revenue, wasted staff time, customer churn)
- Why Spoki solves it (mechanism, not just "WhatsApp helps")

**Best fit** — what type of company within the vertical this applies to most (e.g. "Independent aesthetic clinics with 2-5 practitioners and Meta Ads running", "Real estate franchise networks with >5 branches")

**Search angle** — 1-2 concrete Apollo search queries or company description criteria to find these companies. Be specific enough that `/apollo-list` can use them directly.

**Quality check per hypothesis:**
- Is it specific to a workflow or business moment, not a vague trend?
- Can a prospect confirm it from their own experience in 5 seconds?
- Does it connect directly to a Spoki capability (not a random pain)?
- Is the search angle concrete enough to drive a list query?

### Step 6 — Review with user

Present the full hypothesis set and ask:
- "Do these match what you know about [vertical]?"
- "Any hypotheses to add, merge, or drop?"
- "Are the search angles specific enough for Apollo?"

Refine based on feedback — expect 1-2 rounds. This is meant to be interactive.

### Step 7 — Save

Save to `/output/hypothesis_set_[vertical-slug].md`

Create the `/output/` directory if it doesn't exist.

## Output Format

```markdown
# Hypothesis Set: [Vertical] — [Geography]
Generated: [date]
Based on: CLAUDE.md ICP + [N] relevant won deals

---

### #1 [Short name]
[2-3 sentence description — the pain, why it exists, why Spoki fits]
**Best fit:** [company type within the vertical]
**Search angle:** [1-2 Apollo search queries or company criteria]

### #2 [Short name]
[description]
**Best fit:** [company type]
**Search angle:** [criteria]

...
```

## Refine Mode

When `/output/hypothesis_set_[vertical-slug].md` already exists:

1. Read the existing hypothesis set
2. Ask: "What's changed since this was written? (new wins, campaign results, replies received)"
3. Update, merge, or add hypotheses based on new evidence
4. Note what changed and why at the top of the file
5. Preserve hypothesis numbering (`#N`) wherever possible — downstream skills reference by number

## Example Usage

```
/hypothesis-building beauty-italy
```

```
/hypothesis-building healthcare-spain
```

```
/hypothesis-building real-estate
```
(will ask for geography)

## Downstream consumers

The hypothesis set is used by:
- `/list-segmentation` — matches companies to hypotheses for tiering
- `/email-prompt-building` — hypotheses become P1 email angles
- `/cold-email-writer` — personalized openers per hypothesis
- `/email-response-simulation` — evaluates copy alignment with hypotheses

## Notes

- Validated verticals (Beauty, Real Estate, Fashion, Travel, Education, Pet) have won deal evidence in CLAUDE.md — use those patterns as anchors
- Hypothesis verticals (Healthcare, Automotive, Finance) need more user input — ask more questions in Step 3
- 3 strong hypotheses beat 7 vague ones — it's better to go narrow and iterate
- After a campaign runs, come back and run Refine Mode with actual reply data
