# Apollo List

Create a named contact list in Apollo CRM from a people search, scored CSV, or custom criteria — and push all contacts into it with a single label.

## What this skill does

Searches Apollo's people database using ICP-aligned filters, pulls matching contacts, and saves them to a named list in Apollo CRM. The list is immediately available in Apollo under **Contacts → Lists**.

## Authentication

Read `APOLLO_API_KEY` from CLAUDE.md.

Base URL: `https://api.apollo.io/api/v1`
Auth header: `X-Api-Key: <APOLLO_API_KEY>`

**Required API key permissions (must be enabled in Apollo Settings → API):**
- `Contacts` — read + **write** (create contacts)
- Labels are auto-created by passing `label_names` on contact creation

> ⚠️ The `bulk_create` endpoint silently ignores `label_names`. Always use single `POST /api/v1/contacts` per contact for labels to apply correctly.

## Instructions

1. Accept `$ARGUMENTS` as the list name, or ask: "What should this list be called?"
2. Determine the search criteria — either:
   - From a `/output/*.csv` file (re-push existing contacts), or
   - From ICP filters: ask for industry, country, job titles, company size range
3. Read `APOLLO_API_KEY` from CLAUDE.md

**Step 1 — Search for people:**

```
POST https://api.apollo.io/api/v1/mixed_people/search
```

```json
{
  "page": 1,
  "per_page": 100,
  "person_titles": ["CEO", "Founder", "..."],
  "person_locations": ["Italy"],
  "organization_num_employees_ranges": ["10,500"],
  "q_organization_keyword_tags": ["real estate", "..."]
}
```

- Paginate through results (up to 5 pages = 500 contacts by default, or up to 10 pages for larger campaigns)
- Save all results locally to `/output/<list_name>.csv` before pushing to Apollo

**Step 2 — Save CSV with full contact data:**

Columns: `First Name`, `Last Name`, `Title`, `Seniority`, `Email`, `Email Status`, `LinkedIn URL`, `Company`, `Company Website`, `Company Domain`, `Country`, `City`, `State`, `Apollo Person ID`, `Apollo Account ID`, `Tier`

Tier scoring (from CLAUDE.md ICP):
- **Tier 1:** CEO, Founder, Amministratore Delegato, General Manager, Country Manager, Sales Director, Head of Sales, Responsabile Commerciale, Direttore Commerciale, Direttore Vendite
- **Tier 2:** All other matched titles

**Step 3 — Push contacts to Apollo CRM with label:**

For each contact, `POST /api/v1/contacts`:

```json
{
  "first_name": "...",
  "last_name": "...",
  "title": "...",
  "linkedin_url": "...",
  "organization_name": "...",
  "email_domain": "...",
  "city": "...",
  "country": "...",
  "label_names": ["<list_name>"]
}
```

- Push one contact at a time (do NOT use `bulk_create` — it ignores `label_names`)
- Rate: 4 requests/sec max (`time.sleep(0.25)` between calls)
- Log progress every 50 contacts
- Track `created` (has `label_ids` in response) vs `errors`

**Step 4 — Print summary:**

```
LIST: <list_name>
Total contacts pushed: N
Tier 1: N | Tier 2: N
Errors: N
CSV saved: /output/<list_name>.csv
```

**Step 5 — Update session log:**

Append to `/output/session_log.md`:
- List name, date, total contacts, Tier 1/2 split, search criteria used

## Example Usage

```
/apollo-list "ITA_Beauty_Outbound_04.03.26"
/apollo-list "ESP_RealEstate_Outbound_04.03.26"
/apollo-list    ← will ask for name and criteria
```

## Search Criteria by Campaign Type (from CLAUDE.md ICP)

**Italian Real Estate:**
- Titles: CEO, Founder, Amministratore Delegato, Sales Director, Head of Sales, Responsabile Commerciale, Direttore Commerciale, Direttore Vendite, General Manager, Country Manager
- Location: Italy | Size: 10–500
- Keywords: `real estate`, `agenzia immobiliare`, `immobiliare`

**Italian Beauty/Wellness:**
- Titles: CEO, Founder, Amministratore Delegato, General Manager, Marketing Director
- Location: Italy | Size: 10–500
- Keywords: `beauty`, `wellness`, `spa`, `salone`, `estetica`, `clinica estetica`

**Spain Real Estate:**
- Same titles + location: Spain
- Keywords: `inmobiliaria`, `real estate`, `agencia inmobiliaria`

Refer to CLAUDE.md ICP and Target Industries sections for other verticals.

## Notes

- Apollo search returns up to 100 results per page; use pagination for full coverage
- `email_status: unavailable` means the email exists but needs Apollo credits to unlock — use `/enrich-leads` afterwards
- The label (list) is auto-created in Apollo when the first contact is pushed with that `label_names` value
- If a contact already exists in Apollo CRM (matched by LinkedIn URL), Apollo will create a duplicate — deduplication must be done manually in the UI
- After list creation, run `/cold-email-writer` to generate copy, then `/push-to-lemlist` to launch the campaign
