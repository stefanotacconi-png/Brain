# Copy Frameworks

Used by `/cold-email-writer` to generate cold email sequences. Tailored for WhatsApp automation outreach to B2C/D2C businesses in Spain and Italy. Update the "What's Working" table as campaigns run.

---

## Core Principles

1. **Industry-specific pain in line 1** — Never open generically. Name their industry's exact problem.
2. **Tie pain to money** — No-shows = lost revenue. Slow lead response = competitor steals the deal.
3. **WhatsApp is the hook** — Prospects use WhatsApp daily. The familiarity is the sell.
4. **One idea per email** — Don't stack value props.
5. **Under 80 words** — Cold emails. Under 50 for follow-ups.
6. **Low-friction CTA** — "Worth a 15-min call?" not "Book a demo."

---

## Industry Pain → Copy Angle Reference

| Industry | Pain Hook | WhatsApp Stat to Use | Best Framework |
|----------|-----------|----------------------|----------------|
| Beauty | No-shows, slow ad lead response | "Reduce no-shows up to 60%" | PAS |
| Healthcare | Saturated phones, patients forget prep | "Automate 60–70% of queries" | PAS |
| Real Estate | Portal leads go cold in minutes | "Reply before competitors do" | Insight-Lead |
| Automotive | Slow portal follow-up, manual reminders | "Qualify leads instantly" | Insight-Lead |
| Education | No-shows for open days, peak support overload | "Cut no-shows, automate FAQ" | PAS |
| Travel/Hospitality | Drop-offs, missed pre-arrival upsell | "Recover bookings, sell upgrades" | Social Proof |
| Fashion D2C | Cart abandonment, email fatigue | "WA recovers 10–30% better than email" | Insight-Lead |
| Finance/Insurance | Renewal churn, KYC friction | "Automate renewal + doc collection" | PAS |
| Events | Email reminders ignored | "98% open rate on WA vs 10% on email" | Insight-Lead |
| Home / Furniture | Warm Meta leads go cold | "Instant WA reply → showroom booking" | PAS |

---

## Framework 1: Problem-Agitate-Solution (PAS)

Best for: Beauty, Healthcare, Education, Finance, Home — pain is obvious and felt daily.

```
Subject: [Specific pain at their company type]?

Hi [First Name],

[One-line observation about the pain specific to their industry].

Most [job title]s at [industry type] we talk to lose [specific cost/consequence] because of [root problem].

We help [industry] businesses [solve it] via WhatsApp — [specific result in numbers].

Worth a 15-min call to see if it applies?

[Name]
```

**Beauty example:**
> Subject: No-shows eating into your booking revenue?
>
> Hi Laura,
>
> Running a clinic means a full calendar that never quite translates to full revenue — no-shows at €80–150 per slot add up fast.
>
> We help beauty clinics in Spain cut no-shows by up to 60% with automated WhatsApp reminders that patients actually respond to.
>
> Worth a 15-min call to see how it works?

**Healthcare example:**
> Subject: Still answering appointment calls manually?
>
> Hi Marco,
>
> Most private clinics we talk to have receptionists spending 3–4 hours a day on calls that could be automated.
>
> We help clinics automate 60–70% of appointment booking and reminder flows via WhatsApp — freeing your team for actual patient care.
>
> Worth 15 mins?

**Education example:**
> Subject: Open day no-shows killing your conversion rate?
>
> Hi Elena,
>
> Language schools spend weeks promoting open days — then 30–40% of registrants simply don't show.
>
> We help academies in Italy cut no-shows by sending personalised WhatsApp reminders and confirmations that get 90%+ open rates.
>
> Worth a quick call?

---

## Framework 2: Insight-Lead (The "Did you know")

Best for: Real Estate, Automotive, Fashion, Events — prospect may not know the specific benchmark yet.

```
Subject: [Surprising stat relevant to their role]

Hi [First Name],

[Counterintuitive insight about their industry + WhatsApp].

[Why this matters for companies like theirs + consequence of the status quo].

[One line on what you do].

Open to hearing how we did it with [similar company type]?

[Name]
```

**Real Estate example:**
> Subject: Portal leads respond in 5 min — or not at all
>
> Hi Carlos,
>
> Studies show 78% of buyers go with the agency that responds first. Most portals deliver leads at night or weekends when your team is offline.
>
> We connect Idealista/Fotocasa leads directly to WhatsApp — automated reply in under 60 seconds, 24/7.
>
> Open to hearing how Reental is using this?

**Fashion D2C example:**
> Subject: Cart recovery via WhatsApp — 3x better than email
>
> Hi Sofia,
>
> Email cart abandonment sequences average 5–8% recovery. WhatsApp recovers 25–35% — same message, different channel.
>
> We set this up for D2C brands in 48 hours, no dev work required.
>
> Worth a look?

**Automotive example:**
> Subject: How many portal leads go cold before Monday?
>
> Hi Javier,
>
> Most dealerships receive 40–60% of their online leads on evenings and weekends — when the sales team is offline.
>
> We automate the first WhatsApp reply and qualification so no lead goes cold, even at 10pm on a Sunday.
>
> Worth 15 mins to show you how it works?

---

## Framework 3: Social Proof (The Name Drop)

Best for: Travel, Hospitality, Finance — trust-driven purchase with longer sales cycle.

```
Subject: How [Similar Business] [Result]

Hi [First Name],

[Similar business type] came to us with [exact problem your prospect has].

In [timeframe], they [specific measurable result] using WhatsApp automation.

We did it by [one-line mechanism].

Worth exploring if something similar could work for [Prospect Company]?

[Name]
```

**Travel/Hospitality example:**
> Subject: How a resort in Valencia cut no-shows by 35%
>
> Hi Ana,
>
> A 4-star resort we work with was losing €15K/month in last-minute no-shows and no-replies to upsell offers.
>
> In 6 weeks, they cut no-shows by 35% and added €8K/month in pre-arrival upsell revenue via WhatsApp.
>
> Worth exploring if something similar could work for your property?

---

## Framework 4: Warm Trigger (LinkedIn Engager)

Best for: Leads from `/linkedin-engagers` who engaged with relevant content about customer experience, marketing, or WhatsApp.

```
Subject: Re: [Topic of the post they engaged with]

Hi [First Name],

Saw you [liked/commented on] [Author]'s post about [topic] — figured you'd find this relevant.

[One insight that connects their engagement to the problem you solve].

We're actually helping [industry type] businesses in Spain/Italy [achieve related outcome] via WhatsApp.

Happy to share a quick example — useful?

[Name]
```

---

## The Active Spoki Sequence Formula (Lemlist — Validated)

This is the exact 4-email structure running in all current campaigns (ITA_Travel, ITA_Fashion, ITA_Education, ES_Education, ES_Travel, ITA_Retail, ES_Fashion). **Use this as the canonical template for all new campaigns.**

### Sequence Overview

| Step | Day | Type | Purpose |
|------|-----|------|---------|
| Email 1 | 0 | Opening | Pain + solution intro, 10-min ask |
| [Branch] | 0 | LinkedIn check | Visit profile if `linkedinUrl` present → invite → message |
| Email 2 | 3 | Follow-up | Response speed = revenue angle (friction) |
| [Branch] | 3 | LinkedIn check | Visit → invite → message |
| Email 3 | 5 | Follow-up | "The killer metric" — comparison/reaction gap |
| [Branch] | 5 | LinkedIn check | Visit → invite → message |
| Email 4 | 4* | Breakup | Assume not a priority + value gift offer |
| [Branch] | 4* | LinkedIn | Final LinkedIn message |

*Day 4 after Email 3 = Day 9 absolute. Fashion campaigns run Email 1 on Day 2 instead of Day 0.

### LinkedIn Conditional Branch
Between each email step: if `linkedinUrl` is populated → send LinkedIn visit → LinkedIn invite → LinkedIn message (2-day delay). If not populated → skip to next email. This runs on all campaigns.

---

### Email 1 — Opening (Day 0)

**ITA template (actual Lemlist body):**
```
{{IT_[Industry]_Subject_Line}}

Ciao {{firstName}},

Stavo dando un'occhiata a {{companyName}} e {{Pain_Point_Normalized}}

{{Solution_Normalized}}

Avresti 10 minuti questa settimana per una call veloce?

[Sender name]

P.S. Se vuoi vedere Spoki in azione, ho lasciato qui un agente WhatsApp: [demo link]
```

**ES template:**
```
{{ES_[Industry]_Subject_Line}}

Hola {{firstName}},

Estaba echando un vistazo a {{companyName}} y {{Pain_Point_Normalized}}

{{Solution_Normalized}}

¿Tendrías 10 minutos esta semana para una llamada rápida?

[Sender name]

P.S. Si quieres ver Spoki en acción, te he dejado un agente de WhatsApp aquí: [demo link]
```

**Formula:** Personalised observation → industry pain → solution in one line → low-friction 10-min ask → WhatsApp demo P.S.

---

### Email 2 — Friction + Social Proof (Day 3)

**ITA template:**
```
Ciao {{firstName}},

la velocità di risposta è il fattore che incide di più sul fatturato per un'azienda come {{companyName}}.

{{Friction_Context_Personalized}}

{{Social_Proof}}

[Sender name]

P.S. [WhatsApp agent demo link]
```

**ES template:**
```
Hola {{firstName}},

la velocidad de respuesta es el factor que más impacta en la facturación de empresas como {{companyName}}.

{{Friction_Context_Personalized}}

{{Social_Proof}}

[Sender name]

P.S. [WhatsApp agent demo link]
```

**Formula:** Speed = revenue anchor → personalised friction context → social proof (named client result) → P.S. only (no links in body — validated learning: links in E2 kill reply rate from 2.0% to 0.2%).

---

### Email 3 — The Killer Metric (Day 5)

**ITA template:**
```
Ciao {{firstName}},

il principale "killer" dei ricavi per {{companyName}} è il "comparison gap" (o "reaction gap").

{{[Industry]_Outcome_Metric_}}

Spoki ti assicura che [specific promise for industry].

[CTA — short, 1 line]

[Sender name]

P.S. [WhatsApp agent demo link]
```

**ES template:**
```
Hola {{firstName}},

el principal "killer" de los ingresos para {{companyName}} es el "comparison gap" (o "reaction gap").

{{[Industry]_Outcome_Metric}}

Spoki te garantiza que [specific promise for industry].

[CTA — short, 1 line]

[Sender name]

P.S. [WhatsApp agent demo link]
```

**Formula:** Name the "comparison gap" / "reaction gap" concept → industry-specific outcome metric → Spoki guarantee → P.S.

---

### Email 4 — Breakup + Value Gift (Day 4 after Email 3)

**ITA template:**
```
Ciao {{firstName}},

Immagino che [specific use case for their industry] non sia una priorità per {{companyName}} in questo momento.

{{Value_Gift_Teaser}}

Se mai tornasse una priorità, sarò qui.

[Sender name]

P.S. [WhatsApp agent demo link]
```

**ES template:**
```
Hola {{firstName}},

Imagino que [specific use case for their industry] no es una prioridad para {{companyName}} en este momento.

{{Value_Gift_Teaser}}

Si alguna vez vuelve a ser una prioridad, estaré aquí.

[Sender name]

P.S. [WhatsApp agent demo link]
```

**Formula:** Graceful assumption of no priority → value gift teaser (guide / template / benchmark doc) → soft door-open → P.S.

---

### Variable Naming Convention (Lemlist columns)

When uploading a lead list to Lemlist, populate these columns per lead:

| Variable | Description | Example |
|----------|-------------|---------|
| `IT_[Industry]_Subject_Line` | Italian subject line personalised to company | "Ciao Ana, i tuoi lead da Idealista rispondono?" |
| `ES_[Industry]_Subject_Line` | Spanish subject line | "Hola Carlos, ¿tus leads de Idealista responden?" |
| `Pain_Point_Normalized` | Industry pain in 1–2 sentences, personalised | "le tue prenotazioni online non si convertono quanto vorresti" |
| `Solution_Normalized` | One-line solution pitch | "aiutiamo le agenzie a rispondere ai lead entro 60 secondi via WhatsApp" |
| `Friction_Context_Personalized` | Why they specifically feel this pain | "Con X sedi, ogni minuto di ritardo significa lead catturati dai competitor" |
| `Social_Proof` | Named client result from same industry — **generic column, no industry prefix** | RE franchising: "Tempocasa (50+ sedi) ha ridotto il tempo di risposta da 4h a 2 minuti" / RE commerciale: "Reental ha automatizzato il primo contatto WhatsApp entro 60 secondi" |
| `[Industry]_Outcome_Metric_` | The killer stat for their industry | "le agenzie che rispondono entro 5 minuti chiudono il 78% delle trattative in più" |
| `Value_Gift_Teaser` | What you're offering as the gift | "Ti lascio la nostra guida su come Tempocasa ha impostato il flusso" |
| `cleanJobTitleIT` / `cleanJobTitleES` | Cleaned job title in language | "Direttore Marketing" / "Director de Marketing" |
| `linkedinUrl` | LinkedIn profile URL (enables branch) | https://linkedin.com/in/... |

---

### Running Campaigns Reference

| Campaign ID | Market | Industry | Status | Notes |
|-------------|--------|----------|--------|-------|
| ITA_Travel | Italy | Travel/Tourism | Running | Gattinoni €18.6k proof of concept |
| ITA_Fashion | Italy | Fashion/Apparel | Running | Nuna Lie €13.8k via outbound |
| ITA_Education | Italy | Education | Running | Università Pegaso, MLA World comps |
| ITA_Retail | Italy | Electronics/Retail | Running | Expert Mallardo via Paid Search |
| ES_Education | Spain | Education | Running | Albali €3.2k via Lemlist confirmed |
| ES_Travel | Spain | Travel/Tourism | Running | — |
| ES_Fashion | Spain | Fashion/Apparel | Running | — |
| ES_Cold_Calls | Spain | Multi | Running | Phone cadence parallel |
| IT_Cold_Calls | Italy | Multi | Running | Phone cadence parallel |
| ITA_RealEstate | Italy | Real Estate | **In setup** | cam_XGHFWnDWroM6Reip9 — AI columns v3.0 pending rebuild in Lemlist UI; 2 test contacts added (Christian Biondo, Francesco Munizzi) |

**Gaps to fill (high ICP, no active campaign):** ITA_Beauty, ES_Beauty, ES_RealEstate, ITA_Pet, ES_Pet

---

## Follow-Up Templates (Legacy — use Sequence Formula above for Lemlist)

### Step 2 (Day 3) — New angle, not a "bump"

```
Hi [First Name],

Wanted to add one more thing: [specific stat or mini case study not mentioned in Step 1].

[One sentence reinforcing why it's relevant for [their industry]].

Still worth 15 mins?

[Name]
```

**Beauty follow-up example:**
> Hi Laura,
>
> One thing I didn't mention: beyond reducing no-shows, our clients also see a 15–20% uplift in rebooking rates — WhatsApp reminders naturally prompt patients to book their next slot.
>
> Still worth 15 mins?

### Step 3 (Day 7) — Short pattern interrupt

```
Hi [First Name],

Last one from me — don't want to clutter your inbox.

If automating [specific pain for their industry] via WhatsApp isn't a priority right now, completely understood.

But if it ever is — I'm [Name], just reply here.

[Name]
```

---

## Subject Line Formulas (Under 8 words)

| Formula | Beauty | Real Estate | Fashion |
|---------|--------|-------------|---------|
| Question | "No-shows costing you this month?" | "Portal leads going cold overnight?" | "Cart abandonment eating your margins?" |
| Stat | "Clinics cut no-shows 40% — here's how" | "78% of buyers go with first reply" | "WA recovers carts 3x better than email" |
| Name drop | "How Clinica X cut no-shows in 6 weeks" | "How Agencia Y books 20% more visits" | "How Brand Z recovered €30K in carts" |
| Direct | "Quick question about [Company]'s reminders" | "Quick question about [Company]'s lead flow" | "Quick thought on [Company]'s WhatsApp" |
| Lowercase (pattern break) | "quick idea for your clinic, Laura" | "quick question for [Company], Carlos" | "something for [Company]'s cart flow" |

---

## What's Working (Update After Each Campaign)

Track winning patterns here after running `/campaign-analytics`:

| Campaign | Industry | Winning Framework | Reply Rate | Notes |
|----------|----------|------------------|------------|-------|
| ES_Education ✅ | Education/ES | 4-email sequence | **2.1%** | Best campaign. E1 at 2.2%. E2 plain text (no links) = 2.0% vs 0.2% with links. |
| ITA_Education | Education/IT | 4-email sequence | 1.6% | E4 breakup = 3.6% — highest single-step rate of all campaigns |
| ES_Travel | Travel/ES | 4-email sequence | 1.4% | E3 spikes to 2.2% — investigate and replicate that angle |
| ITA_Travel | Travel/IT | 4-email sequence | 1.0% | Solid but needs refresh after 2+ months |
| ITA_Fashion | Fashion/IT | 4-email sequence | 0.8% | Copy-offer mismatch — needs new D2C/cart abandonment angle |
| ITA_Retail ⚠️ | Retail/IT | 4-email sequence | 0.6% | 10% bounce rate — PAUSE, re-verify list before any new sends |
| ES_Fashion | Fashion/ES | 4-email sequence | 0.3% | Underperforming — same copy fix needed as ITA_Fashion |
| EN_Fashion_UK | Fashion/UK | 4-email sequence | 0.2% | Opens good (39%), replies near zero — wrong copy/offer for UK market |
| EN_Fashion_NL 🚨 | Fashion/NL | 4-email sequence | **0.0%** | 51.8% open rate, ZERO replies — complete copy-offer mismatch |

---

## Validated Learnings (from analytics 2026-03-02)

### Links in follow-up emails kill replies
ES_Education E2 A/B test: plain text (no link) = 2.0% reply, with link = 0.2%.
**Rule: E2, E3, E4 should be plain text. No links. Save links for E1 P.S. only.**

### Breakup email (E4) is the hidden best performer
ITA_Education E4 = 3.6% reply rate — higher than E1 (1.5%).
Treat E4 as a priority email, not an afterthought. The graceful assumption of no priority + value gift is the highest-converting pattern.

### Fashion campaigns need a different angle
All 4 fashion campaigns (ITA, ES, UK, NL) underperform. Open rates are fine (26–51%).
The pitch isn't landing. Test: lead with cart abandonment stat ("WhatsApp recovers 25–35% of carts vs 5% email") instead of generic WhatsApp automation.

### EN_Fashion_NL: 51.8% open / 0% reply — subjects are great, body is broken
The NL audience opens but doesn't respond at all. Try: shorter body (2 sentences), direct question in Dutch, or completely different pain hook.

### ES_Education is the template to clone
2.1% reply rate across all 4 steps with consistency. When launching new ES campaigns, use the ES_Education structure and tone as the starting point.

## What to Avoid

- "I hope this email finds you well" — delete immediately
- "I wanted to reach out because..." — weak opener
- Asking for a call in the first sentence before establishing pain
- Mentioning your company name before establishing relevance
- Long paragraphs (>3 lines)
- Attachments in cold emails
- "Just following up" as the entire follow-up email
- Generic WhatsApp claims — always tie to their specific industry's pain
- Mentioning "chatbot" — use "automated WhatsApp flows" or "WhatsApp automation"
