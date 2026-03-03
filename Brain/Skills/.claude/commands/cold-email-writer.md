# Cold Email Writer

Generate personalized cold email sequences for each lead using copy frameworks stored in /templates/. No generic copy — every email must reference something specific about the prospect.

## What this skill does

Takes an enriched lead list and generates a complete multi-step email sequence for each contact, using the copy frameworks and tone defined in your templates. Outputs ready-to-upload copy.

## Instructions

1. Accept `$ARGUMENTS` as the path to an enriched leads CSV, or ask which file to use
2. Read copy frameworks from `/templates/copy-frameworks.md`
3. Read any successful email examples from `/templates/email-examples.md` if it exists
4. For each lead in the CSV:
   - Research personalization angles (use their title, company, industry, tier reason)
   - Write **Step 1 (Day 1)**: Opening cold email — hook + value prop + soft CTA
   - Write **Step 2 (Day 3)**: First follow-up — different angle, add social proof
   - Write **Step 3 (Day 7)**: Second follow-up — short, pattern-interrupt, last try
   - Each email: subject line + body (max 5 sentences) + CTA
5. Apply these rules from CLAUDE.md:
   - Subject lines under 8 words
   - First line is hyper-personalized (never generic)
   - One CTA per email
   - No attachments mentioned
6. Save all copy to `/output/campaign_copy_[YYYY-MM-DD].csv` with columns ready for Instantly upload
7. Print 3 example generated emails for review
8. Ask: "Does this copy look right? Should I push this campaign to Lemlist?"

## Output CSV Format (Lemlist-compatible)

Column names match Lemlist's variable naming conventions exactly, so `/push-to-lemlist` can upload without any remapping:
- `email`, `firstName`, `lastName`, `companyName`
- `subject_1`, `body_1`
- `subject_2`, `body_2`
- `subject_3`, `body_3`
- `personalization_note` (what specific detail was used — for your reference, not uploaded)

In email bodies, wrap variable references in `{{double braces}}` — Lemlist resolves these per lead at send time (e.g. `Hi {{firstName}}, noticed {{companyName}} recently...`).

## Example Usage

```
/cold-email-writer /output/enriched_leads.csv
```

## Personalization Sources (in priority order)

1. Recent LinkedIn post or company news (if available)
2. Company tech stack or tools they use
3. Their specific job title + company stage
4. Industry-specific pain point
5. Mutual connection or shared context (if any)

## Notes

- Never use "I hope this finds you well" or similar openers
- If you can't find a genuine personalization angle, flag that lead for manual review
- Adapt tone per ICP: founders = casual/direct; enterprise = more formal
