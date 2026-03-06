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

## ⚠️ Apollo Taxonomy Trap (read before building any list)

Apollo's industry tags are **self-reported** by companies on LinkedIn and are often inaccurate or overly broad. A search filtered to "Real Estate" will routinely return:
- Energy suppliers and utilities that own property
- Facility management and engineering firms serving the RE sector
- PropTech/SaaS companies selling software to real estate agencies
- Consulting firms with a real estate practice

**The tag tells you what the company claims — not what they actually do.**

### Mandatory Spot-Check Before Proceeding

After exporting any list from Apollo, **before enrichment or Lemlist push**, spot-check 10 random company descriptions:

1. Pull 10 random rows from the export CSV
2. Read their `company description` or `LinkedIn about` section
3. Ask: "Does this company actively buy/sell/rent/manage property for end customers?"
4. If **>2 out of 10** are off-target → stop. Refine the Apollo search using the keyword inclusions and exclusions below before proceeding.
5. If ≤2 off-target → acceptable contamination. Log the false positive count in session_log.md and proceed.

---

## Search Criteria by Campaign Type (from CLAUDE.md ICP)

### Italian Real Estate — ITA_RealEstate

**Titles to include:**
CEO, Founder, Amministratore Delegato, Sales Director, Head of Sales, Responsabile Commerciale, Direttore Commerciale, Direttore Vendite, General Manager, Country Manager, Titolare, Responsabile Vendite

**Titles to exclude (common false positives):**
- Project Manager, Facility Manager, Energy Manager, Ingegnere, Tecnico
- Software Engineer, CTO, Product Manager (PropTech filter)
- Consulente (generic consultants rarely qualify)

**Location:** Italy | **Size:** 10–500

**Keyword inclusions** (use in `q_organization_keyword_tags` — these confirm genuine RE activity):
- `agenzia immobiliare` (agency — strongest signal)
- `compravendita` (buy/sell transactions — genuine agency)
- `affitti` (rentals — property management angle)
- `nuova costruzione` (new build developer)
- `gestione immobiliare` (property management)
- `Immobiliare.it` or `Casa.it` (portal integrations — strong signal of active agency)
- `franchising immobiliare` (franchise networks — Tecnocasa, Gabetti, RE/MAX)
- `real estate agency`, `real estate` (for English-language profiles)

**Keyword exclusions** (add to filter OUT false positives):
- `facility management` → FM firms, not RE agencies
- `progettazione impianti` → engineering/systems design
- `fornitura energia` / `energia rinnovabile` → energy suppliers
- `software` / `SaaS` / `PropTech` → tech companies serving RE, not agencies
- `consulenza manageriale` → management consulting
- `costruzioni` alone (without `nuova costruzione` pair) → construction, not agency

**Apollo search template:**
```json
{
  "page": 1,
  "per_page": 100,
  "person_titles": ["CEO", "Founder", "Amministratore Delegato", "Responsabile Commerciale", "Direttore Vendite", "Head of Sales", "General Manager"],
  "person_locations": ["Italy"],
  "organization_num_employees_ranges": ["10,500"],
  "q_organization_keyword_tags": ["agenzia immobiliare", "compravendita", "affitti", "nuova costruzione"],
  "not_q_organization_keyword_tags": ["facility management", "software immobiliare", "SaaS", "fornitura energia"]
}
```

> Run spot-check before proceeding. Target: <20% contamination rate.

---

### Italian Beauty/Wellness

**Titles:** CEO, Founder, Amministratore Delegato, General Manager, Marketing Director, Titolare
**Location:** Italy | **Size:** 10–500
**Keywords:** `beauty`, `wellness`, `spa`, `salone`, `estetica`, `clinica estetica`, `centro benessere`, `laser`, `medicina estetica`
**Exclusions:** `cosmetica` (product manufacturers, not service providers), `e-commerce beauty` (unless also B2C service)

---

### Spain Real Estate

**Titles:** CEO, Founder, Director General, Director Comercial, Head of Sales, Responsable Comercial, Gerente
**Location:** Spain | **Size:** 10–500
**Keywords:** `inmobiliaria`, `agencia inmobiliaria`, `compraventa`, `alquileres`, `gestión de propiedades`, `real estate`
**Exclusions:** `facility management`, `energía`, `software inmobiliario`, `consultoría`

---

### Spain Beauty/Wellness

**Titles:** CEO, Founder, Director General, Gerente, Director de Marketing
**Location:** Spain | **Size:** 10–500
**Keywords:** `belleza`, `wellness`, `spa`, `salón`, `estética`, `clínica estética`, `centro de belleza`

---

Refer to CLAUDE.md ICP and Target Industries sections for other verticals. Always apply the Taxonomy Trap logic when building any new vertical.

## Notes

- Apollo search returns up to 100 results per page; use pagination for full coverage
- `email_status: unavailable` means the email exists but needs Apollo credits to unlock — use `/enrich-leads` afterwards
- The label (list) is auto-created in Apollo when the first contact is pushed with that `label_names` value
- If a contact already exists in Apollo CRM (matched by LinkedIn URL), Apollo will create a duplicate — deduplication must be done manually in the UI
- After list creation, **run spot-check**, then `/enrich-leads`, then `/cold-email-writer`, then `/push-to-lemlist`
- Log contamination rate and spot-check result in `/output/session_log.md` for every list built
