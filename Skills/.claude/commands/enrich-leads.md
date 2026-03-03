# Enrich Leads

Find ideal contacts at target companies and enrich them with verified email addresses using Apollo and email enrichment APIs.

## What this skill does

Takes a scored company list (Tier 1/2) and finds the right decision-maker contacts at each company, then enriches with verified emails. Replaces the need for Clay or manual enrichment tools.

## Instructions

1. Accept `$ARGUMENTS` as the path to a scored CSV (e.g. `/output/scored_companies.csv`), or ask the user which file to use
2. Filter to only Tier 1 and Tier 2 companies (skip Tier 3 and Disqualified)
3. For each company, use the **Apollo API** to find contacts:
   - Read `APOLLO_API_KEY` from CLAUDE.md
   - Target job titles defined in the ICP section of CLAUDE.md
   - Limit to 1–3 contacts per company (best fit first)
   - **Primary endpoint:** `POST https://api.apollo.io/v1/mixed_people/search`
     ```json
     {
       "api_key": "<APOLLO_API_KEY>",
       "person_titles": ["VP Sales", "Head of Growth"],
       "organization_domains": ["company.com"],
       "organization_num_employees_ranges": ["11,200"],
       "page": 1,
       "per_page": 3
     }
     ```
   - **Fallback (if 0 results):** `POST https://api.apollo.io/v1/mixed_people/organization_top_people`
     ```json
     { "api_key": "<APOLLO_API_KEY>", "organization_domain": "company.com", "person_titles": ["VP Sales"] }
     ```
   - Use the job titles and company size ranges from the ICP section of CLAUDE.md
4. For each contact found, enrich email using **Prospeo API** or **Wiza API**:
   - Read `PROSPEO_API_KEY` or `WIZA_API_KEY` from CLAUDE.md
   - Only use verified emails (bounce risk < 5%)
   - If email not found, mark as `email_not_found` and skip
5. Save enriched leads to `/output/enriched_leads_[YYYY-MM-DD].csv`
6. Print summary:
   - Companies searched
   - Contacts found
   - Emails verified
   - Email not found (how many)
7. Ask: "Should I proceed to generate cold email copy for these leads?"

## Output Format

CSV with columns:
- `company_name`, `website`, `tier`, `industry`
- `first_name`, `last_name`, `title`, `linkedin_url`
- `email`, `email_status` (verified / not_found / risky)
- `apollo_contact_id`

## Example Usage

```
/enrich-leads /output/scored_companies.csv
```

## Notes

- Apollo free tier: 50 exports/month. Upgrade for scale.
- Always verify emails before uploading to any sequencer — bounces hurt domain health
- If `mixed_people/search` returns 0 results, fall back to `mixed_people/organization_top_people` with just the domain
- If still no results, try `organization_linkedin_url` instead of domain (some companies have non-obvious domains)
- Apollo returns emails directly on paid plans — on free tier, only LinkedIn URLs are returned, so Prospeo/Wiza enrichment becomes mandatory
