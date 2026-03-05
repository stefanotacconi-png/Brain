# Context Building

Build and maintain the Spoki GTM context file — the single source of truth that feeds all other skills. Four modes: Create, Update, Call Recording Capture, and Feedback Loop.

## What this skill does

Synthesizes product positioning, ICP insights, win cases, proof points, campaign history, and active hypotheses into a structured context file. All other skills read CLAUDE.md as their source, but this skill helps you extract and organize new signals — from HubSpot won deals, call transcripts, and campaign performance — and decide what to update in CLAUDE.md.

## Instructions

### Step 0 — Select mode

Ask: "Which mode?
1. **Create** — build context file from scratch (for a new campaign vertical or market)
2. **Update** — add new win cases, proof points, or ICP refinements
3. **Call Recording Capture** — extract GTM signals from a call transcript
4. **Feedback Loop** — import campaign metrics and update hypotheses"

Or accept `$ARGUMENTS` as the mode name.

---

## Mode 1: Create

Build a campaign-specific context file for a vertical or market not yet in CLAUDE.md.

### Step 1 — Pull HubSpot data for the vertical

Read `HUBSPOT_API_KEY` from environment or ask the user to provide it.

Search HubSpot deals for wins in the target vertical:
- `GET https://api.hubapi.com/crm/v3/objects/deals/search`
- Filter: `dealstage = closedwon` + industry contains [vertical keyword]
- Pull: `dealname`, `amount`, `closedate`, `company`, `hs_analytics_source`

If HubSpot access is unavailable, ask user to describe 2–3 representative won deals.

### Step 2 — Interview the user

Ask (conversationally, not as a form):

**About the vertical:**
- What types of companies are you targeting? (size, structure, geography)
- What's the primary pain you believe Spoki solves for them?
- What makes a company in this vertical a bad fit?

**About the product for this use case:**
- Which Spoki features are most relevant here?
- What's the ROI story specific to this vertical?

**About past deals:**
- Tell me about the best win you've had here. What triggered the purchase?
- Any lost deals or churned customers to learn from?

**About contacts:**
- Which persona signs? Which persona champions?
- Any recurring objections?

### Step 3 — Generate context file

Save to `/output/context/[vertical-slug]_context.md`

Structure:

```markdown
# GTM Context: [Vertical] — [Geography]
Created: [date]
Source: HubSpot won deals + CLAUDE.md + user input

## What We Do (for this vertical)
[Product positioning specific to this vertical's pain]
[Key metrics most relevant here]

## ICP for This Vertical
- Company size: [range]
- Revenue: [range]
- Structure: [e.g. franchise vs independent, chains vs boutiques]
- Geography: [primary targets]
- Disqualified: [what makes a company a bad fit in this vertical]

## Buyer Personas
- Decision maker: [title + context]
- Champion: [title + context]
- Approach: [SME direct vs mid-market champion-first]

## Win Cases
### [Company Name] — [Deal value] — [Close date]
- Trigger: [what made them look for a solution]
- Pain: [specific workflow problem]
- Value delivered: [outcome with numbers if available]
- Time to close: [N days]
- Source: [HubSpot deal ID or user-provided]

## Proof Library
[Pre-written email sentences, mapped to audience size and pain]
e.g. "For a beauty clinic your size, we typically see no-show rates drop 60% in the first 90 days."

## Active Hypotheses
[List hypothesis short names + status — imported from hypothesis_set.md]

## Campaign History
[Empty at creation — updated via Feedback Loop mode]

## Voice Rules (vertical-specific)
[Tone adjustments, banned phrases, CTA preferences for this vertical]

## DNC List
[Domains or companies to exclude from outreach]
```

---

## Mode 2: Update

Add new information to an existing context file without overwriting prior entries.

### Step 1 — Select the file

Ask: "Which context file should I update?" List files in `/output/context/`. Or accept file path from `$ARGUMENTS`.

### Step 2 — Identify update type

Ask: "What are you adding?
- New win case
- New proof point
- ICP refinement (something you've learned about the target buyer)
- DNC addition (company or domain to exclude)
- Hypothesis revision"

### Step 3 — Append

Add to the relevant section with date stamp. Never overwrite existing entries — append with `[Updated: YYYY-MM-DD]` tag.

For win cases: pull from HubSpot if available, or take user input.

---

## Mode 3: Call Recording Capture

Extract GTM signals from a sales call or discovery call transcript.

### Step 1 — Load transcript

Ask: "Please paste the call transcript or provide the file path."

If a file path is given, read the file.

### Step 2 — Extract signals

Parse the transcript for:

**ICP signals:**
- Company size, structure, and tech stack mentioned by the prospect
- Role of the person on the call and who else was involved
- What they said they currently use (tools, workflows)
- What they said is broken or painful

**Buying signals:**
- Problems they described in their own words (save exact quotes)
- Competitor tools mentioned (buying signal — see CLAUDE.md)
- Timeline urgency signals
- Budget signals

**Proof point candidates:**
- Metrics or outcomes the prospect reacted positively to
- Analogies or examples that landed — note what made them click

**Hypothesis validation/refutation:**
- Which hypotheses from the active hypothesis set did this call confirm?
- Which did it contradict?
- Any new hypothesis candidate not in the set?

**DNC signals:**
- Anything suggesting this company or contact is a bad fit permanently

### Step 3 — Output structured summary

```
CALL SUMMARY — [Date] — [Company] — [Prospect role]

ICP SIGNALS:
- [signal 1]
- [signal 2]

BUYING SIGNALS:
- [signal with exact quote if available]

PROOF POINTS THAT LANDED:
- [what resonated and why]

HYPOTHESIS UPDATE:
- #[N] [name]: CONFIRMED / REFUTED / NEW CANDIDATE
  Evidence: [what was said]

DNC:
- [if applicable]

RECOMMENDED ACTIONS:
1. [e.g. Add to Tier 1 outreach with hypothesis #2 angle]
2. [e.g. Update hypothesis #3 — prospect didn't recognize the pain]
3. [e.g. Add [Company] to DNC — pure B2B, wrong fit]
```

### Step 4 — Append to context file

Ask: "Should I append these signals to `/output/context/[vertical]_context.md`?"

On confirmation, add to relevant sections with date stamp.

---

## Mode 4: Feedback Loop

Import campaign performance data and update hypotheses based on what's working.

### Step 1 — Load campaign metrics

Ask: "Which campaign should I analyze? Provide the Lemlist campaign name or ID, or the analytics CSV from `/output/`."

If Lemlist campaign ID is provided:
- Read `LEMLIST_API_KEY` from CLAUDE.md
- `GET https://api.lemlist.com/api/campaigns/{campaignId}/stats`
- Pull: emails sent, open rate, reply rate, click rate, bounce rate, unsubscribes

If CSV provided, read columns: `email`, `step`, `opened`, `replied`, `clicked`, `bounced`

### Step 2 — Segment by hypothesis

Join metrics to the segmented lead file from `/output/segmented_*.csv` using email as the key.

Calculate per-hypothesis:
- Open rate, reply rate, click rate
- Which variant (A/B/C/D) performed best
- Which Tier (1 vs 2) had better engagement

### Step 3 — Update hypotheses

For each hypothesis:

**If reply rate > 5%:** Mark as **Validated** — expand this angle in next campaign
**If reply rate 2–5%:** Mark as **Promising** — test with better personalization
**If reply rate < 2%:** Mark as **Underperforming** — revise or retire

Update the hypothesis set file at `/output/hypothesis_set_[vertical-slug].md` with new status tags and evidence.

### Step 4 — Recommend next actions

Output:

```
FEEDBACK LOOP — [Campaign name] — [Date]

Performance summary:
- Emails sent: X | Opens: X% | Replies: X% | Clicks: X%

Hypothesis performance:
- #1 [Name]: X% reply rate → [Validated / Promising / Underperforming]
- #2 [Name]: X% reply rate → [...]

Best-performing variant: [A/B/C/D] — [why, based on data]
Worst-performing segment: [e.g. Tier 2 with hypothesis #3]

RECOMMENDED ACTIONS:
1. [e.g. Expand hypothesis #2 angle into next campaign]
2. [e.g. Retire hypothesis #4 — 0.8% reply rate across 45 sends]
3. [e.g. Re-enrich Tier 3 holds and re-test with hypothesis #1]
4. [e.g. Update cold-email-writer template — subject line variant C outperformed A by 3x]
```

Save to `/output/feedback_loop_[campaign]_[YYYY-MM-DD].md`
Append summary to `/output/session_log.md`

---

## Example Usage

```
/context-building create beauty-italy
```

```
/context-building update
```

```
/context-building call-recording
```
(then paste transcript)

```
/context-building feedback-loop "ITA Beauty Q1"
```

## Notes

- CLAUDE.md is the master context — this skill extracts and organizes signals to inform updates to it, but edits to CLAUDE.md itself should be confirmed with the user
- HubSpot integration requires API access — if unavailable, all modes work with user-provided information
- Call Recording Capture is the fastest way to turn discovery calls into GTM intelligence — run it same day as the call
- Feedback Loop should run after every Lemlist campaign reaches 2+ weeks of sends
