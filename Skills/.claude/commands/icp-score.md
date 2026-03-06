# ICP Score

Score and tier a list of companies against the Ideal Customer Profile defined in CLAUDE.md.

## What this skill does

Takes a CSV of companies and scores each one against the ICP criteria, assigning Tier 1 / Tier 2 / Tier 3 or Disqualified. Outputs a scored CSV to `/output/`.

## Instructions

1. Ask the user: "Which CSV file in /data/ should I score?" (or accept `$ARGUMENTS` as the filename)
2. Read the ICP definition and scoring tiers from CLAUDE.md
3. Also read `/templates/scoring-criteria.md` if it exists for detailed scoring rules
4. **Before scoring: Apollo Taxonomy Check**
   - Apollo's industry tags are self-reported. The `industry` column in the CSV reflects what the company claims on LinkedIn — not what they actually do.
   - If the list was exported from Apollo using an industry filter, treat the `industry` column as unreliable.
   - Score primarily from the `company_description` or `about` field. If absent, use `company_name` and `website` to infer the actual business.
   - Flag any company where the description does not match the target industry as `Disqualified (false positive — industry tag mismatch)`.
5. For each company row in the CSV:
   - Evaluate each ICP dimension (industry, size, revenue, geography, signals)
   - Assign a tier: Tier 1, Tier 2, Tier 3, or Disqualified
   - Add a short `scoring_reason` column explaining why (1–2 sentences)
6. Save the scored output to `/output/scored_[original_filename]_[YYYY-MM-DD].csv`
7. Print a summary table:
   - Total companies processed
   - Count per tier
   - **False positive count** (companies that had the right Apollo tag but wrong actual business)
   - Top 5 Tier 1 companies with their reasons
8. If false positive rate exceeds 20%, warn: "High contamination rate detected — recommend refining Apollo search before further enrichment. See `/apollo-list` for keyword inclusion/exclusion guidance."
9. Ask: "Should I proceed to lead enrichment for Tier 1 and Tier 2 companies?"

## Apollo False Positive Patterns by Industry

These are the most common sources of contamination when building Apollo lists. Use this to calibrate scoring:

| Target Industry | Common False Positives | Detection Signal |
|----------------|----------------------|-----------------|
| Real Estate (ITA) | Facility management firms, energy suppliers, engineering/systems companies, PropTech SaaS | Description mentions "impianti", "energia", "software", "consulenza" without "compravendita" or "affitti" |
| Real Estate (ESP) | Same patterns + property valuation consultancies | Description mentions "valoración", "tasación" without "agencia" or "compraventa" |
| Beauty/Wellness | Cosmetics product manufacturers, beauty retail chains (no services), B2B beauty distributors | No mention of "trattamenti", "appuntamenti", "clienti"; mentions "distribuzione", "ingrosso" |
| Education | Corporate training firms (B2B), LMS software companies, staffing agencies | No mention of students, courses for individuals; mentions "aziende clienti", "formazione aziendale" only |
| Fashion/Apparel | Raw fabric suppliers, B2B clothing manufacturers, uniform companies | No D2C or retail mention; mentions "tessile industriale", "fornitura" |
| Travel/Hospitality | Travel tech SaaS, B2B booking platforms, airline software | No direct-to-consumer offering; mentions "API", "platform", "B2B solutions" |

### Scoring Rule for Ambiguous Cases

- If company description is **empty**: score conservatively — assign Tier 3 unless other signals (size, title, signals) are very strong.
- If company description **partially matches**: e.g., real estate company that also does facility management — check primary revenue source. Tier 2 if real estate is primary.
- If description is in a **different language than expected** (e.g., English description for Italian company): still evaluate content, do not downgrade for language.

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
