"""
Write contextual Claude suggestion notes on all 161 stale deals.
Each note is tailored to the deal's specific situation based on:
- Last note content
- Deal amount + close date
- Contact info
- Known blockers or context clues
"""
import json
import time
import re
import requests
from pathlib import Path
from datetime import datetime, timezone

HUBSPOT_TOKEN = "YOUR_HUBSPOT_TOKEN"
BASE_URL = "https://api.hubapi.com"
HEADERS = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}

TODAY = datetime(2026, 3, 4, tzinfo=timezone.utc)
TODAY_STR = "2026-03-04"
NOTE_TIMESTAMP_MS = str(int(TODAY.timestamp() * 1000))

# ---- KNOWN HIGH-VALUE BRANDS (escalate) ----
BIG_BRANDS = [
    "dolce", "gabbana", "mondadori", "arcaplanet", "selex", "cisalfa",
    "mediaworld", "drivalia", "harmont", "blaine", "conbipel", "poltronesof",
    "bosio", "milano ristorazione", "dan john", "fouunderz", "via condotti",
    "athena", "cfi ferrara", "anytime fitness"
]

def is_big_brand(dealname: str) -> bool:
    name_lower = dealname.lower()
    return any(b in name_lower for b in BIG_BRANDS)

def days_overdue(close_date: str) -> int:
    """Returns positive number if overdue, 0 if not."""
    if not close_date:
        return 0
    try:
        cd = datetime.fromisoformat(close_date + "T00:00:00+00:00")
        diff = (TODAY - cd).days
        return max(0, diff)
    except:
        return 0

def days_until_close(close_date: str) -> int:
    """Returns days until close. Negative if overdue."""
    if not close_date:
        return 999
    try:
        cd = datetime.fromisoformat(close_date + "T00:00:00+00:00")
        return (cd - TODAY).days
    except:
        return 999

def detect_context(note_text: str, dealname: str) -> dict:
    """
    Detect specific blockers or signals from the latest note text.
    Returns a dict with detected context keys.
    """
    note_lower = (note_text or "").lower()
    name_lower = dealname.lower()

    ctx = {
        "technical_block": False,
        "meta_bm_issue": False,
        "postponed": False,
        "postponed_month": None,
        "price_issue": False,
        "competitor": False,
        "no_budget": False,
        "death_bereavement": False,
        "legal_review": False,
        "integration_waiting": False,
        "no_crm": False,
        "agency_client": False,
        "seasonal": False,
        "ghosting": False,
        "free_plan": False,
        "outbound_lemlist": False,
        "no_show": False,
        "custom_enterprise": False,
        "uses_competitor": False,
    }

    # Technical issues
    if any(w in note_lower for w in ["business manager", "bm", "waba", "numero", "collegato", "errore", "scollegato", "attivazione numero", "account wa"]):
        ctx["technical_block"] = True
    if any(w in note_lower for w in ["business manager", "bm si", "bm chiedi", "meta bm", "meta ban", "debiti meta"]):
        ctx["meta_bm_issue"] = True

    # Postponed / timing
    postpone_months = {
        "gennaio": "January", "febbraio": "February", "marzo": "March",
        "aprile": "April", "maggio": "May", "giugno": "June",
        "luglio": "July", "agosto": "August", "settembre": "September",
        "ottobre": "October", "novembre": "November", "dicembre": "December",
        "january": "January", "february": "February", "march": "March",
        "april": "April", "may": "May", "june": "June",
        "july": "July", "august": "August", "september": "September",
        "october": "October", "november": "November", "december": "December",
    }
    if any(w in note_lower for w in ["rimandato", "rimandato a", "posticipato", "risentire a", "aspettare", "più avanti", "da ricontattare", "ricontattare a", "partono a"]):
        ctx["postponed"] = True
        for it_month, en_month in postpone_months.items():
            if it_month in note_lower:
                ctx["postponed_month"] = en_month
                break

    # Pricing / budget
    if any(w in note_lower for w in ["troppo caro", "prezzo", "pricing", "budget", "no budget", "non ha budget", "liquidità", "soldi", "caro", "expensive", "too expensive"]):
        ctx["price_issue"] = True
    if any(w in note_lower for w in ["non ha budget", "no budget", "no money", "non hanno soldi"]):
        ctx["no_budget"] = True

    # Competitor
    if any(w in note_lower for w in ["competitor", "concorrente", "charles", "trengo", "brevo", "callbell", "sirena", "respond.io", "manychat", "twilio", "zendesk", "whatsapp api", "360dialog", "wati"]):
        ctx["competitor"] = True
        ctx["uses_competitor"] = True

    # Bereavement / personal
    if any(w in note_lower for w in ["morto", "funerali", "lutto", "bereavement", "passed away"]):
        ctx["death_bereavement"] = True

    # Legal review
    if any(w in note_lower for w in ["legal", "legal review", "compliance", "rgpd", "gdpr", "policy", "safety and policy"]):
        ctx["legal_review"] = True

    # Integration / waiting on their side
    if any(w in note_lower for w in ["integr", "crm integration", "waiting for integration", "shopify", "woocommerce", "prestashop", "klaviyo", "implementare", "still implementing"]):
        ctx["integration_waiting"] = True

    # Agency / partner
    if any(w in note_lower for w in ["agency", "agenzia", "partner", "cliente di ", "for her clients", "per i clienti"]):
        ctx["agency_client"] = True

    # Seasonal / event
    if any(w in note_lower for w in ["olimpiadi", "evento", "stagion", "season", "summer", "estate", "natale", "fiera"]):
        ctx["seasonal"] = True

    # Ghosting
    if any(w in note_lower for w in ["ghosting", "no answer", "no risponde", "non risponde", "email failed", "not answered"]):
        ctx["ghosting"] = True

    # Free plan
    if any(w in note_lower for w in ["free", "piano free", "free plan", "mese gratis", "prova"]):
        ctx["free_plan"] = True

    # Outbound / lemlist
    if "outbound from lemlist" in name_lower or "outbound" in name_lower:
        ctx["outbound_lemlist"] = True

    # No show
    if any(w in note_lower for w in ["no show", "non si è presentat", "non presentato"]):
        ctx["no_show"] = True

    # Enterprise / custom
    if any(w in note_lower for w in ["enterprise", "custom", "personalizzato", "pilota", "pilot", "ramp-up", "168k", "7 country", "multinazionale"]):
        ctx["custom_enterprise"] = True

    return ctx

def generate_suggestion(deal: dict) -> str:
    """Generate a contextual next-action suggestion for a stale deal."""
    dealname = deal.get("dealname", "this deal")
    amount = deal.get("amount", 0)
    close_date = deal.get("close_date", "")
    note_text = deal.get("latest_note_text", "") or ""
    contacts = deal.get("contacts", [])
    hs_next_step = deal.get("hs_next_step", "") or ""

    contact_name = contacts[0]["name"] if contacts else "the contact"
    contact_email = contacts[0]["email"] if contacts else ""

    overdue_days = days_overdue(close_date)
    days_to_close = days_until_close(close_date)
    ctx = detect_context(note_text, dealname)
    big_brand = is_big_brand(dealname)

    # Determine urgency
    if overdue_days > 0 and amount > 5000:
        urgency = "🔴 URGENT"
    elif overdue_days > 0 or (days_to_close <= 14 and amount > 1000):
        urgency = "🟠 HIGH"
    elif amount > 10000:
        urgency = "🟠 HIGH"
    elif days_to_close <= 30:
        urgency = "🟡 MEDIUM"
    else:
        urgency = "⚪ LOW"

    # Build the action line
    lines = []

    # --- SPECIFIC CONTEXT-BASED SUGGESTIONS ---

    if ctx["death_bereavement"]:
        lines.append(f"📋 Suggested action: The contact experienced a bereavement (noted in last activity). Wait at least 3–4 weeks before re-engaging. When reaching out, keep the tone human and acknowledge the time passed. Do not push pricing.")

    elif ctx["custom_enterprise"] and amount > 10000:
        lines.append(f"📋 Suggested action: This is a custom/enterprise deal (€{amount:,.0f}). No rep activity logged. Escalate immediately to a senior rep or management for a personal follow-up. Book a stakeholder meeting — do not delegate to automated sequences.")

    elif big_brand and amount == 0:
        lines.append(f"📋 Suggested action: High-profile brand deal with no amount logged and no rep activity. Identify who owns this deal, confirm it is still active, and log an amount. If stalled, escalate to management for a relationship-based re-engagement.")

    elif big_brand:
        lines.append(f"📋 Suggested action: High-value brand (€{amount:,.0f}). No rep activity logged. Escalate to senior rep this week for a personal follow-up call. These deals require executive-level attention, not a sequence email.")

    elif ctx["postponed"] and ctx["postponed_month"]:
        lines.append(f"📋 Suggested action: Contact asked to be re-engaged in {ctx['postponed_month']} (noted in last activity). Schedule a follow-up task for the first week of {ctx['postponed_month']} — do not contact before then. Confirm the deal amount and close date are updated to reflect the new timeline.")

    elif ctx["postponed"]:
        lines.append(f"📋 Suggested action: Last note indicates the prospect asked to reconnect later. Review the last note to confirm the timing, then schedule a follow-up task for that date. Update the close date to reflect the real expected timeline.")

    elif ctx["meta_bm_issue"] or ctx["technical_block"]:
        lines.append(f"📋 Suggested action: Last note indicates a technical blocker (Meta Business Manager / WhatsApp account setup). Assign a CS/technical specialist to unblock this immediately. Once resolved, re-engage the rep to push toward activation. Do not let this sit — technical issues that go unresolved kill deals.")

    elif ctx["legal_review"]:
        lines.append(f"📋 Suggested action: Prospect is going through a legal or compliance review. Send a brief check-in email asking for an update on timing. Offer to connect your DPO or provide GDPR/compliance documentation to speed up their review. Book a follow-up in 2 weeks if no response.")

    elif ctx["integration_waiting"]:
        lines.append(f"📋 Suggested action: Last note mentions waiting on an integration or CRM setup. Check if Spoki's integration team can help accelerate this. Send a proactive email: 'We have pre-built integrations with [their CRM/ecommerce stack] — can we set up a 20-min call to get this live this week?' ")

    elif ctx["no_budget"]:
        lines.append(f"📋 Suggested action: Last note flags a budget constraint. Try a smaller entry point — offer the Free or Service plan (€349/mo) to get them started, with an upgrade path once they see ROI. Or offer a quarterly payment to reduce upfront commitment.")

    elif ctx["price_issue"] and not ctx["no_budget"]:
        lines.append(f"📋 Suggested action: Pricing was flagged as a concern. Re-open with an ROI-first message: 'For every €1 invested in Spoki, customers generate €23 in revenue on average.' Offer a pilot on the Marketing plan (€599/mo) with a 30-day money-back framing. Avoid discounting — anchor on ROI instead.")

    elif ctx["competitor"]:
        lines.append(f"📋 Suggested action: Last note mentions a competitor. Use the displacement angle: identify which competitor they're evaluating, then send a direct comparison email highlighting Spoki's advantages (official Meta partner, 19 AI features, unlimited operators). Offer a free migration call.")

    elif ctx["ghosting"] or ctx["no_show"]:
        lines.append(f"📋 Suggested action: Contact has gone dark (ghosting or no-show noted). Send one final re-engagement email with a clear subject line (e.g. 'Still interested in WhatsApp automation?') and a low-friction CTA. If no response within 5 business days, disqualify the deal and mark as Closed Lost — freeing up the pipeline.")

    elif ctx["seasonal"]:
        lines.append(f"📋 Suggested action: Last note references a seasonal event or timing dependency. Check whether the event has passed or is upcoming. If the window has closed, re-engage with the next seasonal hook. Update the close date to align with the real timeline.")

    elif ctx["free_plan"]:
        lines.append(f"📋 Suggested action: Contact is on or considering a Free plan. Run an upgrade sequence: show them 1–2 key features they're missing (mass campaigns, AI automation) and quantify the ROI. Offer a 1-month trial on the Marketing plan (€599/mo) to demonstrate value before committing.")

    elif ctx["agency_client"]:
        lines.append(f"📋 Suggested action: This appears to be an agency or partner managing multiple clients. Re-engage with a partner-first pitch: offer agency pricing or a reseller arrangement. Ask which of their clients is the best fit for WhatsApp automation and start there.")

    elif ctx["outbound_lemlist"] and not note_text:
        lines.append(f"📋 Suggested action: This deal originated from a Lemlist cold outreach sequence. No further activity was logged after the initial interest signal. Send a personal follow-up email referencing the original campaign. Qualify their pain point before investing more time.")

    elif overdue_days > 30 and amount == 0:
        lines.append(f"📋 Suggested action: Close date passed {overdue_days} days ago, no amount logged, no activity. Strong candidate for disqualification. Mark as Closed Lost unless a rep can confirm the deal is still alive within 48 hours.")

    elif overdue_days > 0 and amount > 0:
        lines.append(f"📋 Suggested action: Close date passed {overdue_days} days ago (expected close: {close_date}). Call {contact_name} this week to get a clear yes/no. If no answer after 2 attempts, disqualify and move on. Do not leave overdue deals open — they distort the forecast.")

    elif not note_text and amount > 5000:
        lines.append(f"📋 Suggested action: No notes or activity logged on a €{amount:,.0f} deal. This is a significant amount with no rep engagement tracked. Immediately identify which rep owns this, review the deal history, and schedule a check-in call with {contact_name} this week.")

    elif not note_text and amount > 0:
        lines.append(f"📋 Suggested action: No notes or activity logged. Send a brief check-in email to {contact_name}: 'Hi [name], following up on our WhatsApp automation proposal — are you still interested in moving forward? Happy to answer any questions.' If no reply in 5 days, disqualify.")

    elif not note_text and amount == 0:
        lines.append(f"📋 Suggested action: No amount, no notes, no activity. This deal may have been created by mistake or is a test entry. Verify with the deal owner whether this is real pipeline. If not, disqualify and close as Lost.")

    elif days_to_close <= 14 and note_text:
        lines.append(f"📋 Suggested action: Close date in {days_to_close} days. Last note: '{note_text[:100]}...'. Call {contact_name} this week for a closing conversation. Confirm whether they need anything to move forward — proposal, technical setup, pricing clarification.")

    else:
        # Generic — use whatever context we have
        if note_text:
            lines.append(f"📋 Suggested action: No rep activity since last note. Review the context: '{note_text[:150]}'. Schedule a follow-up call or email with {contact_name} to re-qualify and confirm next step. Update hs_next_step in HubSpot after the interaction.")
        else:
            lines.append(f"📋 Suggested action: No activity logged. Send a brief re-engagement email to {contact_name} and log the next step in HubSpot. If no response in 5 business days, consider disqualifying.")

    # Build full note
    amount_str = f"€{amount:,.0f}" if amount > 0 else "no amount logged"
    overdue_str = f" — {overdue_days} days overdue" if overdue_days > 0 else (f" — closes in {days_to_close} days" if days_to_close < 60 else "")
    contact_str = f"{contact_name} ({contact_email})" if contact_email else contact_name

    note = f"""🤖 This note is an automated suggestion from Claude — {TODAY_STR}

{urgency} | Deal value: {amount_str}{overdue_str}
Contact: {contact_str}

{lines[0]}

---
Context: No rep activity or next step has been logged on this deal. This note was generated automatically during a pipeline review of 161 stale deals in the Pricing Discussed stage. The rep who owns this deal should review, take action, and update hs_next_step within 48 hours."""

    return note.strip()


def create_note_on_deal(deal_id: str, note_body: str) -> tuple:
    """Create a note and associate it with the deal."""
    note_payload = {
        "properties": {
            "hs_note_body": note_body,
            "hs_timestamp": NOTE_TIMESTAMP_MS
        }
    }
    resp = requests.post(f"{BASE_URL}/crm/v3/objects/notes", headers=HEADERS, json=note_payload)
    if resp.status_code not in [200, 201]:
        return False, None, resp.status_code, resp.text[:150]

    note_id = resp.json()["id"]
    assoc_url = f"{BASE_URL}/crm/v3/objects/notes/{note_id}/associations/deals/{deal_id}/note_to_deal"
    resp2 = requests.put(assoc_url, headers=HEADERS)
    if resp2.status_code not in [200, 201, 204]:
        return False, note_id, resp2.status_code, resp2.text[:150]

    return True, note_id, resp2.status_code, "OK"


# ---- MAIN ----
print("Loading stale deals...")
with open("output/pricing_discussed_v2_review.json") as f:
    data = json.load(f)

# Include pure stale AND stale+overdue — both need action notes
stale_deals = [r for r in data["results"] if "STALE" in r["classification"]["status"]]
print(f"Found {len(stale_deals)} stale deals to annotate")
print("=" * 60)

results_log = []
success_count = 0
fail_count = 0

for idx, deal in enumerate(stale_deals):
    deal_id = deal["deal_id"]
    dealname = deal["dealname"]
    amount = deal["amount"]

    # Generate tailored suggestion
    note_body = generate_suggestion(deal)

    # Post to HubSpot
    ok, note_id, status_code, msg = create_note_on_deal(deal_id, note_body)

    if ok:
        success_count += 1
        print(f"  ✅ [{idx+1}/{len(stale_deals)}] {dealname[:45]} (€{amount:,.0f})")
    else:
        fail_count += 1
        print(f"  ❌ [{idx+1}/{len(stale_deals)}] {dealname[:45]} — {status_code}: {msg}")

    results_log.append({
        "deal_id": deal_id,
        "dealname": dealname,
        "amount": amount,
        "note_created": ok,
        "note_id": note_id,
        "note_preview": note_body[:200]
    })

    time.sleep(0.35)  # rate limit buffer

print("\n" + "=" * 60)
print(f"✅ Notes created: {success_count}/{len(stale_deals)}")
if fail_count:
    print(f"❌ Failed: {fail_count}")

with open("output/stale_deals_notes_log.json", "w") as f:
    json.dump({"date": TODAY_STR, "total": len(stale_deals), "results": results_log}, f, indent=2)

print(f"Log saved to output/stale_deals_notes_log.json")
