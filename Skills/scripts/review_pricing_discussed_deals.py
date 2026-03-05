"""
Review all open deals in 'Pricing Discussed' (old Follow up) stage.
For each deal: pull notes, latest engagements, associated contacts.
Output structured analysis for stage reclassification.
"""
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timezone

HUBSPOT_TOKEN = "YOUR_HUBSPOT_TOKEN"
BASE_URL = "https://api.hubapi.com"
HEADERS = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}

PRICING_DISCUSSED_STAGE = "986053468"
SALES_PIPELINE = "671838099"

OUTPUT_FILE = Path("output/pricing_discussed_deals_review.json")
REPORT_FILE = Path("output/pricing_discussed_stage_review.md")

# Load Fathom call data for cross-reference
FATHOM_EMAIL_MAP = {}
email_map_file = Path("output/all_contact_emails.json")
if email_map_file.exists():
    with open(email_map_file) as f:
        data = json.load(f)
        FATHOM_EMAIL_MAP = data.get("email_map", {})

def get_deal_notes(deal_id: str) -> list:
    """Get all notes associated with a deal via engagements API."""
    url = f"{BASE_URL}/crm/v3/objects/deals/{deal_id}/associations/notes"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return []
    note_ids = [r["id"] for r in resp.json().get("results", [])]
    notes = []
    for nid in note_ids[:5]:  # cap at 5 most recent notes
        resp2 = requests.get(
            f"{BASE_URL}/crm/v3/objects/notes/{nid}",
            headers=HEADERS,
            params={"properties": "hs_note_body,hs_timestamp,hubspot_owner_id"}
        )
        if resp2.status_code == 200:
            notes.append(resp2.json())
        time.sleep(0.05)
    # Sort by timestamp desc
    notes.sort(key=lambda x: x.get("properties", {}).get("hs_timestamp", ""), reverse=True)
    return notes

def get_deal_emails(deal_id: str) -> list:
    """Get recent emails associated with a deal."""
    url = f"{BASE_URL}/crm/v3/objects/deals/{deal_id}/associations/emails"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return []
    email_ids = [r["id"] for r in resp.json().get("results", [])]
    emails = []
    for eid in email_ids[:3]:  # cap at 3
        resp2 = requests.get(
            f"{BASE_URL}/crm/v3/objects/emails/{eid}",
            headers=HEADERS,
            params={"properties": "hs_email_subject,hs_email_direction,hs_email_status,hs_timestamp,hs_email_text"}
        )
        if resp2.status_code == 200:
            emails.append(resp2.json())
        time.sleep(0.05)
    emails.sort(key=lambda x: x.get("properties", {}).get("hs_timestamp", ""), reverse=True)
    return emails

def get_deal_calls(deal_id: str) -> list:
    """Get recent calls associated with a deal."""
    url = f"{BASE_URL}/crm/v3/objects/deals/{deal_id}/associations/calls"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return []
    call_ids = [r["id"] for r in resp.json().get("results", [])]
    calls = []
    for cid in call_ids[:3]:
        resp2 = requests.get(
            f"{BASE_URL}/crm/v3/objects/calls/{cid}",
            headers=HEADERS,
            params={"properties": "hs_call_title,hs_call_body,hs_timestamp,hs_call_status,hs_call_direction"}
        )
        if resp2.status_code == 200:
            calls.append(resp2.json())
        time.sleep(0.05)
    calls.sort(key=lambda x: x.get("properties", {}).get("hs_timestamp", ""), reverse=True)
    return calls

def get_deal_contacts(deal_id: str) -> list:
    """Get contacts associated with a deal."""
    url = f"{BASE_URL}/crm/v3/objects/deals/{deal_id}/associations/contacts"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return []
    contact_ids = [r["id"] for r in resp.json().get("results", [])]
    contacts = []
    for cid in contact_ids[:3]:
        resp2 = requests.get(
            f"{BASE_URL}/crm/v3/objects/contacts/{cid}",
            headers=HEADERS,
            params={"properties": "email,firstname,lastname,company,lifecyclestage"}
        )
        if resp2.status_code == 200:
            contacts.append(resp2.json())
        time.sleep(0.05)
    return contacts

def get_all_open_pricing_discussed_deals() -> list:
    """Get all open deals in Pricing Discussed stage."""
    all_deals = []
    after = None
    while True:
        payload = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "pipeline", "operator": "EQ", "value": SALES_PIPELINE},
                    {"propertyName": "dealstage", "operator": "EQ", "value": PRICING_DISCUSSED_STAGE},
                    {"propertyName": "hs_is_closed", "operator": "EQ", "value": "false"}
                ]
            }],
            "properties": [
                "dealname", "dealstage", "amount", "closedate", "pipeline",
                "createdate", "hubspot_owner_id", "hs_lastmodifieddate",
                "notes_last_updated", "num_associated_contacts", "hs_next_step",
                "hs_deal_stage_probability"
            ],
            "limit": 100,
            "sorts": [{"propertyName": "amount", "direction": "DESCENDING"}]
        }
        if after:
            payload["after"] = after
        resp = requests.post(
            f"{BASE_URL}/crm/v3/objects/deals/search",
            headers=HEADERS,
            json=payload
        )
        if resp.status_code != 200:
            print(f"Error: {resp.status_code} {resp.text[:200]}")
            break
        data = resp.json()
        all_deals.extend(data.get("results", []))
        paging = data.get("paging", {})
        after = paging.get("next", {}).get("after")
        if not after:
            break
        time.sleep(0.2)
    return all_deals

def classify_deal(deal: dict, contacts: list, notes: list, emails: list, calls: list) -> dict:
    """
    Classify a deal into the new stage based on all available signals.
    Returns: stage_recommendation, confidence, reasoning
    """
    props = deal["properties"]
    next_step = (props.get("hs_next_step") or "").strip()
    amount = float(props.get("amount") or 0)
    close_date_str = props.get("closedate", "") or ""
    close_date = close_date_str[:10] if close_date_str else "N/A"

    # Collect all text signals
    note_texts = " | ".join([
        n.get("properties", {}).get("hs_note_body", "") or ""
        for n in notes
    ]).lower()
    email_subjects = " | ".join([
        e.get("properties", {}).get("hs_email_subject", "") or ""
        for e in emails
    ]).lower()
    call_texts = " | ".join([
        c.get("properties", {}).get("hs_call_body", "") or ""
        for c in calls
    ]).lower()
    all_signals = (next_step + " " + note_texts + " " + email_subjects + " " + call_texts).lower()

    # Contact emails for Fathom cross-ref
    contact_emails = [c.get("properties", {}).get("email", "").lower() for c in contacts]
    fathom_calls_found = any(e in FATHOM_EMAIL_MAP for e in contact_emails)

    # --- CLASSIFICATION LOGIC ---

    # Strong signals → Negotiation / Trial Activation (70%)
    negotiation_signals = [
        "onboarding call", "onboarding", "deve pagare", "pagare",
        "they should buy", "activation", "attivazione", "contratto",
        "ha confermato", "confirmed", "trial running", "trial attivo",
        "ready to sign", "pronto a firmare", "pagamento", "invoice sent",
        "fattura inviata", "stanno attivando"
    ]
    for sig in negotiation_signals:
        if sig in all_signals:
            return {
                "recommended_stage": "Negotiation / Trial Activation",
                "stage_id": "2674750700",
                "probability": "70%",
                "confidence": "HIGH",
                "trigger": sig,
                "reasoning": f"Signal '{sig}' found in notes/next_step — confirmed intent or payment imminent"
            }

    # Strong signals → Back to Demo (30%)
    back_to_demo_signals = [
        "demo", "to present proposal", "presentare proposta",
        "show the product", "call to show", "rifare demo",
        "fare demo", "ancora da presentare", "non ha visto il prodotto"
    ]
    # Only move back if it's clearly pre-pricing (not "post-demo issues")
    back_to_demo_exceptions = ["after demo", "dopo demo", "post demo", "follow up demo"]
    for sig in back_to_demo_signals:
        if sig in all_signals and not any(exc in all_signals for exc in back_to_demo_exceptions):
            return {
                "recommended_stage": "Demo",
                "stage_id": "986053467",
                "probability": "30%",
                "confidence": "HIGH",
                "trigger": sig,
                "reasoning": f"Signal '{sig}' — pricing hasn't been discussed yet, deal should be in Demo"
            }

    # At Risk signals — keep in Pricing Discussed but flag
    at_risk_signals = [
        "at risk", "no answer", "ghosting", "no show", "no decision maker",
        "not a decision maker", "rischio", "rimandite", "rimandato",
        "no se decide", "stall", "stalling"
    ]
    for sig in at_risk_signals:
        if sig in all_signals:
            return {
                "recommended_stage": "Pricing Discussed",
                "stage_id": "986053468",
                "probability": "40%",
                "confidence": "HIGH",
                "trigger": sig,
                "reasoning": f"AT RISK: '{sig}' — keep in Pricing Discussed but needs immediate rep action"
            }

    # Decision signals — leaning toward Negotiation
    decision_signals = [
        "decision call", "decision meeting", "meeting to make", "decide",
        "decisione", "decide today", "decide this week", "chiude",
        "chiusura", "negotiation", "negoziazione", "closing call"
    ]
    for sig in decision_signals:
        if sig in all_signals:
            return {
                "recommended_stage": "Negotiation / Trial Activation",
                "stage_id": "2674750700",
                "probability": "70%",
                "confidence": "MEDIUM",
                "trigger": sig,
                "reasoning": f"Decision signal '{sig}' — move to Negotiation pending final yes/no"
            }

    # Stale / no signal — assess by age and close date
    notes_updated = props.get("notes_last_updated") or ""
    today = datetime(2026, 3, 4, tzinfo=timezone.utc)
    days_since_note = 999
    if notes_updated:
        try:
            last_note_dt = datetime.fromisoformat(notes_updated.replace("Z", "+00:00"))
            days_since_note = (today - last_note_dt).days
        except:
            pass

    if days_since_note > 14:
        return {
            "recommended_stage": "Pricing Discussed",
            "stage_id": "986053468",
            "probability": "40%",
            "confidence": "LOW",
            "trigger": "stale",
            "reasoning": f"No activity in {days_since_note} days — stale deal, needs rep check-in or disqualification"
        }

    # Default: stays in Pricing Discussed
    return {
        "recommended_stage": "Pricing Discussed",
        "stage_id": "986053468",
        "probability": "40%",
        "confidence": "MEDIUM",
        "trigger": "default",
        "reasoning": "Pricing shared, waiting for prospect decision — correctly placed in Pricing Discussed"
    }

# ---- MAIN ----
print("Fetching all open Pricing Discussed deals...")
deals = get_all_open_pricing_discussed_deals()
print(f"Found {len(deals)} deals")

# Sort by amount desc (highest value first)
deals.sort(key=lambda d: float(d["properties"].get("amount") or 0), reverse=True)

results = []
march_forecast = {"negotiation": 0, "pricing_discussed": 0, "back_to_demo": 0, "at_risk": 0}
deals_closing_march = []

print(f"\nAnalyzing {len(deals)} deals...")
for idx, deal in enumerate(deals):
    deal_id = deal["id"]
    props = deal["properties"]
    dealname = props.get("dealname", "")
    amount = float(props.get("amount") or 0)
    close_date = (props.get("closedate") or "")[:10]
    next_step = props.get("hs_next_step") or ""

    # Pull associations
    contacts = get_deal_contacts(deal_id)
    notes = get_deal_notes(deal_id)
    emails = get_deal_emails(deal_id)
    calls_log = get_deal_calls(deal_id)

    # Cross-ref Fathom
    contact_emails = [c.get("properties", {}).get("email", "").lower() for c in contacts]
    fathom_match = any(e in FATHOM_EMAIL_MAP for e in contact_emails)
    fathom_calls = []
    for e in contact_emails:
        if e in FATHOM_EMAIL_MAP:
            fathom_calls = FATHOM_EMAIL_MAP[e].get("fathom_calls", [])

    # Classification
    classification = classify_deal(deal, contacts, notes, emails, calls_log)

    # Most recent note text
    latest_note = ""
    if notes:
        latest_note = (notes[0].get("properties", {}).get("hs_note_body") or "")[:300]

    entry = {
        "deal_id": deal_id,
        "dealname": dealname,
        "amount": amount,
        "close_date": close_date,
        "hs_next_step": next_step,
        "owner_id": props.get("hubspot_owner_id"),
        "notes_last_updated": (props.get("notes_last_updated") or "")[:10],
        "num_notes": len(notes),
        "num_emails": len(emails),
        "num_calls": len(calls_log),
        "fathom_match": fathom_match,
        "fathom_calls_count": len(fathom_calls),
        "contacts": [{"email": c.get("properties", {}).get("email"), "name": f"{c.get('properties',{}).get('firstname','')} {c.get('properties',{}).get('lastname','')}".strip()} for c in contacts],
        "latest_note": latest_note,
        "classification": classification
    }

    results.append(entry)

    # March forecast tracking
    if close_date.startswith("2026-03"):
        deals_closing_march.append(entry)
        stage = classification["recommended_stage"]
        if stage == "Negotiation / Trial Activation":
            march_forecast["negotiation"] += amount
        elif stage == "Pricing Discussed":
            if "AT RISK" in classification.get("reasoning", ""):
                march_forecast["at_risk"] += amount
            else:
                march_forecast["pricing_discussed"] += amount
        elif stage == "Demo":
            march_forecast["back_to_demo"] += amount

    if (idx + 1) % 10 == 0:
        print(f"  Processed {idx+1}/{len(deals)}")

# Save raw results
with open(OUTPUT_FILE, "w") as f:
    json.dump({
        "generated": "2026-03-04",
        "total_deals": len(results),
        "results": results,
        "march_forecast": march_forecast
    }, f, indent=2)

print(f"\nSaved to {OUTPUT_FILE}")

# ---- GENERATE REPORT ----
print("Generating report...")

# Group by recommendation
move_to_negotiation = [r for r in results if r["classification"]["recommended_stage"] == "Negotiation / Trial Activation"]
stay_pricing = [r for r in results if r["classification"]["recommended_stage"] == "Pricing Discussed" and "AT RISK" not in r["classification"].get("reasoning","")]
at_risk = [r for r in results if r["classification"]["recommended_stage"] == "Pricing Discussed" and "AT RISK" in r["classification"].get("reasoning","")]
back_to_demo = [r for r in results if r["classification"]["recommended_stage"] == "Demo"]

total_pipeline = sum(r["amount"] for r in results)
negotiation_value = sum(r["amount"] for r in move_to_negotiation)
at_risk_value = sum(r["amount"] for r in at_risk)
back_to_demo_value = sum(r["amount"] for r in back_to_demo)
stay_pricing_value = sum(r["amount"] for r in stay_pricing)

# March forecast
march_total = sum(d["amount"] for d in deals_closing_march)
march_neg = sum(d["amount"] for d in deals_closing_march if d["classification"]["recommended_stage"] == "Negotiation / Trial Activation")
march_pricing = sum(d["amount"] for d in deals_closing_march if d["classification"]["recommended_stage"] == "Pricing Discussed" and "AT RISK" not in d["classification"].get("reasoning",""))
march_risk = sum(d["amount"] for d in deals_closing_march if "AT RISK" in d["classification"].get("reasoning",""))

# Weighted forecast (probability × amount)
march_weighted = (march_neg * 0.70) + (march_pricing * 0.40) + (march_risk * 0.15)

report_lines = [
    "# Pricing Discussed → Stage Review",
    f"**Generated:** 2026-03-04 | **Total deals reviewed:** {len(results)} | **Total pipeline value:** €{total_pipeline:,.0f}",
    "",
    "---",
    "",
    "## Summary",
    "",
    f"| Action | Deals | Value |",
    f"|--------|-------|-------|",
    f"| ✅ Move to Negotiation / Trial Activation | {len(move_to_negotiation)} | €{negotiation_value:,.0f} |",
    f"| ✅ Stay in Pricing Discussed (active) | {len(stay_pricing)} | €{stay_pricing_value:,.0f} |",
    f"| ⚠️ Stay in Pricing Discussed — AT RISK | {len(at_risk)} | €{at_risk_value:,.0f} |",
    f"| ↩️ Move back to Demo | {len(back_to_demo)} | €{back_to_demo_value:,.0f} |",
    "",
    "---",
    "",
    "## 1. Move to Negotiation / Trial Activation (70%)",
    "",
    "These deals show confirmed intent: payment mentioned, onboarding booked, or explicit decision meeting confirmed.",
    "",
    "| Deal | Amount | Close | Signal | Confidence |",
    "|------|--------|-------|--------|------------|"
]

for r in sorted(move_to_negotiation, key=lambda x: x["amount"], reverse=True):
    report_lines.append(f"| {r['dealname']} | €{r['amount']:,.0f} | {r['close_date']} | {r['classification']['trigger']} | {r['classification']['confidence']} |")

report_lines += [
    "",
    "---",
    "",
    "## 2. Move Back to Demo (30%)",
    "",
    "These deals never had pricing shared — they got stuck in Follow up before the proposal.",
    "",
    "| Deal | Amount | Close | Signal |",
    "|------|--------|-------|--------|"
]

for r in sorted(back_to_demo, key=lambda x: x["amount"], reverse=True):
    report_lines.append(f"| {r['dealname']} | €{r['amount']:,.0f} | {r['close_date']} | {r['classification']['trigger']} |")

report_lines += [
    "",
    "---",
    "",
    "## 3. AT RISK — Keep in Pricing Discussed but Flag",
    "",
    "These have explicit risk signals. Need rep action within 48h or should be disqualified.",
    "",
    "| Deal | Amount | Close | Risk Signal | Next Action |",
    "|------|--------|-------|-------------|-------------|"
]

for r in sorted(at_risk, key=lambda x: x["amount"], reverse=True):
    hs_ns = r.get("hs_next_step") or "None"
    report_lines.append(f"| {r['dealname']} | €{r['amount']:,.0f} | {r['close_date']} | {r['classification']['trigger']} | {hs_ns} |")

report_lines += [
    "",
    "---",
    "",
    "## 4. Correctly Placed — Stay in Pricing Discussed",
    "",
    "Pricing has been sent, waiting for prospect decision. These are correctly staged.",
    "",
    "| Deal | Amount | Close | Last Note | Notes Count |",
    "|------|--------|-------|-----------|-------------|"
]

for r in sorted(stay_pricing, key=lambda x: x["amount"], reverse=True)[:30]:
    report_lines.append(f"| {r['dealname']} | €{r['amount']:,.0f} | {r['close_date']} | {r['notes_last_updated']} | {r['num_notes']} |")

report_lines += [
    "",
    "---",
    "",
    "## 5. March 2026 Forecast",
    "",
    f"**Deals with March close dates:** {len(deals_closing_march)} deals | Total face value: €{march_total:,.0f}",
    "",
    f"| Stage | March Deals Value | Probability | Weighted |",
    f"|-------|------------------|-------------|---------|",
    f"| Negotiation / Trial Activation | €{march_neg:,.0f} | 70% | €{march_neg*0.70:,.0f} |",
    f"| Pricing Discussed (active) | €{march_pricing:,.0f} | 40% | €{march_pricing*0.40:,.0f} |",
    f"| At Risk | €{march_risk:,.0f} | 15% | €{march_risk*0.15:,.0f} |",
    f"",
    f"**Weighted forecast (March, Pricing Discussed pipeline only):** €{march_weighted:,.0f}",
    "",
    "> ⚠️ This is only the Pricing Discussed stage. Deals in Demo, Discovery, and Negotiation (already at 70%) are not included here. Full pipeline forecast requires all stages.",
    "",
    "---",
    "",
    "## Top 10 Deals Closing March — Detailed",
    "",
    "| Deal | Amount | Stage Rec | Risk | Next Step |",
    "|------|--------|-----------|------|-----------|"
]

top_march = sorted(deals_closing_march, key=lambda x: x["amount"], reverse=True)[:10]
for r in top_march:
    risk_flag = "🔴" if "AT RISK" in r["classification"].get("reasoning","") else ("🟢" if r["classification"]["recommended_stage"] == "Negotiation / Trial Activation" else "🟡")
    report_lines.append(f"| {r['dealname']} | €{r['amount']:,.0f} | {r['classification']['recommended_stage']} | {risk_flag} | {r.get('hs_next_step','—')} |")

report_lines += ["", "---", "", "*Sources: HubSpot Sales Pipeline, Fathom call data cross-reference*"]

with open(REPORT_FILE, "w") as f:
    f.write("\n".join(report_lines))

print(f"\nReport saved to {REPORT_FILE}")
print(f"\n=== SUMMARY ===")
print(f"Move to Negotiation: {len(move_to_negotiation)} deals (€{negotiation_value:,.0f})")
print(f"Stay Pricing Discussed: {len(stay_pricing)} deals (€{stay_pricing_value:,.0f})")
print(f"AT RISK: {len(at_risk)} deals (€{at_risk_value:,.0f})")
print(f"Back to Demo: {len(back_to_demo)} deals (€{back_to_demo_value:,.0f})")
print(f"\nMarch weighted forecast (this stage only): €{march_weighted:,.0f}")
