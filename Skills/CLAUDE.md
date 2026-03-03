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

## What We Sell

WhatsApp automation and AI-powered conversational workflows for customer-facing businesses. We help companies automate lead response, appointment reminders, customer support, upsell flows, and post-purchase communication via WhatsApp — reducing manual work, cutting no-show rates by 20–40%, and automating 50%+ of repetitive support queries.

## ICP Definition

**Product:** WhatsApp Business automation (AI chatbots, drip flows, appointment reminders, lead qualification, post-purchase sequences)

**Target Industries (priority order — validated against HubSpot won deals 2026-03-02):**
1. Beauty / Wellness (clinics, salons, aesthetic centres, spas) ✓ CRM-validated
2. Real Estate (agencies, developers, franchises like Tempocasa) ✓ CRM-validated — fast close outbound
3. Fashion / Apparel (D2C, ecommerce, retail chains — Nuna Lie, Caleffi, Il Lenzuolo) ✓ CRM-validated
4. Travel / Hospitality (hotels, travel agencies, tour operators — Gattinoni, Forba Viaggi) ✓ CRM-validated
5. Education (language schools, academies, e-learning, study abroad — MLA World, Pegaso, Astudy) ✓ CRM-validated — large deal sizes
6. Pet retail / D2C (SURPRISE winner — Zampa, ILMA PET, Cuori a Quattro Zampe) ✓ CRM-validated — fast close
7. Electronics / Consumer retail (Expert Mallardo, Electrolux) ✓ CRM-validated
8. Home / Furniture (interior design showrooms, D2C textiles — Caleffi, Il Lenzuolo) ✓ CRM-validated
9. Healthcare (private clinics, diagnostic centres)
10. Automotive (dealerships, service centres)
11. Finance / Insurance (brokers, insurers)
12. Events (organisers, venues)
13. Energy (solar, utilities)
14. Food / GDO (supermarkets, delivery)
15. Logistics / Distribution

**Company Size:** 10–500 employees (SME to mid-market)
**Revenue Range:** €1M–€50M
**Geography:** Spain, Italy, and broader Southern Europe (primary); rest of EU (secondary)
**Business Model Focus:** B2C and D2C — companies with a direct relationship to the end consumer. Exclude pure B2B.

**Primary Personas to Target (validated against HubSpot won deals):**

Decision makers (sign the deal):
- CEO / Founder / Amministratore Delegato — dominant at SMEs, also present at mid-market
- CMO / Marketing & Communication Director — key for B2C brands with comms budget
- General Manager / Country Manager — multi-location or international businesses

Internal champions (find the product, push the deal):
- CRM Manager / CRM Specialist — most frequent champion role in won deals
- Senior Ecommerce Manager / Digital Marketing Manager — D2C, fashion, home, sporting goods
- Social Media Manager — can initiate but usually too junior to sign; use as entry point to escalate

Sales-oriented roles (Real Estate, Automotive, Finance):
- Sales Director / Head of Sales / Responsabile Commerciale — for Real Estate and Insurance

**Persona strategy:** For SME (<50 employees), go direct to CEO/Founder. For mid-market, target CRM Manager or Ecommerce Manager as champion + CC their CMO/Marketing Director.

**Buying Signals (high intent — validated from won deal notes):**
- **Currently using a WhatsApp tool** (Charles, Zendesk WA, ManyChat, Twilio, Respond.io) → top priority, already has budget + proven need, pitch switching/consolidation
- Running Meta or Google Ads but no WhatsApp follow-up automation
- Hiring customer service agents or marketing coordinators (pain is growing)
- Using legacy tools (SMS, email newsletters) for customer communication
- Recently opened new locations or expanding nationally
- Active on LinkedIn posting about customer experience challenges
- No WhatsApp Business at all → education-first pitch

## Scoring Tiers

- **Tier 1** — Perfect fit. Target industry + right size + Marketing or CS persona reachable. Prioritize immediately.
- **Tier 2** — Strong fit. Industry match + slightly outside size range, or secondary persona. Worth targeting.
- **Tier 3** — Weak fit. Industry is a stretch or company too small/large. Low priority.
- **Disqualified** — B2B-only companies, pure SaaS, public sector, non-commercial organisations.

## Copy Principles

- Keep subject lines under 8 words
- First line must be hyper-personalized — reference their industry + specific pain (e.g. no-shows, slow lead response)
- Body: 3–5 sentences max
- One clear CTA per email — always a low-friction ask (15-min call, not a demo)
- No attachments in cold outreach
- Always tie the pain to a concrete business cost (lost revenue, wasted staff time, no-show rate)
- Use industry-specific language — "no-show rate" for Beauty/Healthcare, "lead response time" for Automotive/Real Estate, "cart abandonment" for Fashion/Electronics

## Industry Pain → Solution Map

Use this to personalise copy per industry:

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

## CRM-Validated Learnings (from 750+ won deals — updated 2026-03-02)

### Proven outbound channels:
- **Lemlist → Spain** already producing wins (Albali Centros de Formación closed from a Lemlist sequence)
- **Meetings links** drive largest deals (Gattinoni €18.6k, Tempocasa €21.6k via calendar booking)
- **Paid Search (Google, brand + WhatsApp keywords in Italian)** drives fast inbound closes

### Time to close benchmarks:
- SME inbound (self-serve): 0–3 days
- SME inbound with demo: 6–36 days
- Outbound SME: 6–30 days
- Outbound / Inbound enterprise: 60–240 days

### Competitor displacement — highest-intent signal:
Companies already paying for a WhatsApp tool (Charles, Zendesk, Twilio, ManyChat) are the warmest outbound targets. They have budget, proven need, and are open to switching if you can demonstrate simpler onboarding or better price/features. Always reference the competitor in the first email line.

### Spain market:
10+ won deals across Spain. Real Estate (Tempocasa, Percent), Education (Albali, MLA World), Pet (Zampa), and Beauty are working. Outbound + Lemlist confirmed. Use Spanish-language sequences for Spain accounts.

### Italy market:
Dominant market. Fashion/Apparel (Nuna Lie, Caleffi), Travel (Gattinoni), Education (Pegaso), Beauty/Wellness (EtnaWellness, Casillo Spa), Electronics (Expert Mallardo) are all proven.

### Surprise: Pet industry
Pet retail (B2C/D2C) has produced 3 significant wins totalling ~€40k. Fast close (Zampa: 6 days). Not initially in ICP — now added as priority 6. Pain: high volume of customer queries, appointment booking, order updates.

## Working Conventions

- Always save intermediate outputs to `/output/` so work is never lost
- When a workflow succeeds, note it in a `session_log.md` file
- Ask for confirmation before pushing anything to external APIs
- If an API call fails, log the error and suggest alternatives
- Use only Tier 1 and Tier 2 leads for outreach unless told otherwise
