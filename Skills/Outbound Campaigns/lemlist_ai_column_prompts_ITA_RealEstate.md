# Lemlist AI Column Prompts — ITA_RealEstate
**Version:** 3.0 — Rebuilt on PDF framework (ITA_Retail architecture)
**Updated:** 2026-03-03
**Campaign:** ITA_RealEstate (cam_XGHFWnDWroM6Reip9)

Create columns in Lemlist → Leads → "Create AI Columns" → "AI Column" tab → "Create from scratch".
**Create in order 1→8. Each column feeds the next.**

---

## Column order & model

| # | Column name | Model | Temp |
|---|-------------|-------|------|
| 1 | `cleanJobTitle` | GPT-4o | 0.3 |
| 2 | `IT_RealEstate_Industry` | GPT-4o | 0.3 |
| 3 | `RealEstate_Pain_Point_Normalized` | Haiku 4.5 | 0.5 |
| 4 | `Friction_Context_Personalized` | Haiku 4.5 | 0.5 |
| 5 | `Social_Proof` | Haiku 4.5 | 0.5 |
| 6 | `IT_RealEstate_Solution_Normalized` | Haiku 4.5 | 0.5 |
| 7 | `RealEstate__Outcome_Metric_` | Haiku 4.5 | 0.5 |
| 8 | `IT_RealEstate_Subject_Line` | Haiku 4.5 | 0.5 |

---

## Column 1: `cleanJobTitle`
**Model:** GPT-4o | **Temp:** 0.3

```
You are a job title standardization assistant.
Your task is to clean and standardize job titles while following these strict rules:

Rules:
- Language preservation is critical:
  - Never translate the job title, always keep it in the original language
  - When modifying or adding words, do it in the original language
- Format case (latin characters only):
  - Use title case (capitalize first letter of each word)
  - Keep common acronyms/initialisms fully uppercase (CEO, CTO, VP, CFO, HR, IT, COO, CMO, etc)
- Remove unnecessary seniority terms:
  - Keep principal seniority terms: C-level, VP, Director, Head, Principal, Lead
  - Remove other seniority indicators unless crucial for role clarity
- Replace or remove decorative terms with professional equivalents
- Remove unnecessary elements: emojis, special characters, company names, locations, years of experience, contract types
- Handle multiple roles: keep only the most relevant or first role
- Don't return anything for invalid or meaningless titles (e.g. "-----", "n/a", "?", " ")

Examples:
"Senior Software Engineer @ Google" → "Software Engineer"
"CTO & Co-founder 🚀" → "CTO"
"Head of HR - EMEA Region" → "Head of HR"
"Presidente Amministratore Delegato & Co-Fondatore" → "CEO"
"VP of Sales & Marketing | Team Lead" → "VP Sales"

Always return just the cleaned title without any explanation or additional text.
Never translate the job title, always return in the original language.
If empty, meaningless, or invalid, do not return anything.

Clean the following job title: {{jobTitle}}
```

---

## Column 2: `IT_RealEstate_Industry`
**Model:** GPT-4o | **Temp:** 0.3

```
Leggi questa descrizione aziendale da LinkedIn e rispondi con una sola cosa: che cosa fa concretamente questa agenzia immobiliare. Non il settore, non la missione, non la visione. L'attività per cui qualcuno paga.

La tua risposta deve funzionare in questa frase:
"Ho visto che vi occupate di ___."

Esempi corretti:
- "compravendita residenziale nella zona di Milano"
- "affitti brevi e gestione proprietà in Toscana"
- "immobili commerciali e uffici nel centro di Roma"
- "nuove costruzioni residenziali in Veneto"
- "franchising immobiliare con più sedi in Italia"

Esempi sbagliati:
- "soluzioni immobiliari innovative" (troppo vago, linguaggio da mission)
- "aiutiamo i clienti a trovare casa" (non è un'offerta, è uno slogan)
- "immobiliare" (troppo generico)

Regole:
- Una frase sola, massimo 8 parole
- Niente punti finali, elenchi o spiegazioni
- Ignora tutto il linguaggio di visione, filosofia e advocacy
- In italiano

Descrizione azienda:
{{companyDescriptionFromApollo}}
```

---

## Column 3: `RealEstate_Pain_Point_Normalized`
**Model:** Haiku 4.5 | **Temp:** 0.5

```
Step 1: Leggi {{companyDescriptionFromApollo}} e {{IT_RealEstate_Industry}} e identifica in massimo 3 parole la sottocategoria dell'agenzia (es. "agenzia residenziale", "rete franchising", "developer nuova costruzione", "gestione affitti", "immobiliare commerciale"). Chiamala [tipo].

Step 2: In base a {{companyDescriptionFromApollo}}, {{cleanJobTitle}}, {{technologiesFromApollo}} e il settore Immobiliare, seleziona la categoria e l'opzione (A o B) più rilevante.

Categorie:

- Agenzia residenziale / indipendente (agenzia singola, piccolo team, compravendita casa):
  A) "Parlando con altri {{cleanJobTitle}}, il tema che esce sempre sono i lead di Immobiliare.it e Casa.it che arrivano fuori orario e il giorno dopo hanno già chiamato un'altra agenzia."
  B) "Una cosa che vedo spesso in immobiliare: i lead dai portali arrivano la sera, il weekend, nei festivi — quando nessuno risponde — e lunedì mattina sono già andati altrove."

- Franchising / rete multi-sede (più uffici, brand immobiliare, rete di agenzie):
  A) "Parlando con altri {{cleanJobTitle}} di reti immobiliari, il tema che esce sempre è che ogni sede risponde ai lead di portale in modo diverso, senza uno standard centralizzato."
  B) "Ho notato che per reti come la vostra il problema vero sono i lead che arrivano a sedi diverse e non ricevono risposta nei tempi giusti — soprattutto fuori orario."

- Costruttore / developer (nuova costruzione, immobiliare di sviluppo, cantieri):
  A) "Parlando con altri {{cleanJobTitle}} nel real estate di sviluppo, il tema che esce sempre sono i lead di nuova costruzione che si interessano, non ricevono risposta veloce, e spariscono."
  B) "Una cosa che vedo spesso con i developer: i lead arrivano da portali e Meta Ads, ma tra il primo contatto e una risposta reale passano giorni — e l'interesse si raffredda in ore."

- Gestione affitti / property management (affitti, inquilini, property manager):
  A) "Parlando con altri {{cleanJobTitle}}, il tema che esce sempre sono le richieste degli inquilini — rinnovi, guasti, documenti — che il team gestisce ancora a mano, una per una."
  B) "Ho notato che per team come il vostro il vero problema sono le comunicazioni ricorrenti con gli inquilini che portano via ore ogni settimana senza generare valore."

- Immobiliare commerciale (uffici, capannoni, negozi, immobili aziendali):
  A) "Parlando con altri {{cleanJobTitle}}, il tema che esce sempre sono le trattative commerciali che si perdono perché il follow-up tra un contatto e l'altro è troppo lento."
  B) "Ho notato che per team come il vostro il collo di bottiglia è il tempo che passa tra il primo interesse di un cliente e la prima risposta concreta — e nel frattempo il cliente guarda altrove."

REGOLE:
- Sostituisci {{cleanJobTitle}} con il ruolo effettivo del lead
- Se la descrizione è vaga, usa la categoria più vicina al settore immobiliare residenziale
- Adatta le preposizioni perché la frase suoni naturale in italiano

OUTPUT (OBBLIGATORIO):
- Restituisci ESCLUSIVAMENTE la frase finale con {{cleanJobTitle}} già sostituito
- NON mostrare Step 1, Step 2, categoria o ragionamento
- L'output deve contenere SOLO la frase, nient'altro
```

---

## Column 4: `Friction_Context_Personalized`
**Model:** Haiku 4.5 | **Temp:** 0.5

```
Analizza la sottocategoria del lead: {{IT_RealEstate_Industry}} e {{keywordsFromApollo}}.

Scrivi una frase breve e conversazionale in italiano che descriva la specifica frizione che fa perdere lead o clienti.

Regole specifiche per nicchia:

• Agenzia residenziale / indipendente: I lead dai portali non aspettano: se non ricevono risposta entro pochi minuti, chiamano la prima agenzia disponibile — che di solito non siete voi.

• Franchising / rete multi-sede: Con più sedi attive, garantire lo stesso standard di risposta ai lead in ogni ufficio è quasi impossibile senza un processo centralizzato.

• Costruttore / developer: I lead di nuova costruzione hanno un ciclo d'acquisto lungo, ma la finestra di interesse iniziale dura ore — non giorni. Chi non risponde subito non recupera più.

• Gestione affitti / property management: Ogni richiesta dell'inquilino gestita a mano è tempo sottratto alle trattative vere. Il volume cresce, il team si satura, qualcosa si perde.

• Immobiliare commerciale: Le trattative commerciali richiedono follow-up precisi e tempestivi: ogni giorno di ritardo nella risposta aumenta il rischio che il cliente valuti alternative.

Vincoli:
- Massimo 25 parole
- Evita gergo commerciale (niente "ottimizzazione" o "conversione")
- Deve sembrare un'osservazione tra pari
- Specifica sempre il soggetto della friction (es. "i lead dai portali", "le richieste degli inquilini")

Output SEMPRE in italiano.
```

---

## Column 5: `Social_Proof`
**Model:** Haiku 4.5 | **Temp:** 0.5

```
Analizza la nicchia specifica di {{companyName}} all'interno del settore immobiliare (es. agenzia indipendente, rete franchising, developer, gestione affitti) analizzando {{IT_RealEstate_Industry}} e {{companyDescriptionFromApollo}}.

Seleziona il risultato Spoki più rilevante per il loro flusso operativo:

• Franchising / rete multi-sede: "Abbiamo aiutato reti come Tempocasa — 50+ sedi — a rispondere ai lead di portale in meno di 60 secondi per ogni ufficio, automaticamente su WhatsApp."

• Agenzia residenziale / indipendente: "Abbiamo aiutato agenzie indipendenti a triplicare il tasso di risposta ai lead nel weekend senza assumere personale aggiuntivo, automatizzando WhatsApp."

• Costruttore / developer: "Abbiamo aiutato developer immobiliari a qualificare i lead di nuova costruzione in automatico su WhatsApp, riducendo il tempo dal primo contatto all'appuntamento da giorni a ore."

• Gestione affitti / property management: "Abbiamo aiutato team di property management a gestire richieste, rinnovi e manutenzioni su WhatsApp in automatico, liberando ore di lavoro manuale ogni settimana."

• Immobiliare commerciale: "Abbiamo aiutato realtà come Reental a non perdere trattative per follow-up lenti, automatizzando il primo contatto WhatsApp entro 60 secondi da ogni richiesta."

Scrivi una sola frase (max 25 parole) con questa struttura:
"Abbiamo aiutato [tipo agenzia] a [risultato concreto] automatizzando WhatsApp."

Evita linguaggio generico.
Usa termini specifici come portali, sedi, inquilini, cantiere, lead in base al lead.
Non inserire mai nel copy il nome dell'azienda trovato in {{companyName}}.

Output SEMPRE in italiano.
```

---

## Column 6: `IT_RealEstate_Solution_Normalized`
**Model:** Haiku 4.5 | **Temp:** 0.5

```
Step 1: In base a {{RealEstate_Pain_Point_Normalized}}, {{cleanJobTitle}}, {{technologiesFromApollo}} e {{IT_RealEstate_Industry}}, seleziona la soluzione Spoki più rilevante.

Soluzioni disponibili:

- Risposta automatica ai lead di portale (agenzia residenziale / indipendente):
"Spoki risponde automaticamente su WhatsApp a ogni lead di Immobiliare.it e Casa.it entro 60 secondi. Nessun agente deve essere disponibile: il lead riceve risposta mentre il competitor ancora aspetta."

- Centralizzazione risposta per reti (franchising / rete multi-sede):
"Spoki centralizza la risposta ai lead di portale per tutte le sedi. Ogni ufficio risponde con lo stesso standard, in automatico, 24 ore su 24, senza coordinamento manuale."

- Follow-up nuova costruzione (costruttore / developer):
"Spoki manda un messaggio WhatsApp in automatico a ogni lead di nuova costruzione entro 60 secondi. Il contatto si qualifica mentre la concorrenza non ha ancora risposto."

- Gestione inquilini (property management / affitti):
"Spoki gestisce su WhatsApp le richieste ricorrenti degli inquilini — rinnovi, guasti, documenti. Il team smette di rispondere a mano e si concentra sulle trattative."

- Immobiliare commerciale (uffici, capannoni, negozi, immobili aziendali):
"Spoki manda un messaggio WhatsApp automatico a ogni richiesta di spazio commerciale entro 60 secondi. Il cliente riceve risposta prima di valutare alternative, senza che nessun agente debba essere disponibile."

Step 2: Riscrivi la soluzione selezionata come una singola frase da inserire in una cold email. Collegala direttamente al pain point in {{RealEstate_Pain_Point_Normalized}}, come se lo stessi spiegando a voce.

Inizia con una di queste strutture:
- "Noi aiutiamo agenzie come la vostra a..."
- "Quello che facciamo è semplice:"
- "In pratica,"

Regole:
- Massimo 25 parole
- UNA sola soluzione, UN solo beneficio. Non elencare, non combinare
- Linguaggio semplice e diretto, niente gergo marketing
- Niente numeri o statistiche (vengono aggiunti altrove nell'email)
- Deve suonare come un suggerimento tra colleghi, non come una headline pubblicitaria

Esempi di tono giusto:
- "Noi aiutiamo agenzie come la vostra a rispondere ai lead di portale su WhatsApp in automatico, prima che chiamino qualcun altro."
- "Quello che facciamo è semplice: quando arriva un lead da Immobiliare.it, parte un WhatsApp in automatico — anche di notte, anche il weekend."
- "In pratica, ogni lead che arriva da portale riceve una risposta WhatsApp in 60 secondi, senza che nessun agente debba farlo a mano."

OUTPUT (OBBLIGATORIO):
- Restituisci ESCLUSIVAMENTE la frase finale riscritta
- NON mostrare Step 1, Step 2, quale soluzione hai scelto o il ragionamento
- L'output deve contenere SOLO la frase, nient'altro
```

---

## Column 7: `RealEstate__Outcome_Metric_`
**Model:** Haiku 4.5 | **Temp:** 0.5
*(Double underscore before Outcome, trailing underscore — exact naming from copy-frameworks.md)*

```
Obiettivo: mostrare l'impatto concreto che Spoki genera su una metrica chiave in base alla sottocategoria immobiliare del lead.

Analizza {{IT_RealEstate_Industry}} e identifica quale superpower di Spoki è più rilevante:

• Agenzia residenziale / indipendente: rispondere ai lead di portale prima dei competitor — le agenzie che rispondono entro 60 secondi convertono molte più trattative di quelle che aspettano anche solo un'ora.

• Franchising / rete multi-sede: standardizzare la risposta in tutte le sedi — ogni ufficio risponde con lo stesso standard e nello stesso tempo, senza coordinamento manuale tra agenti.

• Costruttore / developer: qualificare i lead nel momento di massimo interesse — un messaggio WhatsApp automatico entro 60 secondi trasforma un lead freddo in un appuntamento in cantiere.

• Gestione affitti / property management: ridurre il tempo dedicato alle comunicazioni ricorrenti — automatizzare rinnovi, guasti e richieste degli inquilini libera ore di lavoro ogni settimana.

• Immobiliare commerciale: non perdere trattative per follow-up lenti — nel commerciale, chi risponde per primo stabilisce il frame della negoziazione.

Regole di normalizzazione:
- Restituisci una sola frase, conversazionale, con un risultato specifico
- Usa un linguaggio molto semplice, comprensibile a tutti
- Concentrati su velocità di risposta o eliminazione delle frizioni
- Niente elenchi, niente step, niente ragionamento

Output SEMPRE in italiano. Una sola frase.
```

---

## Column 8: `IT_RealEstate_Subject_Line`
**Model:** Haiku 4.5 | **Temp:** 0.5

```
Variabili di input: {{RealEstate_Pain_Point_Normalized}}, {{IT_RealEstate_Industry}}, {{cleanJobTitle}}

Genera un oggetto email per una cold email in italiano.

L'oggetto deve sembrare un messaggio che un collega o un contatto di lavoro manderebbe, non una newsletter o una promozione.

Regole:
- Tra 2 e 4 parole, tutto minuscolo
- Deve sembrare personale e 1:1
- Niente domande, niente emoji, niente punti esclamativi
- Può fare riferimento al pain point in modo indiretto
- Non deve contenere "?"

Esempi di oggetti giusti:
- "lead fuori orario"
- "risposta ai portali"
- "tempi di risposta"
- "whatsapp per gli agenti"
- "lead immobiliare"
- "una cosa su {{IT_RealEstate_Industry}}"

Esempi di oggetti sbagliati:
- "offerta esclusiva per te" (spam)
- "aumenta le conversioni" (pubblicità)
- "soluzione innovativa" (generico e da AI)
- "opportunità imperdibile" (clickbait)
- "ciao" (troppo vago)

Output: solo l'oggetto, nient'altro. In italiano.
```

---

## Email variable map

| Email | Variables used |
|-------|----------------|
| E1 subject | `{{IT_RealEstate_Subject_Line}}` |
| E1 body | `{{RealEstate_Pain_Point_Normalized}}` + `{{IT_RealEstate_Solution_Normalized}}` |
| E2 body | `{{Friction_Context_Personalized}}` + `{{Social_Proof}}` |
| E3 body | `{{RealEstate__Outcome_Metric_}}` |
| E4 body | static — no AI column needed |

---

## Apollo CSV → Lemlist variable map

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

*Updated 2026-03-03 — v3.0 on PDF framework*
