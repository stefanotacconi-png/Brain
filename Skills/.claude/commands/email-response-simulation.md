# Email Response Simulation

Simulate how a specific high-value Tier 1 prospect would react to your draft cold email — before you send it. Uses a dual-pass evaluation: 2-second gut reaction, then 10-second business assessment.

## What this skill does

Builds a vivid professional "world" for an individual prospect using Apollo + LinkedIn data, then runs a skeptical buyer evaluation against your draft email copy. Outputs a Yes/Maybe/No verdict, ranked risk flags, and a rewritten copy fix.

Use for individual Tier 1 prospects only — not bulk lists. Run 3–5 simulations per campaign to identify systematic copy problems before you push to Lemlist.

## Instructions

### Step 1 — Identify the prospect

Accept `$ARGUMENTS` as either:
- A prospect's full name + company (e.g. `"Marco Rossi, Tempocasa"`)
- A row number from the most recent `/output/campaign_copy_*.csv`

If not provided, ask: "Which prospect should I simulate? Provide name + company or a CSV row number."

### Step 2 — Gather enrichment data

Pull what's available without API calls first — check if the prospect appears in any `/output/enriched_leads*.csv` file.

If not found, use Apollo People Search to get LinkedIn URL, job title, seniority, and department:
- Read `APOLLO_API_KEY` from CLAUDE.md
- `POST https://api.apollo.io/v1/people/search` with `q_person_name` + `q_organization_name`
- Extract: `name`, `title`, `linkedin_url`, `organization.name`, `organization.industry`, `seniority`, `departments`

Then fetch public LinkedIn activity if possible (recent posts, articles, engagement patterns) via web search: `site:linkedin.com/in/ [name] [company]`

### Step 3 — Build the prospect's world

Construct a simulation profile covering:

**Professional reality**
- Daily pressures and KPIs (what they're measured on)
- Tools and workflows they manage
- Team size and reporting structure (from title/seniority)
- Decision-making style (data-driven vs relationship-driven — infer from title + industry)

**Inbox behaviour**
- Volume: how many cold emails does this persona typically receive per week?
- Filter: do they read subject lines or just sender names?
- Bias: what makes them click vs archive in 2 seconds?

**Communication preferences**
- Tone: formal/informal — use industry + country signals (Italy = more formal, Spain = varies by age)
- Format: do they prefer short punchy or structured reasoning?
- CTA sensitivity: are they calendar-link averse or efficiency-seeking?

State assumptions explicitly when data is thin.

### Step 4 — Load the draft email

Read the draft from:
1. The row in `/output/campaign_copy_*.csv` matching this prospect (columns: `subject_1`, `body_1`)
2. Or ask the user to paste the subject + body directly

### Step 5 — Run dual-pass evaluation

**Pass 1 — Emotional gut reaction (2 seconds)**
Read as the prospect. First impression only:
- Subject line: does it trigger curiosity or feel like spam?
- Sender name: recognized or cold?
- First sentence: personalized hook or generic opener?
- Tone: does it feel like it was written for them or copy-pasted?
- Verdict: delete / keep reading?

**Pass 2 — Business assessment (10 seconds)**
Now they're reading the body:
- KPI alignment: does the pain mentioned match what they're actually measured on?
- Credibility: are the proof points from peers their size and industry?
- Effort-to-value ratio: is the CTA proportional to the value claimed?
- Priority level: does this solve a top-3 problem or a nice-to-have?
- Trust: do they have any reason to believe you?

### Step 6 — Output verdict

```
PROSPECT: [Name] — [Title] at [Company]
WORLD: [3-sentence summary of their professional reality]

PASS 1 — GUT REACTION (2 sec)
[What they feel. Be blunt. "They archive this." is a valid output.]

PASS 2 — BUSINESS ASSESSMENT (10 sec)
[What their rational brain says. Connect to their actual KPIs.]

VERDICT: [YES / MAYBE / NO]
Reason: [1-2 sentences grounded in their specific context]

RISK FLAGS (ranked by severity):
1. [Highest-impact problem — e.g. "Pain claim doesn't match their role's KPIs"]
2. [Second issue]
3. [Third issue if relevant]

REWRITTEN VERSION:
Subject: [rewritten subject]
Body: [rewritten email body — same word limit as original]
Key changes: [bullet list of what changed and why]
```

### Step 7 — Pattern analysis (after 3+ simulations)

If the user has run this skill 3 or more times in the current session, add a pattern summary:
- What's failing consistently across prospects?
- Is it the subject line, the pain framing, the CTA, or the proof points?
- Recommend one template-level fix (not prospect-level)

## Example Usage

```
/email-response-simulation "Carla Vega, Tempocasa"
```

```
/email-response-simulation 3
```

## Notes

- The bridge between prospect pain and your solution is the most important thing to evaluate — more than copywriting quality
- If deletion is the likely outcome, say so directly — polite feedback is useless here
- Country matters: Italian recipients expect more formality; Spanish vary significantly by age and sector
- If Apollo returns no match, proceed with role-based assumptions and flag that enrichment was unavailable
- Save simulation outputs to `/output/response_sim_[prospect]_[YYYY-MM-DD].md` for pattern review later
