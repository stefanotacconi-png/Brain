# ICP Score

Score and tier a list of companies against the Ideal Customer Profile defined in CLAUDE.md.

## What this skill does

Takes a CSV of companies and scores each one against the ICP criteria, assigning Tier 1 / Tier 2 / Tier 3 or Disqualified. Outputs a scored CSV to `/output/`.

## Instructions

1. Ask the user: "Which CSV file in /data/ should I score?" (or accept `$ARGUMENTS` as the filename)
2. Read the ICP definition and scoring tiers from CLAUDE.md
3. Also read `/templates/scoring-criteria.md` if it exists for detailed scoring rules
4. For each company row in the CSV:
   - Evaluate each ICP dimension (industry, size, revenue, geography, signals)
   - Assign a tier: Tier 1, Tier 2, Tier 3, or Disqualified
   - Add a short `scoring_reason` column explaining why (1–2 sentences)
5. Save the scored output to `/output/scored_[original_filename]_[YYYY-MM-DD].csv`
6. Print a summary table:
   - Total companies processed
   - Count per tier
   - Top 5 Tier 1 companies with their reasons
7. Ask: "Should I proceed to lead enrichment for Tier 1 and Tier 2 companies?"

## Input Format Expected

CSV with at minimum: `company_name`, `website`, `industry`, `employee_count`

Optional columns that improve scoring: `revenue`, `funding_stage`, `location`, `technologies_used`, `linkedin_url`

## Output Format

Original CSV columns + new columns:
- `tier` (Tier 1 / Tier 2 / Tier 3 / Disqualified)
- `tier_score` (1–10 numeric)
- `scoring_reason` (brief explanation)

## Example Usage

```
/icp-score companies.csv
```

or just `/icp-score` and the skill will ask which file to use.
