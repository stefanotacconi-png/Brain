# LinkedIn Engagers

Scrape people who liked or commented on a LinkedIn post, qualify them against your ICP, and create a warm outreach list. Replaces $300+/month scraping tools.

## What this skill does

LinkedIn post engagement = buying intent signal. This skill extracts who engaged with a post, scores them against your ICP, and enriches them for outreach — turning social engagement into pipeline.

## Instructions

1. Ask: "What's the LinkedIn post URL you want to scrape engagements from?"
2. Ask: "Which engagement types? (likes / comments / both)"
3. Use **Apify** LinkedIn scraper to pull engagers:
   - Read `APIFY_API_TOKEN` from CLAUDE.md
   - Actor: `apify/linkedin-post-reactions-scraper` (or equivalent)
   - Input: `{ "postUrl": "<url>", "reactionsType": "all" }`
   - `POST https://api.apify.com/v2/acts/<actor-id>/runs?token=<APIFY_API_TOKEN>`
   - Poll for completion, then fetch results dataset
4. For each engager profile extracted:
   - `first_name`, `last_name`, `title`, `company`, `linkedin_url`
5. Score each engager against ICP (industry, title, company size):
   - Mark as: `qualified` / `maybe` / `skip`
6. For `qualified` profiles, enrich email via Prospeo/Wiza
7. Save to `/output/engagers_[post-slug]_[YYYY-MM-DD].csv`
8. Print summary:
   - Total engagers scraped
   - Qualified / Maybe / Skip counts
   - Emails found
9. Ask: "Should I generate warm outreach copy for the qualified leads?"
   - If yes, use `/cold-email-writer` logic but adapt tone: reference the specific post they engaged with as the personalization hook

## Output CSV Format

- `first_name`, `last_name`, `title`, `company`, `linkedin_url`
- `engagement_type` (liked / commented / shared)
- `qualification_status` (qualified / maybe / skip)
- `email`, `email_status`
- `personalization_hook` (e.g. "Liked your post about AI in sales")

## Example Usage

```
/linkedin-engagers https://www.linkedin.com/posts/example-post-id
```

## Warm Outreach Tip

The personalization hook almost writes itself:
> "Hey [Name], saw you liked [Author]'s post on [Topic] — thought you'd appreciate what we're doing at [Company]..."

This is 10x warmer than cold outreach because they've already signaled interest in the topic.

## Notes

- Only scrape public posts or posts where you have permission
- Apify costs vary by run size — budget accordingly
- Comments contain richer data than likes (capture comment text as extra context)
- You can run this against competitor posts or industry influencer posts for market research
