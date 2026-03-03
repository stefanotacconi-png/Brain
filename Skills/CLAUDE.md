# Outbound GTM Agent — Project Context

You are an outbound GTM automation agent. Your job is to help score leads, enrich contact data, write personalized cold emails, and push campaigns to outreach tools — all without leaving this terminal.

## Folder Structure

```
/Outbound Campaigns/   → campaign prompt files, copy frameworks, scoring criteria, lead CSV inputs
/ICP/                  → HubSpot won deals analysis, campaign analytics, scored company lists
/.claude/commands/     → reusable skills (slash commands)
```

## API Keys

Store your API keys here (never commit this file to a public repo):

```
APOLLO_API_KEY=
LEMLIST_API_KEY=
APIFY_API_TOKEN=
PROSPEO_API_KEY=
WIZA_API_KEY=
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_AD_ACCOUNT_ID=
GOOGLE_CHAT_WEBHOOK=https://chat.googleapis.com/v1/spaces/AAQAhq1kBCw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=Jf_WY5tsWYm9Z5qIM2o1Qs0jHURvuHdVw7lvGPCc7IM
```

## Team Notifications (Google Chat)

Use `google_chat.py` to notify the team about GTM activities:

```bash
# Lead scoring complete
python google_chat.py --type leads --count 45 --tier1 12 --tier2 18 --source scored_companies.csv

# Campaign launched
python google_chat.py --type campaign --name "ITA Real Estate" --contacts 45 --tool Lemlist

# Analysis output ready
python google_chat.py --type analysis --file "won_deals_analysis_2026-03-02.md" --notes "750+ deals reviewed"

# Custom update
python google_chat.py --type custom --message "Paused Spain campaign — low open rates, revising copy"

# Error alert
python google_chat.py --type error --message "Apollo API rate limit hit — switching to Prospeo"
```

## Working Conventions

- Always save intermediate outputs to `/output/` so work is never lost
- When a workflow succeeds, note it in a `session_log.md` file
- Ask for confirmation before pushing anything to external APIs
- If an API call fails, log the error and suggest alternatives
- Use only Tier 1 and Tier 2 leads for outreach unless told otherwise

---

# GTM Knowledge Base

## What We Sell

WhatsApp automation and AI-powered conversational workflows for customer-facing businesses. We help companies automate lead response, appointment reminders, customer support, upsell flows, and post-purchase communication via WhatsApp — reducing manual work, cutting no-show rates by 20–40%, and automating 50%+ of repetitive support queries.

**Positioning:** Spoki is the Customer Engagement Management (CEM) platform that turns WhatsApp into a powerful channel for marketing, sales, and customer support. Official Meta Business Partner.

**Tagline:** "The future is conversational on WhatsApp"

**Company:** NextAI Srl — founded 2021, HQ in Brindisi (Italy), second office in Barcelona. CEO: Giorgio Pagliara. CMO: Mattia Pace. Team: 60+.

**Scale:** 20,000+ customers · 60M+ messages sent · 4,000+ integrations · 23x documented ROI

---

## ICP Definition

**Company profile:**
- B2C or D2C businesses with a direct relationship to the end consumer
- 10–500 employees (SME to mid-market)
- Revenue: €1M–€50M
- Geography: Spain and Italy primary; broader Southern Europe secondary; rest of EU tertiary
- Exclude: pure B2B, pure SaaS, public sector, non-commercial organisations

---

## Target Industries (priority order — CRM-validated)

| # | Industry | Validation | Notes |
|---|----------|------------|-------|
| 1 | Beauty / Wellness (clinics, salons, aesthetic centres, spas) | ✓ Won deals | Top volume, fast close |
| 2 | Real Estate (agencies, developers, franchises) | ✓ Won deals | Fast close outbound — Tempocasa €21.6k |
| 3 | Fashion / Apparel (D2C, ecommerce, retail chains) | ✓ Won deals | Nuna Lie, Caleffi, Il Lenzuolo |
| 4 | Travel / Hospitality (hotels, travel agencies, tour operators) | ✓ Won deals | Gattinoni €18.6k, Forba Viaggi |
| 5 | Education (language schools, academies, e-learning, study abroad) | ✓ Won deals | Large deal sizes — MLA World, Pegaso |
| 6 | Pet retail / D2C | ✓ Won deals (surprise) | Fast close (Zampa: 6 days), ~€40k total 3 wins |
| 7 | Electronics / Consumer retail | ✓ Won deals | Expert Mallardo, Electrolux |
| 8 | Home / Furniture (interior design showrooms, D2C textiles) | ✓ Won deals | Caleffi, Il Lenzuolo |
| 9 | Healthcare (private clinics, diagnostic centres) | Hypothesis | Strong pain fit |
| 10 | Automotive (dealerships, service centres) | Hypothesis | |
| 11 | Finance / Insurance (brokers, insurers) | Hypothesis | |
| 12 | Events (organisers, venues) | Hypothesis | |
| 13 | Energy (solar, utilities) | Hypothesis | |
| 14 | Food / GDO (supermarkets, delivery) | Hypothesis | |
| 15 | Logistics / Distribution | Hypothesis | |

---

## Buyer Personas

### Decision Makers (sign the deal)

| Persona | Context | Notes |
|---------|---------|-------|
| CEO / Founder / Amministratore Delegato | Dominant at SMEs (<50 employees); also present at mid-market | Go direct at SMEs |
| CMO / Marketing & Communication Director | Key for B2C brands with comms budget | Strong at mid-market |
| General Manager / Country Manager | Multi-location or international businesses | Good entry for franchises |

### Internal Champions (find the product, push the deal)

| Persona | Context | Notes |
|---------|---------|-------|
| CRM Manager / CRM Specialist | Most frequent champion in won deals | Best champion at mid-market |
| Senior Ecommerce Manager / Digital Marketing Manager | D2C, fashion, home, sporting goods | |
| Social Media Manager | Entry point only — usually too junior to sign | Use to escalate to decision maker |

### Sales-Oriented Roles (Real Estate, Automotive, Finance)

| Persona | Context |
|---------|---------|
| Sales Director / Head of Sales / Responsabile Commerciale | Real Estate and Insurance |

### Persona Strategy

- **SME (<50 employees):** Go direct to CEO/Founder
- **Mid-market:** Target CRM Manager or Ecommerce Manager as champion + CC their CMO/Marketing Director

---

## Industry Pain → Solution Map

| Industry | Primary Pain | Our Solution Hook |
|----------|-------------|-------------------|
| Beauty | No-shows + slow ad lead response | "Reduce no-shows 20–40% + auto-respond to ad leads in seconds" |
| Healthcare | Saturated phone lines + patients forget prep | "Automate 50%+ of repetitive queries + pre-exam prep flows" |
| Real Estate | Portal leads go cold in minutes | "Instant WhatsApp reply to portal leads before competitors do" |
| Automotive | Slow follow-up on portal leads + manual service reminders | "Qualify leads instantly + automate service/ITV reminders" |
| Education | No-shows for open days + support overload at peaks | "Cut open day no-shows + automate FAQ during admissions" |
| Travel/Hospitality | Booking drop-offs + missed upsell at pre-arrival | "Recover bookings + automate spa/upgrade upsells before arrival" |
| Fashion | Cart abandonment + low email return | "Recover carts via WA 10–30% better than email" |
| Finance/Insurance | Policy renewal churn + KYC friction | "Automate renewal reminders + frictionless doc collection" |
| Events | Attendees ignore email reminders | "90%+ open rate on WA vs 20% on email for event reminders" |
| Home | Warm leads go cold between website and showroom | "Instant WA follow-up on Meta Ads leads → showroom booking" |
| Pet | High volume of customer queries + order updates | "Automate order status, appointment booking, and FAQs via WhatsApp" |
| Electronics | Post-purchase support overload | "Deflect 50%+ of support queries via WhatsApp self-service flows" |

---

## Buying Signals (high intent — prioritise these leads)

| Signal | Priority | Notes |
|--------|----------|-------|
| Currently using a WhatsApp tool (Charles, Zendesk WA, ManyChat, Twilio, Respond.io) | Top | Already has budget + proven need → pitch switching/consolidation. Always reference competitor in first email line. |
| Running Meta or Google Ads but no WhatsApp follow-up automation | High | Clear gap — easy ROI story |
| Hiring customer service agents or marketing coordinators | High | Pain is growing, budget exists |
| Using legacy tools (SMS, email newsletters) for customer communication | Medium | Education-first pitch |
| Recently opened new locations or expanding nationally | Medium | Scaling pain |
| Active on LinkedIn posting about customer experience challenges | Medium | Warm signal |
| No WhatsApp Business at all | Low | Education-first, longer cycle |

---

## Scoring Tiers

| Tier | Definition |
|------|------------|
| **Tier 1** | Perfect fit. Target industry + right size + Marketing or CS persona reachable. Prioritize immediately. |
| **Tier 2** | Strong fit. Industry match + slightly outside size range, or secondary persona. Worth targeting. |
| **Tier 3** | Weak fit. Industry is a stretch or company too small/large. Low priority. |
| **Disqualified** | B2B-only companies, pure SaaS, public sector, non-commercial organisations. |

---

## Competitive Landscape

**Total competitors tracked:** 83 globally (161 blog domains monitored for content gaps)

### Primary competitors by market

| Market | Top Competitors |
|--------|----------------|
| Italy | Brevo, Callbell, Growy, Charles, Trengo |
| Spain | Sirena.app, Leadsales, B2Chat, Clientify |
| Global | Twilio, Sinch, Infobip, 360dialog, WATI, Sleekflow, Respond.io, Bird, Gupshup, Interakt |

### Displacement targets (switch angle)

| Competitor | Their Weakness | Our Angle |
|-----------|----------------|-----------|
| Charles | Enterprise-focused, higher price | Simpler onboarding, better SME pricing |
| Zendesk WA | Complex ticketing overhead | Lighter, more automation-native |
| ManyChat | Limited WA features, mainly Meta | Full WA Business API, richer flows |
| Twilio | Dev-heavy, needs custom build | No-code/low-code, faster time to value |
| Respond.io | Broad multi-channel, less WA-native | WA-first depth, easier onboarding |
| Brevo | Email-first, WA is secondary | WA-native, 19 AI features built-in |
| Trengo | Multi-channel inbox, not WA-specialist | WA-first depth, unlimited operators included |

### Our key differentiators (use in copy)
- Official Meta Business Partner — zero ban risk (competitors on unofficial APIs risk account suspension)
- 19 AI features natively integrated (no extra cost)
- Unlimited operators + automations + integrations in all plans
- Dual platform: use WhatsApp App and API simultaneously
- Multichannel: WhatsApp + SMS + Voice AI + Email + RCS + Instagram + TikTok
- Free plan available (competitors often start paid)
- Documented 23x ROI

**Key displacement insight:** Companies already paying for a WhatsApp tool are the warmest outbound targets. They have budget, proven need, and are open to switching. Always reference the competitor by name in the first email line.

---

## CRM-Validated Learnings (from 750+ won deals — last reviewed 2026-03-02)

### Proven outbound channels
- **Lemlist → Spain** already producing wins (Albali Centros de Formación closed from a Lemlist sequence)
- **Meeting links** drive largest deals (Gattinoni €18.6k, Tempocasa €21.6k via calendar booking)
- **Paid Search (Google, brand + WhatsApp keywords in Italian)** drives fast inbound closes

### Time to close benchmarks

| Segment | Range |
|---------|-------|
| SME inbound (self-serve) | 0–3 days |
| SME inbound with demo | 6–36 days |
| Outbound SME | 6–30 days |
| Outbound / Inbound enterprise | 60–240 days |

### Spain market
- 10+ won deals. Real Estate (Tempocasa, Percent), Education (Albali, MLA World), Pet (Zampa), Beauty are working.
- Outbound + Lemlist confirmed.
- Use Spanish-language sequences for Spain accounts.

### Italy market
- Dominant market. Fashion/Apparel (Nuna Lie, Caleffi), Travel (Gattinoni), Education (Pegaso), Beauty/Wellness (EtnaWellness, Casillo Spa), Electronics (Expert Mallardo) all proven.

### Surprise wins
- **Pet industry:** 3 wins totalling ~€40k. Fast close (Zampa: 6 days). Pain: high volume of customer queries, appointment booking, order updates. Now priority 6 in ICP.

---

## Key Metrics & Social Proof (use in copy)

| Metric | Value | Notes |
|--------|-------|-------|
| WhatsApp open rate | 98% | vs 10% email — use "98% vs 10%" in copy (NOT 20%) |
| WhatsApp interaction rate | 20% | vs 1.5% email |
| ROI | 23x | €23 revenue per €1 invested (documented) |
| Customers | 20,000+ | |
| Messages sent | 60M+ | |
| Integrations | 4,000+ | |
| Cart recovery | 25–35% | via WhatsApp reminders |
| No-show reduction | 60% | Beauty/appointments |
| Support queries automated | 60–70% | |
| Re-engagement / winback | +35% reactivation | |
| Upsell revenue increase | +40% | automated upsell flows |
| Lead gen from ads | 60% conversion | Click-to-WA campaigns |

**Notable clients (use as social proof per vertical):**
Feltrinelli, UniPegaso (Education), Cofidis (Finance), Skon Cosmetics, Zuiki (Fashion), Reental (Real Estate), Doppelganger, Bauzaar, Macingo, Tuacar (Automotive)

---

## Pricing (for qualifying and displacement conversations)

| Plan | Price | Focus |
|------|-------|-------|
| Free | €0/mo | Customer request handling |
| Service | €349/mo | AI-powered customer support automation |
| Marketing | €599/mo | Marketing campaigns + revenue growth *(recommended)* |
| Sales | €749/mo | Sales and payments on WhatsApp |

All plans include: unlimited operators, unlimited automations, unlimited integrations, AI.
Discounts: -10% quarterly, -20% annual.

---

## Communication Angles (primary hooks — use in outreach)

| Angle | Hook |
|-------|------|
| Conversational future | "Emails have a 10% open rate. WhatsApp has 98%. The future is not an email." |
| CRM → CEM | "CRMs are built for data. Spoki is built for conversations." |
| AI agents 24/7 | "The smartest member of your team is ready to work. 24/7." |
| 23x ROI | "For every euro invested in Spoki, our customers generate €23 in revenue." |
| Meta Partner | "Spoki is an official Meta Tech Partner. Zero risk of bans." |
| Cart recovery | "Stop losing 70% of carts. Recover sales on WhatsApp." |

---

## Copy Principles

- Subject lines: under 8 words
- First line: hyper-personalized — reference their industry + specific pain (no-shows, slow lead response)
- Body: 3–5 sentences max
- CTA: one per email — always low-friction (15-min call, not a demo)
- No attachments in cold outreach
- Always tie pain to a concrete business cost (lost revenue, wasted staff time, no-show rate)
- Use industry-specific language: "no-show rate" for Beauty/Healthcare, "lead response time" for Automotive/Real Estate, "cart abandonment" for Fashion/Electronics
- Email open rate to use in copy: **10%** (not 20%) — "98% vs 10%"

---

## Open Hypotheses (unvalidated — update when confirmed or disproved)

| Hypothesis | Status | Notes |
|-----------|--------|-------|
| Healthcare (private clinics) is a strong vertical | Unvalidated | Pain fit is clear, no CRM wins yet |
| Automotive dealerships respond well to portal lead angle | Unvalidated | |
| Finance/Insurance has long cycles due to compliance | Unvalidated | |

---

## Website Repo (Spoki — Live Source)

Repo: `Spoki-App/spoki-website-nextjs` (branch: `develop`)

This is a live source of polished, market-tested product messaging. Pull from it when writing copy or validating pain points.

### Key paths for GTM work

| Path | Content |
|------|---------|
| `src/locales/industry-landing/it/` | Per-industry landing pages: hero, use cases, features, client success numbers (IT) |
| `src/locales/industry-landing/es/` | Same in Spanish — use for Spain outreach |
| `src/locales/buyer-personas/it/` | Per-persona pages: pain points, challenges, solutions, CTAs |
| `src/locales/use-cases/it/` | Use case pages by workflow |
| `src/locales/roi-calculator/it.json` | ROI stats and conversion benchmarks |

### Available industry landing pages
`automotive`, `beauty-spa-salon`, `clothing-apparel`, `education`, `entertainment-media`, `event-planning`, `finance-banking`, `food-grocery`, `hotel-lodging`, `marketing-agency`, `medical-health`, `nonprofit`, `professional-services`, `public-service`, `restaurant`, `shopping-retail`, `telco`, `tourism`, `travel-transportation`

### Available buyer persona pages
`ceo`, `crm-manager`, `ecommerce-manager`, `marketing-manager`, `marketing-specialist`, `head-of-sales`, `sdr`, `bdr`, `customer-support`, `social-media-manager`, `store-manager`, `operations-manager`, and more.

### Key numbers from the website (use in copy)
- No-show reduction: **60%** (Beauty — appointment reminders)
- Cart abandonment recovery: **25–35%** via WhatsApp vs email
- WhatsApp open rate: **98%** vs **10%** email
- Support queries automated: **60–70%**
- Conversion rate increase: **up to 40%**
- Customer lifetime value increase: **25–40%** (post-purchase flows)
- CAC reduction: **40%** (WhatsApp funnel)
- Client base claims: **600+ salons/spas**, **400+ educational institutions**

### Pain points per persona (website-validated)

| Persona | Primary Pain |
|---------|-------------|
| CRM Manager | Dirty data — email bounce, outdated contacts, incomplete profiles |
| Ecommerce Manager | 70% cart abandonment, low email recovery rate, no repeat purchase channel |
| Marketing Manager | Email lost in spam, 10% open rate, no personalisation at scale |
| CEO/Founder | No ROI visibility across channels, fragmented tools, high CAC |

---

## Changelog

| Date | Update | Source |
|------|--------|--------|
| 2026-03-03 | Knowledge base created — seeded from CLAUDE.md and 750+ won deal CRM analysis | Session init |
| 2026-03-03 | Added website repo as live source — indexed industry landing pages, buyer persona pages, ROI stats | `spoki-website-nextjs` repo scan |
| 2026-03-03 | Added company facts, full metrics table, pricing, competitor landscape (83 competitors), differentiators, communication angles, notable clients | `spoki-mk-mind-2/src/lib/config/spoki-brand-context.ts` |
| 2026-03-03 | Corrected email open rate: 10% (not 20%) — source is brand context file | `spoki-brand-context.ts` |
| 2026-03-03 | Merged knowledge-base.md skill into CLAUDE.md — single source of truth | Restructure |
