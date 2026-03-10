// =============================================================================
// Spoki GTM Assistant — Google Chat Bot
// Powered by OpenAI API (GPT-4o) + Google Docs KB + HubSpot live sync
// =============================================================================
//
// SETUP (run once):
//   1. Open Script Properties and add: OPENAI_API_KEY
//   2. Run setupBot() from the Apps Script editor — creates 2 Google Docs + nightly trigger
//   3. Open Script Properties and add: HUBSPOT_API_TOKEN (HubSpot Private App token)
//   4. Run syncHubSpotToDoc() to populate live CRM data immediately
//
// ONGOING:
//   - Edit the Static KB doc directly (link logged by setupBot)
//   - HubSpot sync runs automatically every night at 2am
//   - Redeploy only when changing code logic, never for KB updates
// =============================================================================

const OPENAI_MODEL = 'gpt-4o';

// Script Properties keys
const PROP_OPENAI_KEY     = 'OPENAI_API_KEY';
const PROP_HUBSPOT_TOKEN  = 'HUBSPOT_API_TOKEN';
const PROP_STATIC_DOC_ID  = 'KB_STATIC_DOC_ID';
const PROP_DYNAMIC_DOC_ID = 'KB_DYNAMIC_DOC_ID';

// Cache keys & TTLs
const CACHE_STATIC_KB  = 'KB_STATIC';
const CACHE_DYNAMIC_KB = 'KB_DYNAMIC';
const CACHE_TTL_STATIC  = 21600; // 6 hours
const CACHE_TTL_DYNAMIC = 3600;  // 1 hour

// Closed Won stage IDs across all pipelines
const CLOSED_WON_STAGES = ['2143720639', '986053469', '2201511127', '2318129391', '3675734213', '3689627873', '4430067919'];

// Fixed persona — edit here in code (rarely changes)
const PERSONA = `You are a GTM assistant for Spoki — an expert on our product, ICP, copy strategy, competitive landscape, and outreach playbooks.

Your job is to help commercial team members (SDRs, AEs, BDRs) answer questions about:
- Who to target and why (ICP, personas, industries)
- How to pitch (copy angles, hooks, subject lines, CTAs)
- How to handle objections (competitor comparisons, pricing)
- Which buying signals to look for
- Market-specific strategies (Italy vs Spain)
- CRM-validated learnings from our won deals

Answer in the same language the person writes in (Italian, Spanish, or English).
Be concise, direct, and actionable — like a senior colleague answering a quick question.
Use bullet points when listing options. Keep answers under 200 words unless the question genuinely needs more detail.`;

// ---------------------------------------------------------------------------
// Knowledge base — fetch from Google Docs with cache
// ---------------------------------------------------------------------------

function getStaticKB() {
  const cache = CacheService.getScriptCache();
  const cached = cache.get(CACHE_STATIC_KB);
  if (cached) return cached;

  const docId = PropertiesService.getScriptProperties().getProperty(PROP_STATIC_DOC_ID);
  if (!docId) return '[Static KB not configured — run setupBot()]';

  try {
    const content = DocumentApp.openById(docId).getBody().getText();
    cache.put(CACHE_STATIC_KB, content, CACHE_TTL_STATIC);
    return content;
  } catch (e) {
    Logger.log('Error fetching static KB: ' + e);
    return '[Static KB fetch error: ' + e + ']';
  }
}

function getDynamicKB() {
  const cache = CacheService.getScriptCache();
  const cached = cache.get(CACHE_DYNAMIC_KB);
  if (cached) return cached;

  const docId = PropertiesService.getScriptProperties().getProperty(PROP_DYNAMIC_DOC_ID);
  if (!docId) return '';

  try {
    const content = DocumentApp.openById(docId).getBody().getText();
    cache.put(CACHE_DYNAMIC_KB, content, CACHE_TTL_DYNAMIC);
    return content;
  } catch (e) {
    Logger.log('Error fetching dynamic KB: ' + e);
    return '';
  }
}

function buildSystemPrompt() {
  const staticKB  = getStaticKB();
  const dynamicKB = getDynamicKB();
  let prompt = PERSONA + '\n\n---\n\n' + staticKB;
  if (dynamicKB) prompt += '\n\n---\n\n' + dynamicKB;
  return prompt;
}

// ---------------------------------------------------------------------------
// HubSpot sync — runs nightly, writes to Dynamic KB doc
// ---------------------------------------------------------------------------

function syncHubSpotToDoc() {
  const token = PropertiesService.getScriptProperties().getProperty(PROP_HUBSPOT_TOKEN);
  const docId = PropertiesService.getScriptProperties().getProperty(PROP_DYNAMIC_DOC_ID);

  if (!token) { Logger.log('HUBSPOT_API_TOKEN not set in Script Properties.'); return; }
  if (!docId)  { Logger.log('KB_DYNAMIC_DOC_ID not set. Run setupBot() first.');  return; }

  Logger.log('Starting HubSpot sync...');

  // 90-day cutoff
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 90);

  const deals = fetchAllWonDeals(token, cutoff.getTime());
  Logger.log('Fetched ' + deals.length + ' won deals from last 90 days');

  // Aggregate by industry
  const byIndustry = {};
  let totalRevenue = 0;

  deals.forEach(deal => {
    const industry = (deal.properties.industry || 'Unknown').trim();
    const amount   = parseFloat(deal.properties.amount)      || 0;
    const days     = parseInt(deal.properties.days_to_close) || 0;

    if (!byIndustry[industry]) byIndustry[industry] = { count: 0, revenue: 0, totalDays: 0 };
    byIndustry[industry].count++;
    byIndustry[industry].revenue    += amount;
    byIndustry[industry].totalDays  += days;
    totalRevenue += amount;
  });

  // Sort by count, take top 15 known industries
  const sortedIndustries = Object.entries(byIndustry)
    .filter(([k]) => k !== 'Unknown' && k !== '')
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 15);

  // Top 10 deals by value
  const topDeals = [...deals]
    .sort((a, b) => parseFloat(b.properties.amount || 0) - parseFloat(a.properties.amount || 0))
    .slice(0, 10);

  // Build content
  const dateStr = Utilities.formatDate(new Date(), 'Europe/Rome', 'yyyy-MM-dd HH:mm');

  let content = `## CRM Live Data — Auto-updated: ${dateStr}\n`;
  content += `> Auto-generated from HubSpot. Do not edit manually — changes are overwritten nightly.\n\n`;

  content += `### Won Deals Summary (Last 90 Days)\n`;
  content += `Total: ${deals.length} deals · €${Math.round(totalRevenue).toLocaleString('it-IT')} revenue\n\n`;

  content += `### Won Deals by Industry\n`;
  sortedIndustries.forEach(([industry, s]) => {
    const avgAmount = s.count ? Math.round(s.revenue / s.count) : 0;
    const avgDays   = s.count ? Math.round(s.totalDays / s.count) : 0;
    content += `- ${industry}: ${s.count} deals · avg €${avgAmount.toLocaleString('it-IT')} · avg ${avgDays} days to close\n`;
  });

  content += `\n### Top 10 Deals by Value (Last 90 Days)\n`;
  topDeals.forEach(deal => {
    const name     = deal.properties.dealname    || 'Unknown';
    const amount   = parseFloat(deal.properties.amount || 0);
    const industry = deal.properties.industry    || '—';
    const days     = deal.properties.days_to_close || '0';
    const date     = deal.properties.closedate ? deal.properties.closedate.substring(0, 10) : '—';
    content += `- ${name} — €${amount.toLocaleString('it-IT')} · ${industry} · ${days}d to close · ${date}\n`;
  });

  // Write to doc (overwrites entirely)
  const body = DocumentApp.openById(docId).getBody();
  body.clear();
  body.appendParagraph(content);

  // Invalidate cache so next message gets fresh data
  CacheService.getScriptCache().remove(CACHE_DYNAMIC_KB);

  Logger.log('HubSpot sync complete.');
}

function fetchAllWonDeals(token, cutoffMs) {
  const url    = 'https://api.hubapi.com/crm/v3/objects/deals/search';
  const deals  = [];
  let after    = undefined;

  do {
    const body = {
      filterGroups: [{
        filters: [
          { propertyName: 'dealstage',  operator: 'IN',  values: CLOSED_WON_STAGES },
          { propertyName: 'closedate',  operator: 'GTE', value: cutoffMs.toString() }
        ]
      }],
      properties: ['dealname', 'amount', 'closedate', 'days_to_close', 'industry'],
      sorts: [{ propertyName: 'closedate', direction: 'DESCENDING' }],
      limit: 100
    };
    if (after) body.after = after;

    const resp = UrlFetchApp.fetch(url, {
      method: 'post',
      contentType: 'application/json',
      headers: { 'Authorization': 'Bearer ' + token },
      payload: JSON.stringify(body),
      muteHttpExceptions: true
    });

    const data = JSON.parse(resp.getContentText());
    if (data.results) deals.push(...data.results);
    after = data.paging && data.paging.next ? data.paging.next.after : undefined;

    if (deals.length >= 3000) break; // safety cap
  } while (after);

  return deals;
}

// ---------------------------------------------------------------------------
// Apps Script Chat integration handlers
// ---------------------------------------------------------------------------

function onMessage(event) {
  try {
    // Chat Add-on format: event.chat.messagePayload.message.text
    const msg = event && event.chat && event.chat.messagePayload && event.chat.messagePayload.message;
    const userMessage = msg ? (msg.text || msg.argumentText || '') : '';
    const cleanMessage = userMessage.replace(/<[^>]+>/g, '').trim();
    const answer = callOpenAI(cleanMessage);
    return {
      hostAppDataAction: {
        chatDataAction: {
          createMessageAction: {
            message: { text: answer }
          }
        }
      }
    };
  } catch (err) {
    Logger.log('Error in onMessage: ' + err.toString());
    return {
      hostAppDataAction: {
        chatDataAction: {
          createMessageAction: {
            message: { text: '⚠️ Errore interno. Riprova tra un momento.' }
          }
        }
      }
    };
  }
}

function onAddToSpace(event) {
  return {
    hostAppDataAction: {
      chatDataAction: {
        createMessageAction: {
          message: {
            text: '🧠 Benvenuto in Spoki Brain!\n\n' +
              'Sono il tuo assistente GTM. Chiedimi qualsiasi cosa su:\n' +
              '• ICP e industrie target\n' +
              '• Personas e strategie di approccio\n' +
              '• Copy, oggetti email e CTA\n' +
              '• Competitor e come batterli\n' +
              '• Pricing e obiezioni\n' +
              '• Segnali di acquisto e scoring\n\n' +
              'Rispondo in italiano, spagnolo o inglese 🚀'
          }
        }
      }
    }
  };
}

function onRemoveFromSpace(event) {
  // Nothing to do
}

// ---------------------------------------------------------------------------
// OpenAI API call
// ---------------------------------------------------------------------------

function callOpenAI(userMessage) {
  const apiKey = PropertiesService.getScriptProperties().getProperty(PROP_OPENAI_KEY);

  if (!apiKey) {
    return '⚠️ API key non configurata. Aggiungi OPENAI_API_KEY nelle Proprietà script.';
  }

  const payload = {
    model: OPENAI_MODEL,
    max_tokens: 1024,
    messages: [
      { role: 'system', content: buildSystemPrompt() },
      { role: 'user',   content: userMessage }
    ]
  };

  try {
    const response = UrlFetchApp.fetch('https://api.openai.com/v1/chat/completions', {
      method: 'post',
      contentType: 'application/json',
      headers: { 'Authorization': 'Bearer ' + apiKey },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });

    const data = JSON.parse(response.getContentText());

    if (data.choices && data.choices[0] && data.choices[0].message) {
      return data.choices[0].message.content;
    }
    if (data.error) {
      Logger.log('OpenAI error: ' + JSON.stringify(data.error));
      return '⚠️ Errore API: ' + data.error.message;
    }
    return '⚠️ Risposta non valida da OpenAI. Riprova.';

  } catch (err) {
    Logger.log('Fetch error: ' + err.toString());
    return '⚠️ Impossibile contattare OpenAI. Controlla la connessione o la API key.';
  }
}

// ---------------------------------------------------------------------------
// One-time setup — run once from the Apps Script editor
// ---------------------------------------------------------------------------

function setupBot() {
  const props = PropertiesService.getScriptProperties();

  // 1. Create Static KB Google Doc (seed with current knowledge base)
  Logger.log('Creating Static KB doc...');
  const staticDoc  = DocumentApp.create('Spoki Brain — Static Knowledge Base');
  staticDoc.getBody().clear();
  staticDoc.getBody().appendParagraph(STATIC_KB_SEED);
  staticDoc.saveAndClose();
  props.setProperty(PROP_STATIC_DOC_ID, staticDoc.getId());

  // 2. Create Dynamic KB Google Doc (auto-overwritten by HubSpot sync)
  Logger.log('Creating Dynamic KB doc...');
  const dynamicDoc = DocumentApp.create('Spoki Brain — CRM Live Data (auto-updated)');
  dynamicDoc.getBody().clear();
  dynamicDoc.getBody().appendParagraph(
    'CRM Live Data\n\nNot yet synced. Add HUBSPOT_API_TOKEN to Script Properties, then run syncHubSpotToDoc().'
  );
  dynamicDoc.saveAndClose();
  props.setProperty(PROP_DYNAMIC_DOC_ID, dynamicDoc.getId());

  // 3. Set up nightly trigger (2am Rome time)
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'syncHubSpotToDoc')
    .forEach(t => ScriptApp.deleteTrigger(t));

  ScriptApp.newTrigger('syncHubSpotToDoc')
    .timeBased()
    .everyDays(1)
    .atHour(2)
    .inTimezone('Europe/Rome')
    .create();

  Logger.log('=== SETUP COMPLETE ===');
  Logger.log('Static KB:  https://docs.google.com/document/d/' + staticDoc.getId());
  Logger.log('Dynamic KB: https://docs.google.com/document/d/' + dynamicDoc.getId());
  Logger.log('Next steps:');
  Logger.log('  1. Add HUBSPOT_API_TOKEN to Script Properties');
  Logger.log('  2. Run syncHubSpotToDoc() to populate live CRM data');
  Logger.log('  3. Share the Static KB doc with your team for editing');
}

// ---------------------------------------------------------------------------
// Static KB seed content — populates the Google Doc on first setup.
// After that, edit the Google Doc directly. This constant is only used once.
// ---------------------------------------------------------------------------

const STATIC_KB_SEED = `## What We Sell

Spoki is the Customer Engagement Management (CEM) platform that turns WhatsApp into a powerful channel for marketing, sales, and customer support. Official Meta Business Partner.

We help B2C/D2C businesses automate: lead response, appointment reminders, customer support, upsell flows, and post-purchase communication via WhatsApp — reducing manual work, cutting no-show rates by 20–40%, and automating 50%+ of repetitive support queries.

Tagline: "The future is conversational on WhatsApp"
Company: NextAI Srl — founded 2021, HQ Brindisi (Italy), second office in Barcelona. CEO: Giorgio Pagliara. CMO: Mattia Pace. Team: 60+.
Scale: 20,000+ customers · 60M+ messages sent · 4,000+ integrations · 23x documented ROI

---

## ICP

- B2C or D2C businesses with a direct consumer relationship
- 10–500 employees (SME to mid-market)
- Revenue: €1M–€50M
- Geography: Italy and Spain primary; broader Southern Europe secondary
- Exclude: pure B2B, pure SaaS, public sector

---

## Target Industries (CRM-validated, priority order)

1. Beauty / Wellness — clinics, salons, aesthetic centres, spas (top volume, fast close)
2. Real Estate — agencies, developers, franchises (Tempocasa €21.6k, fast close outbound)
3. Fashion / Apparel — D2C, ecommerce, retail chains (Nuna Lie, Caleffi, Il Lenzuolo)
4. Travel / Hospitality — hotels, travel agencies, tour operators (Gattinoni €18.6k)
5. Education — language schools, academies, e-learning (MLA World, Pegaso — large deals)
6. Pet retail / D2C — SURPRISE winner (Zampa: 6-day close, ~€40k from 3 wins)
7. Electronics / Consumer retail (Expert Mallardo, Electrolux)
8. Home / Furniture — interior design, D2C textiles (Caleffi, Il Lenzuolo)
9. Healthcare — private clinics, diagnostic centres (hypothesis, strong pain fit)
10. Automotive — dealerships, service centres (hypothesis)
11. Finance / Insurance — brokers, insurers (hypothesis)

---

## Buyer Personas

Decision makers (sign the deal):
- CEO / Founder / Amministratore Delegato — go direct at SMEs (<50 employees)
- CMO / Marketing & Communication Director — key for B2C brands with comms budget
- General Manager / Country Manager — multi-location or international businesses

Internal champions (find the product, push the deal):
- CRM Manager / CRM Specialist — most frequent champion in won deals
- Senior Ecommerce Manager / Digital Marketing Manager — D2C, fashion, home
- Social Media Manager — entry point only, too junior to sign; use to escalate

Sales-oriented roles (Real Estate, Automotive, Finance):
- Sales Director / Head of Sales / Responsabile Commerciale

Strategy:
- SME (<50 employees): go direct to CEO/Founder
- Mid-market: target CRM Manager or Ecommerce Manager as champion + CC their CMO

---

## Industry Pain → Solution Map

Beauty: No-shows + slow ad lead response → "Reduce no-shows 20–40% + auto-respond to ad leads in seconds"
Healthcare: Saturated phone lines + patients forget prep → "Automate 50%+ of repetitive queries + pre-exam prep flows"
Real Estate: Portal leads go cold in minutes → "Instant WhatsApp reply to portal leads before competitors do"
Automotive: Slow follow-up on portal leads + manual service reminders → "Qualify leads instantly + automate service/ITV reminders"
Education: No-shows for open days + support overload at peaks → "Cut open day no-shows + automate FAQ during admissions"
Travel/Hospitality: Booking drop-offs + missed upsell at pre-arrival → "Recover bookings + automate spa/upgrade upsells before arrival"
Fashion: Cart abandonment + low email return → "Recover carts via WA 10–30% better than email"
Finance/Insurance: Policy renewal churn + KYC friction → "Automate renewal reminders + frictionless doc collection"
Events: Attendees ignore email reminders → "90%+ open rate on WA vs 20% on email for event reminders"
Home: Warm leads go cold between website and showroom → "Instant WA follow-up on Meta Ads leads → showroom booking"
Pet: High volume of customer queries + order updates → "Automate order status, appointment booking, and FAQs via WhatsApp"
Electronics: Post-purchase support overload → "Deflect 50%+ of support queries via WhatsApp self-service flows"

---

## Buying Signals (prioritise in this order)

1. TOP — Currently using a WhatsApp tool (Charles, Zendesk WA, ManyChat, Twilio, Respond.io) → already has budget + proven need → pitch switching. Always reference the competitor by name in the first email line.
2. HIGH — Running Meta or Google Ads but no WhatsApp follow-up automation → clear gap, easy ROI story
3. HIGH — Hiring customer service agents or marketing coordinators → pain is growing, budget exists
4. MEDIUM — Using legacy tools (SMS, email newsletters) → education-first pitch
5. MEDIUM — Recently opened new locations or expanding nationally → scaling pain
6. LOW — No WhatsApp Business at all → education-first, longer cycle

---

## Scoring Tiers

Tier 1 — Perfect fit: target industry + right size + Marketing or CS persona reachable. Prioritize immediately.
Tier 2 — Strong fit: industry match + slightly outside size range, or secondary persona. Worth targeting.
Tier 3 — Weak fit: industry is a stretch or company too small/large. Low priority.
Disqualified — B2B-only, pure SaaS, public sector, non-commercial organisations.

---

## Competitive Landscape

### Primary competitors

Italy: Brevo, Callbell, Growy, Charles, Trengo
Spain: Sirena.app, Leadsales, B2Chat, Clientify
Global: Twilio, Sinch, Infobip, 360dialog, WATI, Sleekflow, Respond.io, Bird, Gupshup, Interakt

### Displacement angles

Charles: Enterprise-focused, higher price → "Simpler onboarding, better SME pricing"
Zendesk WA: Complex ticketing overhead → "Lighter, more automation-native"
ManyChat: Limited WA features, mainly Meta → "Full WA Business API, richer flows"
Twilio: Dev-heavy, needs custom build → "No-code/low-code, faster time to value"
Respond.io: Broad multi-channel, less WA-native → "WA-first depth, easier onboarding"
Brevo: Email-first, WA is secondary → "WA-native, 19 AI features built-in"
Trengo: Multi-channel inbox, not WA-specialist → "WA-first depth, unlimited operators included"

### Our key differentiators

- Official Meta Business Partner — zero ban risk (competitors on unofficial APIs risk account suspension)
- 19 AI features natively integrated at no extra cost
- Unlimited operators + automations + integrations in all plans
- Dual platform: WhatsApp App and API simultaneously
- Multichannel: WhatsApp + SMS + Voice AI + Email + RCS + Instagram + TikTok
- Free plan available (competitors often start paid)
- Documented 23x ROI

---

## Pricing

Free: €0/mo — customer request handling
Service: €349/mo — AI-powered customer support automation
Marketing: €599/mo — marketing campaigns + revenue growth (RECOMMENDED)
Sales: €749/mo — sales and payments on WhatsApp

All plans: unlimited operators, automations, integrations, AI.
Discounts: -10% quarterly, -20% annual.

---

## Key Metrics & Social Proof

WhatsApp open rate: 98% vs 10% email (use "98% vs 10%" in copy — NOT 20%)
WhatsApp interaction rate: 20% vs 1.5% email
ROI: 23x (€23 revenue per €1 invested)
Customers: 20,000+
Messages sent: 60M+
Cart recovery: 25–35% via WhatsApp reminders
No-show reduction: 60% (Beauty/appointments)
Support queries automated: 60–70%
Upsell revenue increase: +40%
Lead gen from Click-to-WA ads: 60% conversion

Notable clients: Feltrinelli, UniPegaso, Cofidis, Skon Cosmetics, Zuiki, Reental, Tuacar (Automotive)

---

## Communication Angles

"Emails have a 10% open rate. WhatsApp has 98%. The future is not an email."
"CRMs are built for data. Spoki is built for conversations."
"The smartest member of your team is ready to work. 24/7."
"For every euro invested in Spoki, our customers generate €23 in revenue."
"Spoki is an official Meta Tech Partner. Zero risk of bans."
"Stop losing 70% of carts. Recover sales on WhatsApp."

---

## Copy Principles

- Subject lines: under 8 words
- First line: hyper-personalized — reference their industry + specific pain
- Body: 3–5 sentences max
- CTA: one per email — always low-friction (15-min call, not a demo)
- No attachments in cold outreach
- Tie pain to a concrete business cost (lost revenue, wasted staff time, no-show rate)
- Industry-specific language: "no-show rate" for Beauty/Healthcare, "lead response time" for Real Estate/Automotive, "cart abandonment" for Fashion/Electronics
- Email open rate in copy: 10% (NOT 20%) — "98% vs 10%"

---

## CRM-Validated Learnings

Proven outbound channels:
- Lemlist → Spain already producing wins (Albali Centros de Formación closed from a sequence)
- Meeting links drive largest deals (Gattinoni €18.6k, Tempocasa €21.6k via calendar booking)
- Paid Search (Google, brand + WhatsApp keywords in Italian) drives fast inbound closes

Time to close:
- SME inbound (self-serve): 0–3 days
- SME inbound with demo: 6–36 days
- Outbound SME: 6–30 days
- Enterprise: 60–240 days

Spain: Real Estate (Tempocasa, Percent), Education (Albali, MLA World), Pet (Zampa), Beauty are working. Use Spanish-language sequences.
Italy: Fashion/Apparel (Nuna Lie, Caleffi), Travel (Gattinoni), Education (Pegaso), Beauty/Wellness (EtnaWellness), Electronics (Expert Mallardo) all proven.
Pet industry surprise: 3 wins ~€40k total. Fast close (Zampa: 6 days). Pain: high volume of queries, appointment booking, order updates.`;
