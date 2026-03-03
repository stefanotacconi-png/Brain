# Push to Lemlist

Create a fully configured outbound campaign in Lemlist via API — including leads with personalized variables, email sequence steps, and sending settings. No copy-paste required.

## What this skill does

Takes the campaign copy CSV from /output/ and programmatically creates a complete campaign in Lemlist, including uploading leads and their personalized email steps.

## Authentication

Lemlist uses **Basic Auth** with an empty username and your API key as the password.

```
Authorization: Basic base64(":" + LEMLIST_API_KEY)
```

In Python: `requests.get(url, auth=("", api_key))`
In curl: `--user ":your_api_key"`

Read `LEMLIST_API_KEY` from CLAUDE.md.

Base URL: `https://api.lemlist.com/api`
Rate limit: 20 requests per 2 seconds — add a small delay between batched calls.

## Instructions

1. Accept `$ARGUMENTS` as the campaign name, or ask: "What should this campaign be named?"
2. Ask: "Which copy file should I use?" (default: the most recent `/output/campaign_copy_*.csv`)
3. Read `LEMLIST_API_KEY` from CLAUDE.md

**Step 1 — Create the campaign:**
- `POST /campaigns`
- Body: `{ "name": "<campaign_name>" }`
- Save the returned `_id` as `campaignId` and `sequenceId` — both are needed for subsequent calls

**Step 2 — Add email sequence steps (while campaign is in Draft):**
- `POST /campaigns/{campaignId}/sequences/{sequenceId}/steps`
- Add Step 1 (day 0):
  ```json
  {
    "type": "email",
    "subject": "{{subject_1}}",
    "body": "{{body_1}}",
    "delay": 0
  }
  ```
- Add Step 2 (day 3), Step 3 (day 7) with `"delay": 3` and `"delay": 7` respectively
- Note: steps use `{{variable}}` placeholders — values are supplied per lead at upload time

**Step 3 — Upload leads with personalized variables:**
- `POST /campaigns/{campaignId}/leads`
- Upload one lead at a time (or in batches with delay to respect rate limit)
- Map CSV columns to Lemlist fields:
  ```json
  {
    "email": "lead@company.com",
    "firstName": "John",
    "lastName": "Doe",
    "companyName": "Acme Corp",
    "subject_1": "<personalized subject>",
    "body_1": "<personalized email body>",
    "subject_2": "<follow-up subject>",
    "body_2": "<follow-up body>",
    "subject_3": "<last follow-up subject>",
    "body_3": "<last follow-up body>"
  }
  ```
- Lemlist stores any extra fields as custom variables available in the sequence via `{{fieldName}}`

**Step 4 — Review before launch:**
Print a full summary:
- Campaign name and ID
- Total leads uploaded
- Sequence steps (subject + delay day for each)
- Any leads that failed to upload (with reason)

Ask: "Ready to activate? Type YES to launch the campaign."

**Step 5 — On YES, start the campaign:**
- `POST /campaigns/{campaignId}/start`

Save campaign ID and launch time to `/output/session_log.md`.

## Example Usage

```
/push-to-lemlist "Q1 SaaS Founders Campaign"
```

## Output CSV Format Expected (from /cold-email-writer)

The cold-email-writer skill outputs these columns — they map directly to Lemlist variables:
- `email`, `firstName`, `lastName`, `companyName`
- `subject_1`, `body_1`
- `subject_2`, `body_2`
- `subject_3`, `body_3`

## Safety Rules

- NEVER start the campaign without explicit user "YES" confirmation
- Steps must be added **before** leads are uploaded (Lemlist requirement: campaign must be in Draft state to add steps)
- Respect the 20 req/2s rate limit — add `time.sleep(0.1)` between lead uploads
- If any API call fails, stop and report the error — do not partially upload
- Check that campaign state is `draft` before adding steps; if already active, warn the user

## Notes

- Lemlist supports multichannel sequences (email + LinkedIn) — to add a LinkedIn step, use `"type": "linkedinMessage"` or `"type": "linkedinInvite"` with the same endpoint
- Lemlist's `{{variable}}` system is the same pattern as most sequencers — variable names are case-sensitive
- To add a delay step between emails (without sending): use `"type": "delay"` with `"delay": N`
- Pull campaign analytics later with `/campaign-analytics`
