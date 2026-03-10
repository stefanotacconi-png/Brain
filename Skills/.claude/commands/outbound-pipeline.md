# Outbound Pipeline

Run the full end-to-end outbound campaign: ICP scoring → lead enrichment → AI copywriting → push to sequencer. One prompt. No tab switching. No copy-paste.

## What this skill does

Orchestrates the entire outbound workflow from a raw company list to a live campaign in Instantly. This is the "single prompt" workflow demonstrated by ColdIQ — what used to take a team days now takes one person minutes.

## Instructions

Start by confirming context with the user:

1. Ask: "Which company list CSV in /data/ should we use?"
2. Ask: "What's the goal of this campaign? (e.g. book discovery calls, promote a service)"
3. Ask: "Any ICP adjustments for this specific campaign, or use CLAUDE.md defaults?"
4. Ask: "Which campaign name should I use in Instantly?"

Then run each stage sequentially, reporting progress after each:

---

### Stage 1 — ICP Scoring
- Run the logic from `/score-and-segment` skill (quick mode)
- Score all companies, assign tiers
- Save to `/output/scored_[date].csv`
- Report: Tier breakdown summary
- **Checkpoint:** Show top 10 Tier 1 companies. Ask: "Continue to enrichment?"

---

### Stage 2 — Lead Enrichment
- Run the logic from `/enrich-leads` skill on Tier 1 + Tier 2 only
- Find decision-maker contacts via Apollo API
- Enrich emails via Prospeo/Wiza
- Save to `/output/enriched_[date].csv`
- Report: Contacts found, emails verified, not found
- **Checkpoint:** Show sample of 5 enriched leads. Ask: "Continue to copy generation?"

---

### Stage 3 — AI Copywriting
- Run the logic from `/cold-email-writer` skill
- Generate 3-step sequences for all verified leads
- Apply copy frameworks from `/templates/copy-frameworks.md`
- Save to `/output/campaign_copy_[date].csv`
- Report: Show 3 example email sets for review
- **Checkpoint:** Ask: "Does this copy look good? Continue to campaign push?"

---

### Stage 4 — Push to Lemlist
- Run the logic from `/push-to-lemlist` skill
- Create campaign → add email steps to sequence → upload leads with personalized variables
- Print full campaign summary before launch
- **Final checkpoint:** "Type YES to activate campaign."

---

### After Launch
- Log campaign ID, lead count, and launch time to `/output/session_log.md`
- Remind user: "Run `/campaign-analytics` in 3–5 days to pull performance data."

## Example Usage

```
/outbound-pipeline
```

Just run it — the skill will ask everything it needs.

## Why this matters

Before Claude Code:
- Clay for enrichment → Lemlist for campaign → manual copy-paste → hours of work

After Claude Code:
- One prompt → everything done in the terminal → minutes
