# Campaign Analytics

Pull outbound campaign performance data from Lemlist, identify what's working, and save learnings back into your copy frameworks.

## What this skill does

Pulls live stats from Lemlist, surfaces insights about which copy, audiences, and sequence steps are driving replies, and updates your stored frameworks so every future campaign is smarter.

## Authentication

Basic Auth: empty username, API key as password.
Read `LEMLIST_API_KEY` from CLAUDE.md.
Base URL: `https://api.lemlist.com/api`

## Instructions

1. Ask: "Which campaign should I analyse?" — list available campaigns:
   - `GET /campaigns` → show campaign names and IDs for the user to pick from
2. Accept a campaign name or ID as `$ARGUMENTS` to skip the prompt

**Pull campaign-level stats:**
- `GET /v2/campaigns/{campaignId}/stats?startDate=<ISO>&endDate=<ISO>`
- Use today as `endDate` and campaign launch date as `startDate` (check `/output/session_log.md`)
- Key metrics returned: `nbLeads`, `messagesSent`, `delivered`, `opened`, `replied`
- Also returns a `steps` array with per-step breakdowns

**Pull activity feed for reply analysis:**
- `GET /activities?campaignId={campaignId}&type=emailReplied`
- Review reply content to identify which angles resonated

**Pull lead-level engagement data:**
- `GET /campaigns/{campaignId}/leads`
- Filter for leads where `replyCount > 0` to profile who responded

**Analyse patterns:**
- Which step (1/2/3) drove the most replies?
- Which subject lines had the highest open rate?
- Which job titles replied most?
- Which industries had the best engagement?
- What copy angle (pain-based / value / social proof / warm trigger) won?

**Print performance report:**
```
Campaign: [name]
Date range: [start] → [end]

Sent: X | Delivered: X (X%) | Opened: X (X%) | Replied: X (X%)

Step breakdown:
  Step 1 — Sent: X | Opened: X% | Replied: X%
  Step 2 — Sent: X | Opened: X% | Replied: X%
  Step 3 — Sent: X | Opened: X% | Replied: X%

Top responding title: [title]
Top responding industry: [industry]
Best subject line: "[subject]" — X% open rate
```

Save the full report to `/output/analytics_[campaign-name]_[YYYY-MM-DD].md`

Ask: "Should I update the copy frameworks in /templates/ based on these learnings?"
- If yes: append the winning angles, subject patterns, and what flopped to `/templates/copy-frameworks.md` under the "What's Working" table

## Example Usage

```
/campaign-analytics
```

or

```
/campaign-analytics "Q1 SaaS Founders Campaign"
```

## The Learning Loop

```
Launch campaign → Pull analytics → Find what worked → Update frameworks → Next campaign is smarter
```

## Benchmarks

| Metric | Below average | Good | Excellent |
|--------|--------------|------|-----------|
| Open rate | <20% | 30–50% | >50% |
| Reply rate | <1% | 2–5% | >5% |
| Bounce rate | >5% ⚠️ | 1–3% | <1% |

- Low open rate → subject line or deliverability problem
- High bounce rate → fix email enrichment step (use better verification)
- Good opens, low replies → body copy problem, revisit frameworks
- Step 1 outperforms Step 3 → follow-ups are weak, improve them

## Notes

- Run at day 3–5 for first signal (Step 1 data)
- Run again at day 14 for full sequence completion data
- Lemlist's `/v2/campaigns/{id}/stats` requires `startDate` and `endDate` in ISO 8601 format (e.g. `2026-01-01T00:00:00.000Z`)
- For multi-account reporting, run this skill once per campaign and consolidate in a summary file
