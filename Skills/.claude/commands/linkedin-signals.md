# LinkedIn Signals

Surface warm ICP leads from LinkedIn using three signal types: post engagers, hiring intent, and topic discussions. Run one mode or combine all three — each feeds directly into enrichment and outreach.

## Modes

| Mode | Command | What it finds |
|------|---------|--------------|
| `engagers` | `/linkedin-signals engagers <post-url>` | People who liked/commented on a LinkedIn post — turn social engagement into warm pipeline |
| `hiring` | `/linkedin-signals hiring` | ICP companies actively hiring roles that signal WhatsApp automation pain |
| `topics` | `/linkedin-signals topics` | ICP-matched profiles posting about pain points where Spoki adds value |

If no mode is specified, ask which one to run.

---

## How the three modes fit together

```
topics    →  surfaces warm ICP posts + engagement hooks (who's talking NOW)
engagers  →  scrapes who reacted to specific posts (competitors' or influencers')
hiring    →  finds ICP companies about to feel the pain (leading indicator)
        ↓
    score-and-segment → enrich-leads → cold-email-writer → push-to-lemlist
```

Cross-reference: companies appearing in both `topics` and `hiring` output are top priority.

---

## Mode: engagers

Scrape people who liked or commented on a LinkedIn post, qualify them against your ICP, and create a warm outreach list. Replaces $300+/month scraping tools.

### Instructions

1. Ask: "What's the LinkedIn post URL?"
2. Ask: "Which engagement types? (likes / comments / both)"
3. Use Apify `apify/linkedin-post-reactions-scraper`:
   - Read `APIFY_API_TOKEN` from CLAUDE.md
   - `POST https://api.apify.com/v2/acts/apify~linkedin-post-reactions-scraper/runs?token=<TOKEN>`
   - Input: `{ "postUrl": "<url>", "reactionsType": "all" }`
   - Poll for completion, then fetch results dataset
4. For each engager, collect: `first_name`, `last_name`, `title`, `company`, `linkedin_url`
5. Score against ICP (industry, title, company size): `qualified` / `maybe` / `skip`
6. For `qualified` profiles, enrich email via Prospeo/Wiza
7. Save to `/output/engagers_[post-slug]_[YYYY-MM-DD].csv`
8. Print summary: total scraped, qualified/maybe/skip counts, emails found
9. Ask: "Should I generate warm outreach copy for the qualified leads?"
   - If yes: use cold email logic but open with a reference to the specific post they engaged with

### Output columns

`first_name`, `last_name`, `title`, `company`, `linkedin_url`, `engagement_type` (liked / commented / shared), `qualification_status`, `email`, `email_status`, `personalization_hook`

### Warm outreach tip

> "Hey [Name], saw you liked [Author]'s post on [Topic] — thought you'd appreciate what we're doing at Spoki..."

This is 10x warmer than cold outreach because they've already signalled interest in the topic.

### Notes

- Only scrape public posts or posts you have permission to scrape
- Comments contain richer data than likes — capture comment text as extra personalization context
- Run against competitor posts or industry influencer posts for market research
- Apify costs vary by run size — budget accordingly

---

## Mode: hiring

Detect ICP companies hiring roles that signal a WhatsApp automation pain — before they know they need Spoki. Companies hiring Customer Service agents, CRM Managers, or Marketing Coordinators are experiencing exactly the pain Spoki solves: growing communication volume they're trying to solve with headcount instead of automation.

### Buying signal logic

| Role Being Hired | What It Signals | Spoki Angle |
|-----------------|-----------------|-------------|
| Customer Service Rep / Agente Servizio Clienti | High inbound query volume — solving with headcount | "Automate 60–70% of those queries via WhatsApp before hiring" |
| CRM Manager / Specialist | Formalising CRM — about to evaluate tools | Best champion persona — they'll own the Spoki evaluation |
| Marketing Coordinator | Growing comms workload — email/social not converting | "WhatsApp has 98% open rate vs 10% email" |
| Customer Success Manager | Churn risk — trying to retain with human touch | "Scale retention flows via WhatsApp without adding headcount" |
| SDR / Inside Sales | Lead volume growing — response time becoming critical | "Automate lead qualification on WhatsApp before leads go cold" |
| Social Media Manager | Expanding digital comms — WhatsApp is missing | Entry point — escalate to marketing decision maker |
| Appointment Coordinator / Booking Manager | High-volume appointment management | "Automate 60% of no-shows with WhatsApp reminders" |

### Instructions

#### Step 1 — Confirm parameters

Ask (or use defaults):
- Geography: Italy, Spain, or both (default: both)
- Industries: all ICP verticals or specific vertical
- Roles: all signal groups or specific group
- Company size: 10–500 employees (default)

#### Step 2 — Search Apollo for hiring companies

Read `APOLLO_API_KEY` from CLAUDE.md.

Primary: `POST https://api.apollo.io/v1/mixed_companies/search`

Run one search per role group:

| Group | `job_posting_keywords` values | Signal label |
|-------|-------------------------------|--------------|
| CS Volume | "customer service", "agente clienti", "atención al cliente", "supporto clienti" | `cs_volume` |
| CRM Champion | "CRM manager", "CRM specialist", "gestione CRM", "responsabile CRM" | `crm_champion` |
| Marketing Comms | "marketing coordinator", "coordinatore marketing", "email marketing" | `marketing_comms` |
| Sales SDR | "SDR", "sales development", "inside sales", "lead generation specialist" | `sales_sdr` |
| Appointment | "booking coordinator", "appointment scheduler", "segreteria", "recepcionista" | `appointment` |

Fallback (if company search returns <5 results): switch to `POST https://api.apollo.io/v1/mixed_people/search` filtering by title — finds people already in the role at ICP-sized companies, same signal, different angle.

#### Step 3 — Score ICP fit

| Tier | Criteria |
|------|----------|
| **Tier 1** | Top 8 verticals + 10–200 employees + Italy/Spain + hiring `crm_champion` or `cs_volume` |
| **Tier 2** | Industry match + slightly outside size range, or hiring `marketing_comms` or `sales_sdr` |
| **Tier 3** | Industry is a stretch, or <10 or >500 employees |
| **Disqualified** | Pure B2B, SaaS, public sector, NGO |

Also assign `signal_strength`: `hot` (hiring CRM Manager or >2 CS roles simultaneously) / `warm` (1 CS or Marketing Coordinator) / `mild` (general marketing or sales role)

#### Step 4 — Find decision-maker contact

For each Tier 1/2 company, search Apollo `mixed_people/search` by domain + target titles (CEO, Founder, CMO, Marketing Director, CRM Manager, Ecommerce Manager, Direttore Marketing, Director de Marketing, Responsabile CRM, Head of Customer Experience).

Priority per CLAUDE.md: <50 employees → CEO/Founder directly; 50–500 → CRM Manager as champion + CC CMO.

#### Step 5 — Save output

`/output/hiring_signals_[YYYY-MM-DD].csv`

Columns: `company_name`, `website`, `industry`, `employee_count`, `location`, `tier`, `signal_group`, `signal_strength`, `job_posting_detected`, `contact_name`, `contact_title`, `contact_linkedin_url`, `email`, `email_status`, `outreach_angle`

#### Step 6 — Auto-generate outreach angles

**`crm_champion` (Italian):**
> "Stai cercando un CRM Manager — di solito vuol dire che la gestione clienti sta diventando un collo di bottiglia. Spoki automatizza il canale WhatsApp e si integra con il tuo CRM esistente. Ti faccio vedere in 15 min?"

**`cs_volume` (Spanish):**
> "Vi que estáis contratando para atención al cliente — señal de que el volumen crece. Antes de escalar el equipo, ¿tiene sentido automatizar el 60–70% de las consultas repetitivas por WhatsApp?"

**`appointment` (Italian):**
> "Cerchi qualcuno per gestire gli appuntamenti? I nostri clienti hanno ridotto i no-show del 60% automatizzando i reminder su WhatsApp. Posso mostrarti come."

**`marketing_comms` (Spanish):**
> "Buscáis un Marketing Coordinator — si parte del rol es gestionar comunicación con clientes, WhatsApp tiene 98% de apertura vs 10% del email. Vale la pena verlo."

#### Step 7 — Print summary + next steps

```
LinkedIn Hiring Signals — [date]
────────────────────────────────
Companies scanned:    [N]
Tier 1:               [N]  ← prioritise
Tier 2:               [N]
Tier 3/DQ:            [N]

Signal breakdown:
  Hot (CRM / multi-CS): [N]
  Warm (single CS):     [N]
  Mild (marketing):     [N]

Geography: Italy [N] | Spain [N]
```

Then ask:
1. "Should I enrich email addresses for Tier 1 contacts via `/enrich-leads`?"
2. "Should I write personalised cold emails using the hiring angle?"
3. "Should I push Tier 1 + Tier 2 to a Lemlist sequence tagged 'hiring-signal-[date]'?"

### Notes

- **Hottest signal:** Hiring CRM Manager = formalising the function = will evaluate tools. Get in before they decide.
- Apollo job posting data may lag 2–4 weeks — complement with manual LinkedIn Jobs search for priority targets
- Run weekly or bi-weekly — hiring signals are time-sensitive
- Cross-reference with `topics` mode: companies appearing in both lists are top priority

---

## Mode: topics

Scan LinkedIn weekly for posts by ICP-matched profiles discussing pain points where Spoki adds value. Instead of waiting for leads, this mode searches LinkedIn posts by keyword groups in Italian and Spanish, filters out noise, scores genuine buyer signals, and outputs a prioritised engagement list with ready-to-use hooks.

### Keyword groups

**GROUP A — Direct pain keywords**

| Italian | Spanish |
|---------|---------|
| "no show appuntamenti" | "clientes no aparecen" |
| "disdette appuntamenti" | "citas no confirmadas" |
| "abbandono carrello" | "abandono carrito" |
| "clienti non rispondono" | "clientes no responden" |
| "gestione clienti WhatsApp" | "clientes por WhatsApp" |
| "automazione WhatsApp" | "automatizar WhatsApp" |
| "email non funziona" | "el email no funciona" |
| "lead non convertono" | "leads no convierten" |

**GROUP B — Competitor mentions (warm — filter employees)**

`"Brevo"`, `"ManyChat"`, `"Trengo"`, `"Zendesk WhatsApp"`, `"Respond.io"`, `"Callbell"`, `"Leadsales"`, `"Sirena app"`, `"WATI"`, `"Charles platform"`

Skip posts where author works at that company (see noise filter step).

**GROUP C — Industry growth signals**

| Italian | Spanish |
|---------|---------|
| "apriamo nuovo studio" | "abrimos nueva clínica" |
| "nuovo salone aperto" | "nueva apertura salón" |
| "lanciamo e-commerce" | "lanzamos tienda online" |
| "implementiamo CRM" | "implementamos CRM" |
| "nuova sede aperta" | "nueva sede abierta" |

**GROUP D — WhatsApp Business general (high volume — filter harder)**

`"WhatsApp Business Italia"`, `"WhatsApp API aziende"`, `"WhatsApp API empresas"`, `"Meta Business Partner WhatsApp"`

**GROUP E — Industry-specific pain combos (HIGHEST SIGNAL — run first)**

| Vertical | Italian | Spanish |
|----------|---------|---------|
| Beauty/Wellness | "no show centro estetico" | "no show centro estético" |
| Beauty/Wellness | "disdette salone bellezza" | "cancelaciones salón belleza" |
| Beauty/Wellness | "appuntamenti centri estetici" | "citas spa cliente" |
| Real Estate | "lead immobiliare WhatsApp" | "lead inmobiliario WhatsApp" |
| Real Estate | "risposta lead portale" | "respuesta lead portal inmobiliario" |
| Fashion/Ecom | "carrello abbandonato moda" | "carrito abandonado moda" |
| Fashion/Ecom | "recupero carrello WhatsApp" | "recuperar carrito WhatsApp" |
| Travel | "prenotazioni hotel WhatsApp" | "reservas hotel WhatsApp" |
| Education | "iscrizioni corso WhatsApp" | "inscripción curso WhatsApp" |
| Education | "open day scuola reminder" | "jornada de puertas abiertas recordatorio" |
| Healthcare | "appuntamenti clinica WhatsApp" | "citas clínica WhatsApp" |
| Pet | "appuntamenti veterinario WhatsApp" | "citas veterinario WhatsApp" |
| Automotive | "lead concessionaria WhatsApp" | "lead concesionario WhatsApp" |

### Instructions

#### Step 1 — Confirm scan parameters

Ask (or use defaults): timeframe (last 7 days), language (both), keyword mode (all groups, Group E first).

#### Step 2 — Scrape via Apify

- Read `APIFY_API_TOKEN` from CLAUDE.md
- **Confirmed working actor:** `supreme_coder~linkedin-post` (3.5M runs, 99.8% success rate)
- Actor takes LinkedIn search URLs — not keyword parameters directly

Build search URLs:
```
https://www.linkedin.com/search/results/content/?keywords=ENCODED_KEYWORD&datePosted=past-week&sortBy=date
```

```python
import urllib.parse
base = "https://www.linkedin.com/search/results/content/?keywords={}&datePosted=past-week&sortBy=date"
url = base.format(urllib.parse.quote("no show centro estetico"))
```

Apify call:
```bash
POST https://api.apify.com/v2/acts/supreme_coder~linkedin-post/runs?token=APIFY_API_TOKEN
{ "urls": ["<url1>", "<url2>", ...], "maxResults": 15 }
```

Batching strategy:
1. Group E first — 16 keywords, maxResults 15 → ~240 posts
2. Group A — 20 keywords, maxResults 10 → ~200 posts
3. Group B — 10 keywords, maxResults 10 → ~100 posts (apply employee filter)
4. Groups C/D only if credits remain

Collect per post: `text`, `url`, `postedAtISO`, `authorName`, `authorHeadline`, `authorProfileUrl`, `numLikes`, `numComments`, `inputUrl` (reverse-map to keyword/group)

Deduplicate by `url` before scoring.

#### Step 3 — Noise filter

**Competitor employee exclusion (critical for Group B):** skip post if author headline contains competitor name + role indicator (e.g. "Account Executive at Brevo", "@ Zendesk", "Head of Sales at Trengo").

General rule: if `competitor_name.lower()` in `authorHeadline.lower()` alongside "account executive", "sales", "customer success", "head of", "manager at" → skip.

**Vendor/agency filter:** mark `low_fit` (don't skip — may have ICP clients) if headline contains: "consulente", "consultant", "freelance", "agenzia", "agency", "digital agency", "software house", "developer", "coach", "studente"

**ICP positive signals:**
- `strong`: ICP title + ICP industry both present in headline
- `possible`: either present
- `unknown`: neither detectable

ICP titles: CEO, Founder, Titolare, CMO, Marketing Director, Responsabile Marketing, CRM Manager, Ecommerce Manager, Head of Sales, Director Comercial, Gerente Marketing, General Manager, Store Manager

ICP industries: beauty, wellness, spa, salon, estetica, estético, real estate, immobil, moda, fashion, apparel, travel, viaggio, turismo, hotel, education, scuola, accademia, formazione, pet, animali, elettronica, electronics, arredamento, furniture, healthcare, dental, automotive, concessionaria, retail, ecommerce

#### Step 4 — Score relevance (1–10)

| Score | Criteria |
|-------|----------|
| 9–10 | Group E match + ICP author OR explicit competitor frustration (non-employee) |
| 7–8 | Group A pain + ICP author OR Group E with `possible` ICP fit |
| 5–6 | Group C growth signal + ICP industry OR Group A with `unknown` fit but clear pain |
| 3–4 | Industry match but pain is generic |
| 1–2 | Noise |

Boosters (+1 each, max 10): post in Italian/Spanish, `strong` ICP fit, ≥3 pain words from `[no-show, disdett, appuntament, abbandono, carrito, lead, clienti, automaz, reminder, WhatsApp]`, ≥5 likes or ≥2 comments

Engagement angle: `competitor_switch` / `pain_direct` / `growth_signal` / `industry_awareness`

#### Step 5 — Save output

`/output/linkedin_topic_monitor_[YYYY-MM-DD].csv`

Columns: `author_name`, `author_title`, `author_linkedin_url`, `post_url`, `post_date`, `post_text_snippet` (150 chars), `keyword_group`, `keyword_matched`, `lang`, `likes_count`, `comments_count`, `icp_fit`, `relevance_score`, `engagement_angle`, `suggested_hook`

#### Step 6 — Generate engagement hooks (relevance_score ≥ 7)

**`competitor_switch` (Italian):**
> "[Competitor] ha i suoi limiti — soprattutto [pain]. I nostri clienti che sono migrati hanno ridotto i tempi di risposta del 70%. Ti racconto come in 10 min?"

**`competitor_switch` (Spanish):**
> "¿Tienes problemas con [Competitor]? Muchos clientes nuestros migraron desde [Competitor] y redujeron los no-shows un 60%. Te cuento en 15 min."

**`pain_direct` — no-shows (Italian):**
> "I reminder automatici su WhatsApp eliminano il 60% dei no-show. Lo facciamo girare per centinaia di centri estetici — vuoi vedere il flow?"

**`pain_direct` — no-shows (Spanish):**
> "Los recordatorios automáticos por WhatsApp eliminan el 60% de los no-shows. Lo hacemos funcionar para cientos de clínicas en España."

**`pain_direct` — cart abandonment (Italian):**
> "I reminder su WhatsApp recuperano il 25–35% dei carrelli vs il 2–3% dell'email. Ti faccio vedere il flow in 15 min?"

**`pain_direct` — cart abandonment (Spanish):**
> "Los recordatorios de carrito por WhatsApp recuperan el 25–35% vs el 2% del email. ¿Te muestro el flow en 15 min?"

**`pain_direct` — lead response (Real Estate):**
> "I lead dal portale si freddano in minuti. Spoki risponde in automatico su WhatsApp prima che lo faccia il concorrente. Ti faccio vedere?"

**`growth_signal` (Italian):**
> "Congratulazioni per [milestone]! Quando si scala, la gestione messaggi WhatsApp diventa il collo di bottiglia. Vi faccio vedere come si automatizza prima che sia un problema."

**`growth_signal` (Spanish):**
> "¡Enhorabuena por [milestone]! Cuando crece el negocio, los mensajes de WhatsApp se vuelven imposibles de gestionar. ¿Hablamos?"

#### Step 7 — Print summary + next steps

```
LinkedIn Topic Monitor — [date]
────────────────────────────────────────────────
Posts scanned (unique):        [N]
Competitor employees filtered: [N]
Vendors/agencies noted:        [N]  ← low_fit
ICP strong fit:                [N]
ICP possible fit:              [N]
High relevance (7+):           [N]

Language: Italian [N] | Spanish [N]
Group breakdown: E [N] | A [N] | B [N] | C [N]
Angles: competitor_switch [N] | pain_direct [N] | growth_signal [N]

TOP OPPORTUNITIES (score 7+):
1. [score] [Author] — [title] — [angle]
   "[post snippet]"
   Hook: [suggested_hook]
   🔗 [post_url]
```

Then ask:
1. "Should I enrich the high-relevance authors with email via `/enrich-leads`?"
2. "Should I generate personalised cold email copy for these leads?"
3. "Should I save these as a warm prospect list for the next Lemlist sequence?"

### Notes

- **Group E is highest signal.** Industry-specific pain combos return real buyers, not vendors or competitors.
- **Group B always needs the employee filter** — LinkedIn campaigns by competitor AEs create lots of false positives.
- Italian/Spanish posts are 3–5x more actionable than English — prioritise them.
- Engage in comments before cold outreach when possible — converts at 3–5x higher rate than cold DM.
- Confirmed working actor: `supreme_coder~linkedin-post` — input requires `urls` array (not `keywords` field).
- Italian LinkedIn peaks: Mon–Thu 8–11am CET. Spanish: Mon–Wed 9am–12pm CET.
- Free Apify tier ($5/month) covers ~7 full scans/month at current volume.

---

## Example Usage

```
/linkedin-signals engagers https://www.linkedin.com/posts/example-post-id

/linkedin-signals hiring
/linkedin-signals hiring crm italy
/linkedin-signals hiring beauty spain

/linkedin-signals topics
/linkedin-signals topics beauty
/linkedin-signals topics competitors
/linkedin-signals topics spain
```
