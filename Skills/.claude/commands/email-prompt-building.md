# Email Prompt Building

Build a self-contained campaign email prompt template that feeds `/cold-email-writer` and generates personalized emails at scale. Separates strategy (done once) from execution (run per contact row).

## What this skill does

Reads CLAUDE.md, a hypothesis set, and enriched CSV column definitions, then synthesizes a single self-contained markdown prompt file. That file becomes the complete instruction set for `/cold-email-writer` — no runtime file lookups, all reasoning baked in.

The key improvement over running `/cold-email-writer` directly: the prompt template can be reviewed, refined, and version-controlled before a single email is generated. Fixes apply to all emails, not one at a time.

## Instructions

### Step 1 — Gather inputs

Accept `$ARGUMENTS` as the campaign name/vertical slug (e.g. `"real-estate-spain"`), or ask:
"What campaign is this prompt for? (e.g. real-estate-spain, beauty-italy)"

Then collect:

| Input | Where to read | Required |
|-------|--------------|----------|
| ICP, value prop, proof points, metrics | CLAUDE.md | yes |
| Hypothesis set | `/output/hypothesis_set_[vertical-slug].md` | yes — run `/hypothesis-building` first if missing |
| Enriched CSV column definitions | Most recent `/output/enriched_leads*.csv` or user input | yes |
| Campaign brief | User input — target audience, roles, geography | yes |
| Competitor displacement targets (if any) | CLAUDE.md competitive landscape section | optional |

Ask the user:
1. "Which target roles are we writing for?" (e.g. CEO, CRM Manager, CMO)
2. "Is this a displacement campaign (they're using a competitor) or a greenfield approach?"
3. "Any banned phrases or tone constraints beyond what's in CLAUDE.md?"

### Step 2 — Define structural variants

Map each role to a variant format:

| Variant | Target roles | Word limit | Format |
|---------|-------------|-----------|--------|
| A — Champion | CRM Manager, Ecommerce Manager, Digital Marketing Manager | ≤120 words | 4 paragraphs, concrete data, low-friction CTA |
| B — Founder/CEO (SME) | CEO, Founder, Amministratore Delegato (<50 employees) | ≤90 words | 3 paragraphs, stage-tied pain, merged value+proof |
| C — Executive | CMO, Marketing Director, General Manager | ≤70 words | 2-3 paragraphs, one sharp observation, forwardable format |
| D — Peer (displacement) | Any role — currently using a named competitor | ≤80 words | Acknowledge their existing tool by name in line 1, pivot to gap |
| Follow-up | Any — 3-7 days after no reply | ≤60 words | Case study + sector-shaped CTA |

### Step 3 — Build the prompt template

Generate a single markdown file with these 11 sections. Every section must be self-contained — no "see CLAUDE.md" references:

**1. Role line**
Who the LLM is writing as. Pull from CLAUDE.md: sender identity, company name, product positioning.

**2. Core pain**
The audience-specific problem, grounded in hypothesis set and vertical research. Not generic ("you want to grow") — specific ("appointment no-show rate averages 25% in beauty clinics of your size").

**3. Voice rules**
Tone, constraints, and banned words. Pull from CLAUDE.md copy principles + any campaign-specific additions. Always include:
- Subject lines: under 8 words
- First line: hyper-personalized — reference their specific industry + pain
- Never use: "I hope this finds you well", "I wanted to reach out", "quick question"
- Italy: slightly more formal. Spain: direct, warmer tone.

**4. Research context**
Embed actual numbers from CLAUDE.md metrics table. Do not use placeholder stats.
Required inclusions: 98% WhatsApp open rate vs 10% email, 23x ROI, 20,000+ customers, relevant vertical stat (no-show -60% for beauty, cart recovery 25-35% for fashion, etc.)

**5. Enrichment data fields**
Map each CSV column to how it should be used in the email:
- Column name → what it means → how to use it (or skip if empty)
- Flag which columns are personalization triggers vs background context
- Define what to do when a field is blank or "N/A"

**6. Hypothesis-based P1 rules**
For each hypothesis in the hypothesis set file:
- State the hypothesis short name (#1, #2, etc.)
- Write the mechanism (why this pain exists, not just that it exists)
- Define which company profile types this hypothesis fits best
- Give the opening line angle for an email targeting this hypothesis

**7. Role-based emphasis**
Per variant:
- Which proof points to lead with (peer-relevant by company size + industry)
- Which metric to feature (role-specific: CEO → ROI/revenue; CRM Manager → integration/automation depth; CMO → channel performance vs email)
- Tone adjustment notes

**8. Competitive awareness rules** (if displacement campaign)
For each competitor in scope (from CLAUDE.md competitive landscape):
- Name the competitor explicitly in the rule
- State their key weakness (from CLAUDE.md displacement targets)
- Define the positioning pivot: replacement vs layer-on-top vs consolidation
- Note: never disparage — acknowledge they made a smart choice, offer a specific gap

**9. Proof point selection criteria**
Three-dimensional filter for choosing which social proof to use:
1. Peer relevance — same vertical and company size as the prospect
2. Hypothesis alignment — proof point validates the specific pain claimed
3. Non-redundancy — don't repeat the same client across emails in the sequence

Notable clients available per vertical (from CLAUDE.md): Feltrinelli (Education), Gattinoni (Travel), Tempocasa (Real Estate), Zampa (Pet), Nuna Lie (Fashion), Expert Mallardo (Electronics), EtnaWellness (Beauty)

**10. Structural variants — selection logic**
Explicit if/then rules: "If `job_title` contains [CEO / Founder / Titolare / Amministratore], use Variant B. If it contains [Responsabile CRM / CRM Manager / Ecommerce], use Variant A..." etc.
Include fallback: "If title cannot be classified, use Variant A."

**11. Output format and constraints**
- Output as JSON with fields: `subject_1`, `body_1`, `subject_2`, `body_2`, `subject_3`, `body_3`
- Each body field is plain text — no markdown, no bullet points
- Variable references in `{{double braces}}` (Lemlist format)
- Flag any lead where personalization angle could not be found — do not fabricate

### Step 4 — Self-containment check

Before saving, verify:
- [ ] Voice rules come from CLAUDE.md (not hardcoded from memory)
- [ ] All metrics use actual numbers (not "high open rate")
- [ ] Variant selection logic covers all target roles
- [ ] P1 descriptions use mechanisms, not vague pain labels
- [ ] Proof points pass all 3 criteria (peer, alignment, non-redundancy)
- [ ] Competitive rules present if this is a displacement campaign
- [ ] No "see file X" references — everything needed is embedded

### Step 5 — Save and hand off

Save to: `/templates/email-prompt-[campaign-slug]-[YYYY-MM-DD].md`

Print a summary:
- Campaign name and target roles
- Hypotheses covered
- Variants included
- Proof points available per vertical
- Enrichment columns mapped

Ask: "Does this prompt look right? I'll use it as the instruction set when you run `/cold-email-writer`."

## Example Usage

```
/email-prompt-building real-estate-spain
```

```
/email-prompt-building beauty-italy
```

Then pass the generated prompt file to `/cold-email-writer`:
```
/cold-email-writer --prompt /templates/email-prompt-beauty-italy-2026-03-05.md /output/enriched_leads.csv
```

## Notes

- This is strategy, not execution — take time to get it right before running generation at scale
- If the hypothesis set doesn't exist yet, run `/hypothesis-building [vertical]` first
- The prompt file is version-controlled — keep old versions in `/templates/` for comparison
- For displacement campaigns, always name the competitor explicitly in the prompt — vague "you might be using another tool" framing underperforms
