# LinkedIn Ad Campaign

Create and manage LinkedIn ad campaigns programmatically via the LinkedIn Marketing API. No more fighting the LinkedIn Campaign Manager UI.

## What this skill does

Builds a complete LinkedIn ad campaign (campaign group → campaign → creatives) via API. Useful for creating campaigns at scale, bulk-updating ads, or automating thought leader ad creation from existing content.

## Instructions

1. Ask what type of campaign to create:
   - **Sponsored Content** (single image or carousel)
   - **Thought Leader Ad** (promote a specific LinkedIn post)
   - **Message Ad** (direct to LinkedIn inbox)
2. Gather campaign parameters:
   - Campaign name
   - Objective (BRAND_AWARENESS / WEBSITE_VISITS / LEAD_GENERATION / VIDEO_VIEWS)
   - Daily budget (in USD)
   - Start date and end date (or ongoing)
   - Target audience (industries, job titles, company size, geography)
3. Read `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_AD_ACCOUNT_ID` from CLAUDE.md
4. **Step 1 — Create Campaign Group:**
   - `POST https://api.linkedin.com/v2/adCampaignGroupsV2`
   - Set name, status (ACTIVE), runSchedule (start/end)
5. **Step 2 — Create Campaign under that group:**
   - `POST https://api.linkedin.com/v2/adCampaignsV2`
   - Set targeting: `targetingCriteria` with facets for industries, titles, geo
   - Set budget, bidding strategy (AUTOMATED or CPM/CPC)
6. **Step 3 — Create Ad Creative:**
   - For Thought Leader: use `POST /v2/adCreativesV2` with `type: SPONSORED_UPDATE_V2`
   - For Sponsored Content: upload image first via Assets API, then create creative
   - Attach creative to campaign
7. Print full campaign summary before activating:
   - Campaign name, group, objective
   - Budget and schedule
   - Audience targeting summary
   - Creative preview (text/image)
8. Ask: "Type YES to activate this campaign."
9. On YES: update campaign status to `ACTIVE`
10. Save campaign URN and details to `/output/session_log.md`

## Example Usage

```
/linkedin-ad-campaign
```

Follow the prompts to configure.

## Thought Leader Ad Workflow (from the video)

Most powerful use case: take a high-performing LinkedIn post and run it as a Thought Leader Ad:

1. Provide the LinkedIn post URL
2. The skill extracts the post URN
3. Creates campaign targeting your ICP audience
4. Promotes the post as a sponsored update
5. Scales what's already working organically

## Bulk Update Use Case

To update multiple existing campaigns (e.g. change budget or pause underperformers):
- Ask: "Should I list all active campaigns first?"
- `GET https://api.linkedin.com/v2/adCampaignsV2?q=search&search.status.values=ACTIVE`
- Show list, ask which to update, apply changes in bulk

## Notes

- LinkedIn Marketing API requires OAuth 2.0 — token must have `r_ads`, `w_ads` scopes
- LinkedIn API uses URNs (e.g. `urn:li:organization:123456`) — always store and reuse them
- Daily budgets: minimum $10/day per campaign on LinkedIn
- Campaign Manager UI ≠ API — some features available in UI may not be in API v2
