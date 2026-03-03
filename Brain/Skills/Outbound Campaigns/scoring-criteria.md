# ICP Scoring Criteria

Used by `/icp-score` to evaluate and tier companies. Based on the actual ICP: WhatsApp automation for B2C and D2C customer-facing businesses in Spain and Italy.

## How to Use

For each company, score it on the dimensions below. Sum up the points to get a total tier score.

| Score | Tier |
|-------|------|
| 8–10  | Tier 1 — Perfect fit |
| 5–7   | Tier 2 — Strong fit |
| 2–4   | Tier 3 — Weak fit |
| 0–1   | Disqualified |

---

## Scoring Dimensions

### 1. Industry Match (0–3 points)

**3 pts — Primary target industries (highest WhatsApp automation ROI — CRM-validated):**
- Beauty / Wellness (clinics, salons, aesthetic centres, spas) ✓ Won deals: EtnaWellness, Casillo Spa, Essenze Firenze
- Real Estate (agencies, developers, franchises) ✓ Won deals: Tempocasa (€21.6k), Percent (ES)
- Fashion / Apparel (D2C, ecommerce, retail chains) ✓ Won deals: Nuna Lie (€13.8k), Caleffi (€21.6k), Il Lenzuolo
- Travel / Hospitality (hotels, resorts, travel agencies) ✓ Won deals: Gattinoni (€18.6k), Forba Viaggi, inter-studioviaggi
- Education (language schools, academies, e-learning, study abroad) ✓ Won deals: MLA World (€51k), Pegaso (€12.5k), Astudy (€7.8k)

**2 pts — Strong fit industries (also CRM-validated):**
- Pet retail / D2C (SURPRISE: 3 wins — Zampa €21k, ILMA PET €14k, Cuori €4.5k) ✓ Fast close
- Home / Interior Design (furniture showrooms, D2C textiles) ✓ Won deals: Caleffi, Il Lenzuolo
- Electronics / Consumer retail (chains, multi-location stores) ✓ Won deals: Expert Mallardo, Electrolux
- Healthcare (private clinics, dental, diagnostic centres)
- Events (organisers, venues)
- Finance / Insurance (brokers, insurers)

**1 pt — Tertiary industries (viable, lower priority):**
- Energy / Solar
- Electronics retailers
- Food / GDO (supermarkets, food delivery)
- Logistics / Distribution

**0 pts — Wrong fit:**
- B2B-only companies (no consumer-facing touchpoint)
- Pure SaaS or tech companies
- Public sector, NGOs, government
- Companies with no WhatsApp Business presence and no ad spend

---

### 2. Business Model (0–2 points)

- 2 pts — B2C or D2C (direct relationship with end consumer)
- 1 pt — Mixed B2B/B2C (has a consumer segment)
- 0 pts — Pure B2B (no consumer-facing operations)

---

### 3. Company Size (0–2 points)

- 2 pts — Sweet spot: 20–200 employees (SME with enough volume to feel the pain)
- 1 pt — Adjacent: 10–19 employees (owner-run, still viable) or 201–500 (mid-market, longer cycle)
- 0 pts — Too small (<10) or enterprise (>500)

**Target size:** 10–500 employees, sweet spot 20–200

---

### 4. Geography (0–2 points)

- 2 pts — Spain or Italy (primary markets, sales team covers natively)
- 1 pt — Portugal, France, Greece, or broader Southern Europe
- 0 pts — Outside EU, Northern/Eastern Europe with no Southern EU presence

---

### 5. Buying Signals (0–2 points)

**2 pts — Competitor displacement (highest-intent signal — validated from CRM notes):**
- Currently using a WhatsApp tool: Charles, Zendesk WA, ManyChat, Respond.io, Twilio, Bird, WATI
  → They have budget, proven need, and open to switching. Highest close rate.

**1 pt — Activation signals (award if ANY of these apply):**
- Running Meta or Google Ads (visible via ad transparency tools)
- Hiring CS agents, marketing coordinators, or receptionist roles → pain is growing
- Currently using SMS/email for reminders → easy migration pitch
- Actively posting about customer experience challenges on LinkedIn
- Recently opened new locations or announced expansion
- No WhatsApp Business at all + runs ads = greenfield opportunity

Cap this dimension at 2 points.

---

## Disqualification Rules (Instant 0 score)

Automatically disqualify if ANY of these are true:
- Pure B2B business with no consumer-facing operations
- Public sector, government, NGO, or non-commercial entity
- Company is a direct competitor (WhatsApp automation vendor)
- Already a client
- Fewer than 10 employees (too small for automation ROI)
- No web/social presence at all (can't verify legitimacy)
- Located outside Spain, Italy, or Southern Europe (unless campaign is specifically EU-wide)

---

## Persona Scoring Notes

When scoring, also note the best target persona based on industry and company size:

| Segment | Primary Persona | Secondary Persona |
|---------|----------------|-------------------|
| Beauty / Healthcare (any size) | Head of Marketing / Owner | Head of CS / Operations |
| Real Estate / Automotive (20–200 emp) | Head of Marketing / CMO | Sales Director |
| Education / Travel (50–200 emp) | Digital Marketing Manager | Head of CS |
| Fashion / Electronics D2C | Head of Marketing / CMO | General Manager |
| Finance / Insurance (50–500 emp) | Sales Director / Head of Sales | Operations Director |
| Small businesses (<30 emp, any industry) | General Manager / Founder | — |

---

## Example Tier 1 Company

- Industry: Beauty clinic, 3 locations (3 pts)
- Business model: B2C (2 pts)
- Size: 45 employees (2 pts)
- Geography: Barcelona, Spain (2 pts)
- Signals: Running Meta Ads, posting about no-shows on Instagram (1 pt)
- **Total: 10/10 → Tier 1**
- **Best persona:** Head of Marketing or Clinic Manager

## Example Tier 2 Company

- Industry: Furniture showroom (Home) — secondary (2 pts)
- Business model: B2C (2 pts)
- Size: 12 employees (1 pt)
- Geography: Milan, Italy (2 pts)
- Signals: None visible (0 pts)
- **Total: 7/10 → Tier 2**

## Example Disqualified Company

- Industry: B2B logistics software (0 pts)
- Business model: Pure B2B (0 pts)
- → **Disqualified immediately**

---

## Notes for Claude

When scoring, add a `scoring_reason` column with a brief explanation like:
> "Tier 1: Beauty clinic in Barcelona, B2C, 45 employees, running Meta Ads — ideal fit. Target: Head of Marketing."

or

> "Disqualified: B2B SaaS company — no consumer-facing operations."
