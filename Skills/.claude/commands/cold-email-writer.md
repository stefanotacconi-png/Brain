# Cold Email Writer

Generate personalized cold email sequences for each lead. For new campaigns, build a self-contained campaign prompt template first — this lets you review and refine copy strategy before generating at scale.

## Two-step workflow

```
Step 0 (optional): Build campaign prompt template  →  reviewed once per campaign
Step 1+:           Generate emails per lead         →  run for each new batch
```

If a prompt template already exists for this campaign in `/templates/email-prompt-[campaign-slug]-*.md`, skip to Step 1. If not, offer to build one first.

---

## Step 0 — Build campaign prompt template (run once per campaign)

Accept `$ARGUMENTS` as the campaign slug (e.g. `real-estate-spain`, `beauty-italy`), or ask: "Is this a new campaign? Which vertical and market?"

### 0.1 — Gather inputs

| Input | Where to read | Required |
|-------|--------------|----------|
| ICP, value prop, proof points, metrics | CLAUDE.md | yes |
| Hypothesis set | `/output/hypothesis_set_[vertical-slug].md` | yes — run `/hypothesis-building` first if missing |
| Enriched CSV column definitions | Most recent `/output/enriched_leads*.csv` | yes |
| Campaign brief | User input — audience, roles, geography | yes |
| Competitor displacement targets | CLAUDE.md competitive landscape | optional |

Ask the user:
1. "Which target roles are we writing for?" (e.g. CEO, CRM Manager, CMO)
2. "Displacement campaign (they're using a competitor) or greenfield?"
3. "Any banned phrases beyond CLAUDE.md defaults?"

### 0.2 — Define structural variants

| Variant | Target roles | Word limit | Format |
|---------|-------------|-----------|--------|
| A — Champion | CRM Manager, Ecommerce Manager, Digital Marketing Manager | ≤120 words | 4 paragraphs, concrete data, low-friction CTA |
| B — Founder/CEO (SME) | CEO, Founder, Amministratore Delegato (<50 employees) | ≤90 words | 3 paragraphs, stage-tied pain, merged value+proof |
| C — Executive | CMO, Marketing Director, General Manager | ≤70 words | 2–3 paragraphs, one sharp observation, forwardable format |
| D — Displacement | Any role currently using a named competitor | ≤80 words | Name competitor in line 1, pivot to gap |
| Follow-up | Any — 3–7 days after no reply | ≤60 words | Case study + sector-shaped CTA |

### 0.3 — Build the prompt file (11 sections)

Generate a single self-contained markdown file. No "see file X" references — everything embedded:

1. **Role line** — who the LLM writes as; sender identity, company name, product positioning (from CLAUDE.md)
2. **Core pain** — audience-specific problem grounded in the hypothesis set. Specific, not generic: "appointment no-show rate averages 25% in beauty clinics of your size", not "you want to grow"
3. **Voice rules** — tone, constraints, banned words. Pull from CLAUDE.md copy principles + campaign additions. Always include: subject lines <8 words; first line hyper-personalized; never use "I hope this finds you well", "I wanted to reach out", "quick question"; Italy = slightly more formal; Spain = direct, warmer tone
4. **Research context** — embed actual numbers from CLAUDE.md metrics table. Never use placeholder stats. Required: 98% WhatsApp open rate vs 10% email, 23x ROI, 20,000+ customers, relevant vertical stat (no-show -60% beauty, cart recovery 25–35% fashion, etc.)
5. **Enrichment field map** — map each CSV column → what it means → how to use it → what to do when blank or "N/A". Flag which columns are personalization triggers vs background context
6. **Hypothesis P1 rules** — for each hypothesis in the set: short name, mechanism (why the pain exists, not just that it does), best-fit company profile, opening line angle
7. **Role-based emphasis** — per variant: which proof points to lead with (peer-relevant by size + industry), which metric to feature (CEO → ROI/revenue; CRM Manager → integration/automation depth; CMO → channel performance vs email), tone adjustment notes
8. **Competitive rules** (if displacement) — per competitor in scope: name explicitly, key weakness (from CLAUDE.md displacement targets), positioning pivot (replace / layer-on-top / consolidate). Never disparage — acknowledge they made a smart choice, offer a specific gap
9. **Proof point selection** — 3-dimension filter: (1) peer vertical + company size match, (2) hypothesis alignment — proof validates the specific pain claimed, (3) non-redundancy — don't repeat same client across emails in the sequence. Available by vertical: Feltrinelli (Education), Gattinoni (Travel), Tempocasa (Real Estate), Zampa (Pet), Nuna Lie (Fashion), Expert Mallardo (Electronics), EtnaWellness (Beauty)
10. **Variant selection logic** — explicit if/then rules: "If `job_title` contains [CEO / Founder / Titolare / Amministratore] → Variant B. If [Responsabile CRM / CRM Manager / Ecommerce] → Variant A..." Include fallback: if title unclassifiable → Variant A
11. **Output format** — JSON with `subject_1`, `body_1`, `subject_2`, `body_2`, `subject_3`, `body_3`; bodies in plain text (no markdown, no bullet points); variable references in `{{double braces}}`; flag any lead where personalization angle could not be found — do not fabricate

### 0.4 — Self-containment check before saving

- [ ] Voice rules sourced from CLAUDE.md (not from memory)
- [ ] All metrics use actual numbers (not "high open rate")
- [ ] Variant selection covers all target roles
- [ ] P1 descriptions use mechanisms, not vague pain labels
- [ ] Proof points pass all 3 criteria
- [ ] Competitive rules present if displacement campaign
- [ ] No "see file X" references anywhere

Save to: `/templates/email-prompt-[campaign-slug]-[YYYY-MM-DD].md`

Print summary: campaign name, target roles, hypotheses covered, variants included, proof points available, enrichment columns mapped.

Ask: "Does this prompt look right? Should I proceed to email generation?"

---

## Step 1 — Load inputs for generation

Accept `$ARGUMENTS` as the CSV path, or ask which file to use. Optionally accept `--prompt <path>` to specify the template file.

1. Load the most recent matching prompt template from `/templates/email-prompt-[campaign-slug]-*.md`
2. Load copy frameworks from `/templates/copy-frameworks.md`
3. Load email examples from `/templates/email-examples.md` if it exists

---

## Step 2 — Generate email sequences

For each lead in the CSV:
- Research personalization angles (title, company, industry, tier_reason, enrichment fields)
- **Step 1 (Day 1):** Opening cold email — hook + value prop + soft CTA
- **Step 2 (Day 3):** First follow-up — different angle, add social proof
- **Step 3 (Day 7):** Second follow-up — short, pattern-interrupt, last try
- Each email: subject line + body (max 5 sentences) + CTA

Apply from CLAUDE.md:
- Subject lines under 8 words
- First line hyper-personalized (never generic)
- One CTA per email
- No attachments mentioned

Personalization sources (priority order):
1. Recent LinkedIn post or company news
2. Company tech stack or tools they use
3. Specific job title + company stage
4. Industry-specific pain point
5. Mutual connection or shared context

---

## Step 3 — Output and review

Save to `/output/campaign_copy_[YYYY-MM-DD].csv` with Lemlist-compatible columns:
- `email`, `firstName`, `lastName`, `companyName`
- `subject_1`, `body_1`, `subject_2`, `body_2`, `subject_3`, `body_3`
- `personalization_note` (your reference — not uploaded to Lemlist)

In email bodies, wrap variable references in `{{double braces}}` — Lemlist resolves these per lead at send time (e.g. `Hi {{firstName}}, noticed {{companyName}} recently...`).

Print 3 example generated emails for review.

Ask: "Does this copy look right? Should I push this campaign to Lemlist?"

---

## Notes

- Never use "I hope this finds you well" or similar openers
- If no genuine personalization angle exists, flag that lead for manual review — never fabricate
- Adapt tone per ICP: founders = casual/direct; enterprise = more formal
- The prompt file is version-controlled — keep old versions in `/templates/` for comparison
- For displacement campaigns, always name the competitor explicitly — vague "you might be using another tool" underperforms

## Example Usage

New campaign (builds prompt first):
```
/cold-email-writer /output/enriched_leads_beauty_italy.csv
```

With existing prompt:
```
/cold-email-writer --prompt /templates/email-prompt-beauty-italy-2026-03-05.md /output/enriched_leads.csv
```

Build prompt only (no email generation yet):
```
/cold-email-writer --setup real-estate-spain
```
