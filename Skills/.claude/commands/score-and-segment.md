# Score and Segment

Score a company list against the ICP and tier it — quickly by ICP fit alone, or fully by ICP fit + enrichment quality + buying signals.

## Modes

| Mode | When to use |
|------|-------------|
| `quick` | Fresh Apollo export — you want Tier 1/2/3 based on ICP fit only. Fast. |
| `full` | Enriched list from `/enrich-leads` — combine ICP fit with data completeness and buying signals to decide who gets personalized vs templated outreach. |

If not specified, ask: "Quick mode (ICP fit only) or full mode (ICP + enrichment + signals)?"

---

## Instructions

### Step 1 — Load inputs

Accept `$ARGUMENTS` as the CSV path and optional mode flag (e.g. `/score-and-segment companies.csv full`), or ask.

Load:
- ICP definition and scoring tiers from CLAUDE.md
- `/templates/scoring-criteria.md` if it exists
- [Full mode only] Hypothesis set from `/output/hypothesis_set_[vertical-slug].md` — ask which vertical if ambiguous

---

### Step 2 — Apollo Taxonomy Check (both modes)

Apollo's industry tags are self-reported. The `industry` column reflects what the company claims on LinkedIn — not what they actually do. If the list was exported from Apollo using an industry filter, treat the `industry` column as unreliable.

- Score primarily from `company_description` or `about` field. If absent, use `company_name` and `website` to infer the actual business.
- Flag any company where the description does not match the target industry as `Disqualified (false positive — industry tag mismatch)`.

**False positive patterns by industry:**

| Target Industry | Common False Positives | Detection Signal |
|----------------|----------------------|-----------------|
| Real Estate (ITA) | Facility management, energy suppliers, engineering/systems companies, PropTech SaaS | Description mentions "impianti", "energia", "software", "consulenza" without "compravendita" or "affitti" |
| Real Estate (ESP) | Same + property valuation consultancies | Mentions "valoración", "tasación" without "agencia" or "compraventa" |
| Beauty/Wellness | Cosmetics manufacturers, beauty retail chains (no services), B2B distributors | No "trattamenti", "appuntamenti", "clienti"; mentions "distribuzione", "ingrosso" |
| Education | Corporate training (B2B), LMS software, staffing agencies | No students/individual courses; mentions "aziende clienti", "formazione aziendale" only |
| Fashion/Apparel | Raw fabric suppliers, B2B clothing manufacturers, uniform companies | No D2C or retail; mentions "tessile industriale", "fornitura" |
| Travel/Hospitality | Travel tech SaaS, B2B booking platforms, airline software | No D2C offering; mentions "API", "platform", "B2B solutions" |

**Ambiguous case rules:**
- Empty description → Tier 3 unless other signals are very strong
- Partial match → check primary revenue source; Tier 2 if target industry is primary
- Description in wrong language → evaluate content, do not downgrade for language

---

### Step 3 — Score ICP fit (both modes)

For each company, evaluate: industry, size, revenue, geography, signals.

Assign: Tier 1 / Tier 2 / Tier 3 / Disqualified

Add `scoring_reason` (1–2 sentences). Refer to scoring tiers in CLAUDE.md.

---

### Step 4 — [Full mode only] Evaluate enrichment data quality

**Basic fields (don't count toward enrichment score):**
`company_name`, `website`, `industry`, `employee_count`, `location`, `email`, `firstName`, `lastName`

**Enrichment fields (count non-empty, non-"N/A"):**
- `technologies_used`, `crm_tool`, `whatsapp_tool` (buying signals)
- `recent_news`, `linkedin_posts`, `job_postings` (behavioural signals)
- `revenue_estimate`, `funding_stage` (size signals)
- `persona_role_match`, `decision_maker_reachable` (contact quality)

Assign enrichment score: `Rich` (3+ fields) / `Moderate` (1–2) / `Thin` (0)

---

### Step 5 — [Full mode only] Score hypothesis fit

Load the hypothesis set for the vertical. For each company, find the strongest hypothesis match:

- **Strong (4–5):** Description or enrichment directly matches the hypothesis mechanism
- **Medium (2–3):** Industry fits but no confirming signal
- **Weak (0–1):** Tangential or no data

Assign one `primary_hypothesis` per company — the strongest match. Flag for hold if no hypothesis scores above 2.

---

### Step 6 — [Full mode only] Apply two-dimensional tier grid

| | Strong hypothesis fit (4–5) | Medium fit (2–3) | Weak fit (0–1) |
|---|---|---|---|
| **Rich data (3+)** | **Tier 1** — Personalized | **Tier 2** — Templated | **Tier 3** — Hold |
| **Moderate data (1–2)** | **Tier 2** — Templated | **Tier 2** — Templated | **Tier 3** — Hold |
| **Thin data (0)** | **Tier 2** — Templated | **Tier 3** — Hold | **Disqualified** |

---

### Step 7 — [Full mode only] Buying signal override

Upgrade Tier 2 → Tier 1 if any of these signals are present:

| Signal | Column to check |
|--------|----------------|
| Currently using a competitor WhatsApp tool | `whatsapp_tool`, `technologies_used` |
| Running Meta/Google Ads without WA automation | `ad_channels`, `technologies_used` |
| Hiring customer service or marketing roles | `job_postings` |

Note the override reason in `tier_reason`. Buying signal overrides should be reviewed manually before push — confirm the signal is real, not a false positive.

---

### Step 8 — Output

**Quick mode** → save to `/output/scored_[filename]_[YYYY-MM-DD].csv`
**Full mode** → save to `/output/segmented_[filename]_[YYYY-MM-DD].csv`

**Columns (both modes):**
- `tier` (Tier 1 / Tier 2 / Tier 3 / Disqualified)
- `tier_score` (1–10 numeric)
- `scoring_reason` (brief explanation)

**Additional columns (full mode only):**
- `primary_hypothesis` (hypothesis short name — e.g. "#2 No-show pain")
- `enrichment_score` (count of non-empty enrichment fields)
- `hypothesis_fit` (Strong / Medium / Weak)
- `tier_reason` (1–2 sentences — why this tier, what data confirmed it)
- `buying_signal` (if override applied — what signal was detected)

---

### Step 9 — Print summary

```
SCORING SUMMARY — [Campaign] — [mode]
──────────────────────────────────────
Total processed:  X
  Tier 1:         X (X%)
  Tier 2:         X (X%)
  Tier 3:         X (X%)
  Disqualified:   X (X%)

False positives (industry tag mismatch): X
[Full mode] Buying signal overrides: X upgraded to Tier 1
[Full mode] Hypothesis distribution:
  #1 [Name]: X | #2 [Name]: X | ...

Top 5 Tier 1 companies: [list with scoring_reason]
```

If false positive rate > 20%: warn "High contamination rate detected — recommend refining Apollo search before enrichment. See `/apollo-list` for keyword inclusion/exclusion guidance."

---

### Step 10 — Handoff options

**Quick mode:**
"Should I proceed to lead enrichment for Tier 1 and Tier 2 companies?"

**Full mode:**
1. Run `/cold-email-writer` on Tier 1 + Tier 2 with the prompt template
2. Run `/email-response-simulation` on top 3 Tier 1 prospects before generating at scale
3. Re-enrich Tier 3 via `/enrich-leads` to fill data gaps

---

## Notes

- Quick mode: Tier 1 at 15–30% of list is typical. Over 40% means scoring is too loose.
- Full mode: Tier 1 should be 10–20% of list. Over 40% means hypothesis fit criteria are too loose.
- Full mode: never generate personalized emails for Tier 3 — blank enrichment fields produce hollow "Hi {{firstName}}, I noticed your company..." that destroys trust.
- The `primary_hypothesis` column drives which email variant gets used in `/cold-email-writer`.
- Save the summary to `/output/session_log.md`.

## Example Usage

```
/score-and-segment companies.csv
```
(will ask mode)

```
/score-and-segment companies.csv quick
```

```
/score-and-segment enriched_leads_beauty_italy.csv full
```
