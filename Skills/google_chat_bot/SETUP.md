# Spoki Brain — Setup Guide

A Google Chat bot that answers GTM questions using the Spoki knowledge base, powered by Claude API.

---

## Prerequisites

- Google Workspace account (admin access not required)
- Anthropic API key (get one at console.anthropic.com)
- ~15 minutes

---

## Step 1 — Create the Apps Script project

1. Go to [script.google.com](https://script.google.com)
2. Click **New project**
3. Rename it to `Spoki Brain`
4. Delete the default `myFunction()` code in `Code.gs`
5. Paste the entire contents of `Code.gs` from this folder
6. Click **Save** (Ctrl+S)

---

## Step 2 — Add your Anthropic API key

1. In the Apps Script editor, click **Project Settings** (gear icon, left sidebar)
2. Scroll down to **Script Properties**
3. Click **Add script property**
4. Name: `ANTHROPIC_API_KEY`
5. Value: your Anthropic API key (starts with `sk-ant-...`)
6. Click **Save script properties**

---

## Step 3 — Deploy as a Web App

1. Click **Deploy** → **New deployment**
2. Click the gear icon next to **Type** → select **Web app**
3. Set:
   - Description: `Spoki Brain v1`
   - Execute as: **Me**
   - Who has access: **Anyone** *(Google Chat needs to reach this URL)*
4. Click **Deploy**
5. **Copy the Web App URL** — you'll need it in Step 5

> If prompted, click **Authorize access** and grant the required permissions.

---

## Step 4 — Enable the Google Chat API

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Select the project linked to your Apps Script (same project ID — find it in Apps Script under Project Settings)
3. Go to **APIs & Services** → **Enabled APIs & services**
4. Click **+ Enable APIs and Services**
5. Search for **Google Chat API** → click **Enable**

---

## Step 5 — Configure the Google Chat App

1. In Google Cloud Console, go to **APIs & Services** → **Google Chat API** → **Configuration**
2. Fill in:
   - **App name:** `Spoki Brain`
   - **Avatar URL:** *(optional — use Spoki logo URL)*
   - **Description:** `GTM assistant for the commercial team`
   - **Functionality:** tick both **Receive 1:1 messages** and **Join spaces and group conversations**
   - **Connection settings:** select **Apps Script** → paste your **Apps Script deployment ID**
     - Find it in Apps Script: Deploy → Manage deployments → copy the Deployment ID
   - **Visibility:** select **Available to specific people and groups in your domain** → add the commercial team emails
3. Click **Save**

---

## Step 6 — Test it

1. Open [chat.google.com](https://chat.google.com)
2. Click **New chat** → search for `Spoki Brain`
3. Send a message, e.g.:
   - `Come pitcho un'agenzia immobiliare che usa già ManyChat?`
   - `Qual è il nostro angolo per battere Brevo?`
   - `Dammi un oggetto email per una beauty clinic in Spagna`

The bot should respond within 3–5 seconds.

---

## Updating the knowledge base

The GTM knowledge base lives inside `Code.gs` as the `SYSTEM_PROMPT` constant. To update it:

1. Open the Apps Script project
2. Edit the `SYSTEM_PROMPT` string
3. Click **Save**
4. Go to **Deploy** → **Manage deployments** → click the pencil icon → **New version** → **Deploy**

No infrastructure restarts needed.

---

## Usage in a shared Space

To add the bot to a shared Google Chat space (e.g. #commercial team):

1. Open the Space
2. Click the space name → **Apps**
3. Search for `Spoki Brain` → **Add**
4. Address the bot with `@Spoki Brain your question here`

> Tip: create a dedicated Space called **Spoki Brain**, add the commercial team, then add the bot — everyone's Q&As are visible and searchable by the whole team.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Bot doesn't respond | Check that the Web App is deployed and the URL is correct in Chat API config |
| `API key non configurata` error | Re-check Script Properties — key name must be exactly `ANTHROPIC_API_KEY` |
| `Errore API` message | Check your Anthropic account has credits and the key is valid |
| Authorization error on deploy | Re-authorize via Deploy → Manage deployments → Authorize |
| Bot responds with empty message | Check Apps Script execution logs: View → Executions |

---

## Cost estimate

- **Google Apps Script:** free (6 min/day execution quota — more than enough for internal use)
- **Claude API:** ~$0.003 per question (claude-sonnet-4-6 pricing) — 1,000 questions ≈ $3
