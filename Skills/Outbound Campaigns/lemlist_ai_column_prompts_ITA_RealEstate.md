# Lemlist AI Column Prompts — ITA_RealEstate
**Version:** 2.0 — Rebuilt using PDF framework architecture + Apollo field mapping
**Updated:** 2026-03-03
**Campaign:** ITA_RealEstate (cam_XGHFWnDWroM6Reip9)
**Columns:** 8 total (ITA_Retail framework parity)

Create each column in Lemlist → Campaign → Leads → "Create AI Columns" → "Create from scratch".
Model and temperature are specified per column.

---

## Execution order (columns must be created in this order — each feeds the next)

| # | Column name | Model | Temp | Feeds into |
|---|-------------|-------|------|-----------|
| 1 | `cleanJobTitle` | GPT-4o | 0.3 | all copy columns |
| 2 | `IT_RealEstate_Industry` | GPT-4o | 0.3 | Pain, Solution, Friction, Social Proof, Metric |
| 3 | `RealEstate_Pain_Point_Normalized` | Haiku 4.5 | 0.5 | E1 body |
| 4 | `Friction_Context_Personalized` | Haiku 4.5 | 0.5 | E2 body |
| 5 | `RealEstate_Social_Proof` | GPT-4o | 0.3 | E2 body |
| 6 | `IT_RealEstate_Solution_Normalized` | Haiku 4.5 | 0.5 | E1 body |
| 7 | `RealEstate__Outcome_Metric_` | Haiku 4.5 | 0.5 | E3 body |
| 8 | `IT_RealEstate_Subject_Line` | Haiku 4.5 | 0.5 | E1 subject |

---

## Column 1: `cleanJobTitle`
**Model:** GPT-4o | **Temperature:** 0.3
**Purpose:** Normalised, natural-sounding job title for personalisation across all emails.

```
You are processing a job title for use in a professional cold email. Your task is to clean and normalise the job title provided.

Input job title: {{jobTitle}}
Input language (if known): Italian or English

Rules:
1. PRESERVE the original language — never translate Italian to English or vice versa
2. KEEP seniority if meaningful: C-level, VP, Director, Head of, Principal, Lead → keep as-is
3. REMOVE: corporate suffixes (S.r.l., S.p.A., Ltd, Inc.), redundant words ("presso", "at", "di"), email addresses, URLs, numbers
4. SHORTEN overly long titles to the core role (max 4–5 words)
5. CAPITALISE correctly: Title Case for English, sentence case for Italian
6. If the input is empty, clearly not a job title (e.g. a company name, email, or gibberish), return exactly: Responsabile

Examples:
- "Digital Marketing Manager presso Agenzia Roma S.r.l." → "Digital Marketing Manager"
- "CEO & Founder" → "CEO & Founder"
- "responsabile vendite immobiliari" → "Responsabile vendite immobiliari"
- "john.smith@company.com" → "Responsabile"
- "" → "Responsabile"

Return ONLY the cleaned job title. No explanation, no punctuation at the end.
```

---

## Column 2: `IT_RealEstate_Industry`
**Model:** GPT-4o | **Temperature:** 0.3
**Purpose:** Extracts what the agency concretely does in max 8 words — used in "Ho visto che vi occupate di ___" opener.

```
You are processing company data to extract what a real estate company concretely does.

Company name: {{companyName}}
Company description: {{companyDescriptionFromApollo}}
Keywords: {{keywordsFromApollo}}
Website: {{website}}

STEP 1 — Identify which agency subcategory best fits:
A. Agenzia immobiliare residenziale (residential sales/rentals)
B. Agenzia immobiliare commerciale (commercial properties)
C. Franchising immobiliare / rete di agenzie (franchise network, multi-location)
D. Costruttore / developer immobiliare (property developer, new builds)
E. Gestione affitti / property management (rental management, property management)
F. Agenzia immobiliare generalista (generic, mixed)

STEP 2 — Write a short completion for "Ho visto che vi occupate di ___"

Rules:
- Max 8 words
- Concrete and specific (e.g. "compravendita residenziale nella zona di Milano" not "immobiliare")
- Italian only
- No "agenzia", no "immobiliare" as standalone — be more specific
- If description is empty or unclear, default to "compravendita e affitti immobiliari"

Return ONLY the completion phrase (the part after "vi occupate di"). No explanation.
```

---

## Column 3: `RealEstate_Pain_Point_Normalized`
**Model:** Haiku 4.5 | **Temperature:** 0.5
**Purpose:** 1–2 sentence pain point for Email 1 body — Insight-Lead framework opener.

```
You are a cold email copywriter for Spoki, a WhatsApp automation platform for real estate agencies in Italy.

Lead context:
- Company: {{companyName}}
- Job title: {{cleanJobTitle}}
- Agency type: {{IT_RealEstate_Industry}}
- Company description: {{companyDescriptionFromApollo}}
- Technologies used: {{technologiesFromApollo}}

STEP 1 — Identify which pain profile best fits this agency:

A. COMPETITOR TOOL USER — if {{technologiesFromApollo}} mentions Charles, ManyChat, Zendesk, Twilio, or Respond.io
   Pre-written options (pick one):
   - "Parlando con altri {{cleanJobTitle}} nel settore, una cosa che sento spesso è che cambiare strumento per il WhatsApp fa paura — ma rimanere su [tool] significa continuare a pagare per qualcosa che non risponde ai lead di portale in automatico."
   - "Una cosa che noto spesso in agenzie che usano [tool]: il sistema c'è, ma i lead di Immobiliare.it e Casa.it aspettano ancora una risposta manuale."

B. FRANCHISE / MULTI-LOCATION — if {{IT_RealEstate_Industry}} or {{companyDescriptionFromApollo}} mentions più sedi, franchising, or rete
   Pre-written options (pick one):
   - "Parlando con altri {{cleanJobTitle}} di reti immobiliari, una cosa che vedo spesso è che più sedi hai, più è difficile garantire che ogni ufficio risponda ai lead di portale entro i primi 5 minuti."
   - "Una cosa che vedo spesso in franchising immobiliari: i lead arrivano, ma tra un ufficio e l'altro qualcuno risponde in ritardo — e il cliente è già passato al competitor."

C. PROPERTY DEVELOPER / NUOVA COSTRUZIONE — if {{IT_RealEstate_Industry}} mentions costruttore, developer, nuova costruzione
   Pre-written options (pick one):
   - "Parlando con altri {{cleanJobTitle}} nel real estate di sviluppo, una cosa ricorrente è che i lead di nuova costruzione arrivano da portali e Meta Ads, ma il follow-up è ancora manuale — e tra un contatto e l'appuntamento si perdono settimane."
   - "Ho notato che per team come il vostro nel mercato di nuova costruzione, il tempo tra il primo lead e il primo contatto reale è spesso troppo lungo — e nel frattempo il lead raffredda."

D. STANDARD INDEPENDENT AGENCY — default
   Pre-written options (pick one):
   - "Parlando con altri {{cleanJobTitle}} in agenzia, una cosa che sento spesso: i lead di Immobiliare.it e Casa.it arrivano fuori orario, il weekend, o di sera — e quando li chiamate il giorno dopo, la metà ha già contattato qualcun altro."
   - "Una cosa che vedo spesso nelle agenzie: i lead dai portali aspettano ore prima di ricevere risposta. Nel tempo che impiegate a richiamarli, hanno già parlato con un competitor."

STEP 2 — Select the best-fitting option from the matching profile. Substitute [tool] with the actual tool name if profile A, leave other variables as-is.

Rules:
- Output ONLY the final sentence(s). No step labels, no reasoning.
- Italian only
- Do not add any words before or after the selected sentence
```

---

## Column 4: `Friction_Context_Personalized`
**Model:** Haiku 4.5 | **Temperature:** 0.5
**Purpose:** 1–2 sentence friction context for Email 2 body — explains WHY they have the problem.

```
You are a cold email copywriter for Spoki, a WhatsApp automation platform for real estate agencies in Italy.

Lead context:
- Company: {{companyName}}
- Job title: {{cleanJobTitle}}
- Agency type: {{IT_RealEstate_Industry}}
- Company description: {{companyDescriptionFromApollo}}
- Pain identified: {{RealEstate_Pain_Point_Normalized}}

STEP 1 — Select the friction profile:

A. FRANCHISE / MULTI-LOCATION (if {{IT_RealEstate_Industry}} or description mentions più sedi, rete, franchising):
   → "Con più sedi, ogni ufficio gestisce i lead in modo diverso — orari differenti, agenti diversi, nessuna risposta centralizzata. Il risultato: il cliente chiama il primo che risponde, e non sempre siete voi."

B. SMALL TEAM / SINGLE OFFICE (default for independent agencies < 20 employees):
   → "Con un team piccolo, seguire ogni lead di portale in tempo reale è impossibile — soprattutto fuori orario e il weekend, quando i clienti cercano casa ma voi non siete operativi."

C. DEVELOPER / NUOVA COSTRUZIONE:
   → "Il ciclo di acquisto per una nuova costruzione è lungo, ma la finestra per agganciare il lead è breve — se non rispondete nelle prime ore, il lead smette di rispondere e si guarda intorno."

D. COMPETITOR TOOL USER (if {{technologiesFromApollo}} contains a WhatsApp tool):
   → "Avere già uno strumento WhatsApp è un vantaggio, ma se non è configurato per rispondere ai lead di portale in automatico, state ancora perdendo contatti nelle prime ore critiche."

STEP 2 — Output the selected sentence as-is. Substitute {{companyName}} or {{cleanJobTitle}} only if it improves naturalness.

Rules:
- Max 25 words total
- Italian only
- Output ONLY the final sentence. No reasoning, no labels.
```

---

## Column 5: `RealEstate_Social_Proof`
**Model:** GPT-4o | **Temperature:** 0.3
**Purpose:** Named client result for Email 2 body.

```
You are a cold email copywriter for Spoki, a WhatsApp automation platform for real estate agencies in Italy.

Lead context:
- Company: {{companyName}}
- Agency type: {{IT_RealEstate_Industry}}
- Company description: {{companyDescriptionFromApollo}}
- Technologies used: {{technologiesFromApollo}}

STEP 1 — Select the social proof case:

A. If {{technologiesFromApollo}} contains a WhatsApp tool (Charles, ManyChat, Zendesk, Twilio, Respond.io):
   → "Gattinoni, una delle principali reti di agenzie di viaggio in Italia, è migrata da Zendesk a Spoki — e ha ridotto il tempo di risposta ai lead da ore a secondi."
   (Note: use this if competitor tool is detected — displacement proof is strongest signal)

B. If {{IT_RealEstate_Industry}} or {{companyDescriptionFromApollo}} suggests large franchise, rete, or multi-location (or companySize > 30):
   → "Tempocasa, rete immobiliare con 50+ sedi in Italia, ha ridotto il tempo medio di risposta ai lead da 4 ore a 2 minuti — e ha firmato il contratto con noi in 12 giorni."

C. Default (small/independent agency):
   → "Percent Servicios Inmobiliarios, agenzia indipendente in Spagna, ha triplicato il tasso di risposta ai lead nel weekend senza assumere personale aggiuntivo."

STEP 2 — Output the selected sentence as-is.

Rules:
- Italian only
- Output ONLY the social proof sentence. No reasoning, no explanation.
```

---

## Column 6: `IT_RealEstate_Solution_Normalized`
**Model:** Haiku 4.5 | **Temperature:** 0.5
**Purpose:** Single conversational solution sentence for Email 1 body. Two-step: select core → rewrite with natural opener.

```
You are a cold email copywriter for Spoki, a WhatsApp automation platform for real estate agencies in Italy.

Lead context:
- Company: {{companyName}}
- Job title: {{cleanJobTitle}}
- Agency type: {{IT_RealEstate_Industry}}
- Company description: {{companyDescriptionFromApollo}}
- Technologies used: {{technologiesFromApollo}}
- Pain identified: {{RealEstate_Pain_Point_Normalized}}

STEP 1 — Select the solution core that best fits. Check in order:

A. COMPETITOR DISPLACEMENT — if {{technologiesFromApollo}} contains Charles, ManyChat, Zendesk, Twilio, or Respond.io
   → Core: "sostituiamo [nome tool] con un flusso WhatsApp più semplice — attivo in 48 ore, senza sviluppatori"
   → Replace [nome tool] with the actual tool name found in Technologies

B. LARGE FRANCHISE / MULTI-LOCATION — if description or {{IT_RealEstate_Industry}} mentions più sedi, franchising, rete
   → Core: "ogni sede risponde ai lead di portale in meno di 60 secondi — automaticamente, senza che nessun agente debba farlo a mano"

C. PROPERTY DEVELOPER / NUOVA COSTRUZIONE — if {{IT_RealEstate_Industry}} or description mentions costruttore, developer, nuova costruzione
   → Core: "automatizziamo il follow-up sui lead di nuova costruzione — dal primo contatto WhatsApp all'appuntamento in cantiere"

D. STANDARD INDEPENDENT AGENCY — default
   → Core: "rispondiamo automaticamente ai lead di Immobiliare.it e Casa.it su WhatsApp — prima che chiamino il competitor"

STEP 2 — Rewrite the selected core as a single conversational sentence. Choose ONE opener:
- "Noi aiutiamo agenzie come la vostra a..."
- "Quello che facciamo è semplice:"
- "In pratica,"

Pick the opener that flows most naturally after {{RealEstate_Pain_Point_Normalized}}.

Rules:
- Max 25 words total
- No stats, no numbers, no product feature lists
- Peer-to-peer tone
- Italian only
- Output ONLY the final sentence. No step labels, no reasoning.
```

---

## Column 7: `RealEstate__Outcome_Metric_`
**Model:** Haiku 4.5 | **Temperature:** 0.5
**Purpose:** 1–2 sentence industry stat for Email 3 body. Note: double underscore in name is intentional (matches copy-frameworks.md naming convention).

```
You are a cold email copywriter for Spoki, a WhatsApp automation platform for real estate agencies in Italy.

Lead context:
- Company: {{companyName}}
- Agency type: {{IT_RealEstate_Industry}}

STEP 1 — Select the most relevant stat based on agency type:

A. FRANCHISE / MULTI-LOCATION or DEVELOPER:
   → "Harvard Business Review riporta che il 78% degli acquirenti sceglie la prima agenzia che risponde. Per una rete come {{companyName}}, ogni ora di ritardo equivale a cedere lead qualificati — e commissioni — ai competitor."

B. STANDARD INDEPENDENT AGENCY (default):
   → "Le agenzie che rispondono ai lead entro 60 secondi convertono il 391% in più rispetto a quelle che rispondono in un'ora (dati Velocify). Per {{companyName}}, questo è lead che vi scelgono — o che chiamano qualcun altro."

STEP 2 — Output the selected sentence as-is, with {{companyName}} substituted.

Rules:
- 2 sentences max
- Italian only
- Output ONLY the final text. No labels, no reasoning.
```

---

## Column 8: `IT_RealEstate_Subject_Line`
**Model:** Haiku 4.5 | **Temperature:** 0.5
**Purpose:** Email 1 subject line.

```
You are a cold email copywriter for Spoki, a WhatsApp automation platform for real estate agencies in Italy.

Lead context:
- Company: {{companyName}}
- Agency type: {{IT_RealEstate_Industry}}
- Pain identified: {{RealEstate_Pain_Point_Normalized}}

Write ONE subject line in Italian for a cold email to {{companyName}}.

Rules:
- 2–4 words MAXIMUM — strictly enforced
- ALL lowercase — no capitals anywhere
- No questions — do not use "?" under any circumstances
- No emoji
- No punctuation at the end
- Reference the core pain: slow lead response, losing portal leads to competitors
- Sound like a colleague, not an ad

Examples of correct format:
- "lead persi di notte"
- "risposta automatica portali"
- "follow-up immediato immobiliare"
- "lead immobiliare non risponde"

Examples of WRONG format (do not do these):
- "Quanto tempo impiegate a rispondere?" — has a question mark, too long
- "Lead Response Automation" — wrong language, capitalised
- "🏠 rispondete ai lead?" — emoji + question

Return ONLY the subject line. No explanation, no quotes.
```

---

## How to create in Lemlist UI

1. Go to **ITA_RealEstate** campaign → **Leads** tab
2. Click **"Create AI Columns"** → **"Create AI columns"** dropdown → **"AI Column"** tab → **"Create from scratch"**
3. For each column, set:
   - **Column name**: exact name from table above (copy-paste to avoid typos)
   - **AI model**: as specified per column
   - **Temperature**: as specified per column
   - **Prompt**: paste from above
4. Create all 8 columns **in order** (1 → 8) — later columns depend on earlier ones
5. After all 8 are created, click **"Enrich 2 leads"** to run on Marco Ferrari and Anna Rossi
6. Review outputs before launching campaign

---

## Variable reference — what maps to what from Apollo CSV import

| Lemlist variable | Apollo CSV column |
|-----------------|-------------------|
| `{{firstName}}` | First Name |
| `{{lastName}}` | Last Name |
| `{{companyName}}` | Company Name |
| `{{jobTitle}}` | Title |
| `{{companySize}}` | # Employees |
| `{{website}}` | Website |
| `{{companyDescriptionFromApollo}}` | Company Description |
| `{{technologiesFromApollo}}` | Technologies |
| `{{keywordsFromApollo}}` | Keywords |
| `{{linkedinUrl}}` | Person Linkedin Url |
| `{{location}}` | City |

*Generated 2026-03-03 — Campaign: cam_XGHFWnDWroM6Reip9*
