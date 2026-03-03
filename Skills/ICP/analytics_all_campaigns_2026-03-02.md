# Campaign Analytics Report — 2026-03-02

## Summary Table

| Campaign          | Leads | Sent  | Open%  | Reply% | Bounce% | Interested |
|-------------------|-------|-------|--------|--------|---------|------------|
| ES_Travel         | 1,239 | 2,515 | 29.7%  | 1.4%   | 2.1%    | 9/26       |
| ITA_Travel        | 1,593 | 2,385 | 33.6%  | 1.0%   | 2.9%    | 3/22       |
| ITA_Education     | 1,231 | 2,439 | 33.4%  | 1.6%   | 2.8%    | 5/27       |
| ES_Education ✅   | 1,741 | 3,406 | 36.3%  | 2.1%   | 2.0%    | 15/48      |
| ITA_Fashion       | 1,515 | 2,012 | 33.4%  | 0.8%   | 3.4%    | 2/11       |
| ES_Fashion        |   704 |   973 | 26.6%  | 0.3%   | 2.7%    | 2/6        |
| EN_Fashion_UK     | 1,253 | 1,160 | 39.5%  | 0.2%   | 3.0%    | 0/2        |
| EN_Fashion_NL     |   429 |   903 | 51.8%  | 0.0%   | 2.3%    | 0/0        |
| ITA_Retail ⚠️     | 1,310 | 1,519 | 45.2%  | 0.6%   | 10.0%   | 1/8        |
| Saló Ensenyament  |   170 |   219 | 65.3%  | 0.9%   | 2.3%    | 0/7        |

Benchmarks: Open >30% good | Reply >2% good | Bounce >5% critical

---

## Step Breakdown

### ES_Education — Best Performer ✅
| Step  | Sent  | Replied | Rate  |
|-------|-------|---------|-------|
| E1    | 1,693 | 37      | 2.2%  |
| E2_A  | 505   | 10      | 2.0%  |
| E2_B  | 489   | 1       | 0.2%  |
| E3    | 472   | 8       | 1.7%  |
| E4    | 235   | 5       | 2.1%  |
**Winner: E1 at 2.2%. E2 A/B test: A wins decisively (2.0% vs 0.2%).**

### ITA_Education — Breakup Email Wins
| Step  | Sent  | Replied | Rate  |
|-------|-------|---------|-------|
| E1    | 1,137 | 17      | 1.5%  |
| E2    | 782   | 8       | 1.0%  |
| E3    | 316   | 2       | 0.6%  |
| E4    | 110   | 4       | **3.6%** |
**Breakup email E4 outperforms every other step including E1.**

### ES_Travel — E3 Spike
| Step | Sent | Replied | Rate |
|------|------|---------|------|
| E1   | 1,205| 17      | 1.4% |
| E2   | 800  | 8       | 1.0% |
| E3   | 368  | 8       | **2.2%** |
| E4   | 134  | 1       | 0.7% |
**Unusual: E3 outperforms E1. Worth investigating what E3 subject/angle is.**

### ITA_Retail — Critical Bounce Problem ⚠️
- Bounce rate: **10%** (threshold is 5%)
- E1 alone: 480 sent, 80 bounced = **16.7% bounce on E1_A**
- Root cause: email list quality — enrichment/verification failed for this list
- **Action: pause new launches until list is re-verified**

### EN_Fashion_NL — Open/Reply Paradox 🚨
- Open rate: **51.8%** — highest of all campaigns
- Reply rate: **0%** — zero replies across all 4 steps and 903 emails sent
- Diagnosis: subject lines are working (people open) but copy/offer completely misses
- This is a Netherlands market — offer may not resonate, or language barrier

### EN_Fashion_UK — Same pattern
- Open rate: 39.5% | Reply rate: 0.2% (2 replies from 1,160 emails)
- Possible: English copy is too generic, no local social proof, wrong personas

---

## Key Insights

### 1. Best campaign: ES_Education (2.1% reply rate)
The only campaign hitting the "good" benchmark. Consistent across all 4 steps.
E2_A (no CTA link, pure text) massively outperforms E2_B (with link click): 2.0% vs 0.2%.
**Learning: remove links from follow-up emails. Plain text > linked content.**

### 2. Breakup email (E4) is underused and overperforms
ITA_Education E4: 3.6% — the highest single-step rate across all campaigns.
Most leads still have E4 pending (sequence not fully completed).
**Learning: E4 is not a throwaway. Give it as much craft as E1.**

### 3. Fashion campaigns are broken across the board
- ITA_Fashion: 0.8% reply rate
- ES_Fashion: 0.3%
- EN_Fashion_UK: 0.2%
- EN_Fashion_NL: 0.0%
Open rates are decent (26–51%), so deliverability and subjects work.
The problem is copy-offer fit. Fashion segment may need a completely different angle
(cart abandonment stat or D2C specific proof, not the generic WhatsApp pitch).

### 4. ITA_Retail bounce rate is a deliverability emergency
10% bounce will damage sender domain reputation fast.
- Must re-verify the entire ITA_Retail list before adding more leads
- Check if Prospeo/Wiza enrichment was skipped or failed for this batch

### 5. Travel campaigns are solid but below 2% target
Both IT and ES Travel are in the 1.0–1.4% range. Open rates are good (30–34%).
Copy needs freshening — likely message fatigue after 2+ months running.

### 6. Cold call campaigns (ES + IT) are phone-only — no email data to report.
ES: 22 interested, 108 not interested from 615 leads.
IT: 4 interested, 13 not interested from 848 leads — very low contact rate (54/848 reached).

---

## Actions Required

| Priority | Action | Campaign |
|----------|--------|---------|
| 🚨 URGENT | Re-verify email list before any new launches | ITA_Retail |
| 🚨 URGENT | Rewrite copy — fix offer for NL/UK markets or pause | EN_Fashion_NL, EN_Fashion_UK |
| High | Refresh Fashion copy — new angle needed (cart stat, D2C proof) | ITA_Fashion, ES_Fashion |
| High | Study ES_Education E1 — replicate approach in other ES campaigns | All ES |
| Medium | Remove links from E2 across all campaigns (E2_A won decisively) | All |
| Medium | Strengthen E4 breakup copy — it's the hidden gem | All |
| Low | Investigate why ES_Travel E3 outperforms E1 — steal that angle | ES_Travel |
