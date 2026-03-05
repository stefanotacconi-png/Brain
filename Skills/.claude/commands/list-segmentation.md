# List Segmentation

Tier an enriched company list by combining ICP fit AND data completeness — so email generation uses the right template for each prospect and thin-data contacts don't get fake personalization.

## What this skill does

Takes an enriched CSV (from `/enrich-leads` or `/icp-score`) and evaluates each company on two independent dimensions: hypothesis fit and enrichment data quality. Outputs a tiered CSV ready for `/cold-email-writer` or `/email-prompt-building`.

**Key difference from `/icp-score`:** `/icp-score` scores ICP fit only. This skill also gates by data completeness — a perfect-fit prospect with 2 blank enrichment fields gets Tier 2 (templated), not Tier 1 (personalized). This prevents generating hollow personalization that destroys deliverability.

## Instructions

### Step 1 — Load inputs

Accept `$ARGUMENTS` as the path to an enriched CSV, or ask: "Which enriched CSV should I segment?" (default: most recent `/output/enriched_leads*.csv`)

Also load:
- Hypothesis set from `/output/hypothesis_set_[vertical-slug].md` — ask which vertical if ambiguous
- ICP definition and tiers from CLAUDE.md

### Step 2 — Define enrichment fields to evaluate

Identify which CSV columns count as "enrichment data" vs basic company info:

**Basic fields (don't count toward enrichment score):**
`company_name`, `website`, `industry`, `employee_count`, `location`, `email`, `firstName`, `lastName`

**Enrichment fields (count toward data quality score):**
Any column added by Apollo enrichment or manual research — e.g.:
- `technologies_used`, `crm_tool`, `whatsapp_tool` (buying signals)
- `recent_news`, `linkedin_posts`, `job_postings` (behavioural signals)
- `revenue_estimate`, `funding_stage` (size signals)
- `persona_role_match`, `decision_maker_reachable` (contact quality)
- Any custom columns from hypothesis-driven enrichment

Count how many enrichment fields are non-empty and non-"N/A" for each row.

### Step 3 — Evaluate hypothesis fit

For each company, check alignment with each hypothesis in the hypothesis set:

Read each hypothesis's "Best fit" description and "Search angle" from the hypothesis set file.

Score alignment:
- **Strong (4-5):** Company description or enrichment data directly matches the hypothesis mechanism
- **Medium (2-3):** Partial match — industry fits but no confirming signal
- **Weak (0-1):** Industry tangential or no data to confirm

Assign one **primary hypothesis** per company — the strongest match.

If no hypothesis matches above 2, flag for hold.

### Step 4 — Assign tiers

Use this two-dimensional grid:

| | Strong hypothesis fit (4-5) | Medium fit (2-3) | Weak fit (0-1) |
|---|---|---|---|
| **Rich data (3+ enrichment fields)** | **Tier 1** — Personalized | **Tier 2** — Templated | **Tier 3** — Hold |
| **Moderate data (1-2 fields)** | **Tier 2** — Templated | **Tier 2** — Templated | **Tier 3** — Hold |
| **Thin data (0 fields)** | **Tier 2** — Templated (no personalization) | **Tier 3** — Hold | **Disqualified** |

**Tier 1 — Personalized outreach:**
- Strong hypothesis fit + 3+ enrichment fields populated + clear engagement hook (recent news, hiring signal, competitor tool detected, or relevant LinkedIn post)
- These get fully personalized email from the prompt template

**Tier 2 — Templated outreach:**
- Medium fit OR data-rich without a clear hook
- Use variant-based templates (role-matched) without specific personalization triggers

**Tier 3 — Hold:**
- Weak fit, sparse data, or hypotheses don't match
- Flag for re-enrichment or next campaign cycle

**Disqualified:**
- No enrichment data at all + weak hypothesis fit
- Or: pure B2B, public sector, non-commercial (CLAUDE.md disqualification rules still apply)

### Step 5 — Add buying signal override

Even if a company scores Tier 2 on the grid above, **upgrade to Tier 1** if any of these signals are present (from CLAUDE.md buying signals):

| Signal | Column to check |
|--------|----------------|
| Currently using a competitor WhatsApp tool | `whatsapp_tool`, `technologies_used` |
| Running Meta/Google Ads without WA automation | `ad_channels`, `technologies_used` |
| Hiring customer service or marketing roles | `job_postings` |

Flag the override reason in the `tier_reason` column.

### Step 6 — Output

Save to `/output/segmented_[original_filename]_[YYYY-MM-DD].csv`

Add these columns to the original CSV:
- `tier` (Tier 1 / Tier 2 / Tier 3 / Disqualified)
- `primary_hypothesis` (hypothesis short name from hypothesis set — e.g. "#2 No-show pain")
- `enrichment_score` (count of non-empty enrichment fields)
- `hypothesis_fit` (Strong / Medium / Weak)
- `tier_reason` (1-2 sentences — why this tier, what data confirmed it)
- `buying_signal` (if override applied — what signal was detected)

Print a summary table:

```
SEGMENTATION SUMMARY — [Campaign name]
Total companies: X
  Tier 1 (Personalized): X (X%)
  Tier 2 (Templated): X (X%)
  Tier 3 (Hold): X (X%)
  Disqualified: X (X%)

Primary hypothesis distribution:
  #1 [Name]: X companies
  #2 [Name]: X companies
  ...

Buying signal overrides: X companies upgraded to Tier 1
Top 5 Tier 1 companies: [list with tier_reason]
```

### Step 7 — Handoff options

Ask:
"Segmentation complete. Next steps:
1. Run `/cold-email-writer` on Tier 1 + Tier 2 with the prompt template
2. Run `/email-response-simulation` on your top 3 Tier 1 prospects before generating at scale
3. Re-enrich Tier 3 companies via `/enrich-leads` to fill data gaps

Which would you like to do?"

## Example Usage

```
/list-segmentation /output/enriched_leads_real-estate-spain.csv
```

```
/list-segmentation
```
(will ask which file and which hypothesis set to use)

## Notes

- Tier 1 should typically be 10–20% of your list — if you're getting 40%+, your hypothesis fit criteria are too loose
- Never generate fully personalized emails for Tier 3 — blank enrichment fields produce "Hi {{firstName}}, I noticed your company..." which destroys trust
- The `primary_hypothesis` column is what drives which email variant gets used in `/cold-email-writer`
- Buying signal overrides should be reviewed manually before push — confirm the signal is real, not a false positive
- Save the summary to `/output/session_log.md`
