# Outbound GTM Skills

Claude Code skills for B2B lead generation, outbound campaign automation, and LinkedIn marketing — based on the ColdIQ workflow demonstrated in "Claude Code just replaced your lead generation agency."

## What this does

One person can now do in minutes what used to take a full agency team days: score leads, enrich contacts, write personalized copy, and launch campaigns — all from the terminal.

## Skills

| Skill | Command | What it does |
|-------|---------|-------------|
| Full Pipeline | `/outbound-pipeline` | End-to-end: score → enrich → write → launch |
| ICP Scoring | `/icp-score` | Score + tier a company list against your ICP |
| Lead Enrichment | `/enrich-leads` | Find contacts + emails via Apollo + Prospeo |
| Cold Email Writer | `/cold-email-writer` | Generate personalized 3-step sequences |
| Push to Lemlist | `/push-to-lemlist` | Create campaign + upload leads + steps via Lemlist API |
| Campaign Analytics | `/campaign-analytics` | Pull stats, find winners, update frameworks |
| LinkedIn Engagers | `/linkedin-engagers` | Scrape post engagement → warm leads |
| LinkedIn Ads | `/linkedin-ad-campaign` | Create LinkedIn campaigns via Marketing API |

## Setup

1. Fill in your ICP definition in `CLAUDE.md`
2. Add your API keys in `CLAUDE.md` (Apollo, Instantly, Apify, Prospeo, LinkedIn)
3. Customize `templates/scoring-criteria.md` with your scoring rules
4. Customize `templates/copy-frameworks.md` with your messaging
5. Drop your company list CSV in `/data/`
6. Run `/outbound-pipeline` and follow the prompts

## Folder Structure

```
CLAUDE.md                    ← Agent brain: ICP, API keys, copy rules
/data/                       ← Input: company list CSVs
/output/                     ← Scored, enriched, copy, analytics
/templates/
  scoring-criteria.md        ← ICP scoring rubric
  copy-frameworks.md         ← Email frameworks + winning patterns
/.claude/commands/           ← All skills (slash commands)
```

## APIs Used

- **Apollo** — Lead/contact search
- **Prospeo / Wiza / FullEnrich** — Email enrichment + verification
- **Apify** — LinkedIn scraping
- **Lemlist** — Campaign creation, multichannel sequences, and analytics
- **LinkedIn Marketing API** — Programmatic ad campaigns
