"""
Review all open deals in 'Pricing Discussed' stage — v2.
Classification based ONLY on hs_next_step (rep-intentional field).
Note body is read for context summary only — not used for keyword matching.
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

PRICING_DISCUSSED_STAGE = "986053468"
SALES_PIPELINE = "671838099"
NEGOTIATION_STAGE = "2674750700"
DEMO_STAGE = "986053467"

OUTPUT_FILE = Path("output/pricing_discussed_v2_review.json")
REPORT_FILE = Path("output/pricing_discussed_v2_report.md")

TODAY = datetime(2026, 3, 4, tzinfo=timezone.utc)

# ---- CLASSIFICATION RULES (hs_next_step only) ----

NEGOTIATION_KEYWORDS = [
    "deve pagare", "pagare", "pagamento", "sta pagando",
    "attivazione", "activation", "attivare", "attiva",
    "onboarding call", "onboarding",
    "hanno accettato", "ha accettato", "confermato", "confirmed",
    "contratto", "signing", "firma",
    "trial running", "trial attivo", "trial in corso",
    "fattura", "invoice", "paying",
    "they should buy", "si chiude", "chiude",
    "ha detto sì", "ha detto si", "said yes",
    "accordo", "deal chiuso", "pronto ad attivare",
    "stanno attivando", "ready to sign", "pronto a firmare",
    "pagarrrrr",  # Pablo Lax
]

AT_RISK_KEYWORDS = [
    "at risk", "a rischio",
    "no answer", "no risponde", "non risponde",
    "ghosting", "fantasma",
    "no show", "no-show",
    "no decision maker", "not a decision maker", "non è il decision maker",
    "non decide", "not deciding",
    "rimandato", "rimandite", "rimandato a", "rimandato al",
    "troppo caro", "too expensive", "pricing issue", "prezzo alto",
    "competitor", "concorrente",
    "changed his mind", "cambiato idea", "change is mind",
    "stop answer", "stop rispondendo",
    "in attesa di", "waiting for crm", "waiting for integration",
    "#risk", "#at risk",
    "non vuole", "vuole pensarci",
]

DEMO_KEYWORDS = [
    "demo", "to present", "presentare proposta", "presentare offerta",
    "fare demo", "show product", "show the product",
    "rifare demo", "nuova demo",
]

DISCOVERY_KEYWORDS = [
    "discovery call", "first call", "prima call",
    "qualifica", "qualification",
]

FOLLOW_UP_PENDING_KEYWORDS = [
    "follow up", "fup", "follow-up",
    "richiamare", "richiamarlo", "call them",
    "decision", "decide", "deciding",
    "meeting in two weeks", "call next week", "call in",
    "waiting for answer", "aspetto risposta",
    "aspettare", "waiting",
    "discuss internally", "decide internally", "discutere internamente",
    "revisa con", "review with manager",
    "evaluate", "valutare",
]

def strip_html(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def days_since(date_str: str) -> int:
    if not date_str:
        return 999
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return (TODAY - dt).days
    except:
        return 999

def get_latest_note(deal_id: str) -> dict:
    """Get the most recent note on a deal."""
    url = f"{BASE_URL}/crm/v3/objects/deals/{deal_id}/associations/notes"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return {}
    note_ids = [r["id"] for r in resp.json().get("results", [])]
    if not note_ids:
        return {}
    notes = []
    for nid in note_ids[:5]:
        resp2 = requests.get(
            f"{BASE_URL}/crm/v3/objects/notes/{nid}",
            headers=HEADERS,
            params={"properties": "hs_note_body,hs_timestamp"}
        )
        if resp2.status_code == 200:
            notes.append(resp2.json())
        time.sleep(0.04)
    notes.sort(key=lambda x: x.get("properties", {}).get("hs_timestamp", ""), reverse=True)
    if notes:
        p = notes[0].get("properties", {})
        return {
            "date": (p.get("hs_timestamp") or "")[:10],
            "text": strip_html(p.get("hs_note_body") or "")[:400],
            "count": len(note_ids)
        }
    return {}

def classify_by_next_step(hs_next_step: str, notes_updated: str, close_date: str, amount: float) -> dict:
    """
    Classify deal using ONLY hs_next_step + staleness signals.
    Never reads note body for classification.
    """
    ns = (hs_next_step or "").strip().lower()
    days_note = days_since(notes_updated)
    close_days = days_since(close_date) * -1 if close_date else None  # negative = future

    # Check if close date is in the past
    close_overdue = False
    if close_date:
        cd = datetime.fromisoformat(close_date[:10] + "T00:00:00+00:00")
        close_overdue = cd < TODAY

    # --- NEGOTIATION signals ---
    for kw in NEGOTIATION_KEYWORDS:
        if kw in ns:
            return {
                "stage": "Negotiation / Trial Activation",
                "stage_id": NEGOTIATION_STAGE,
                "probability": 0.70,
                "status": "🟢 MOVE TO NEGOTIATION",
                "trigger": kw,
                "confidence": "HIGH",
                "reason": f"Rep explicitly noted '{kw}' in next step — confirmed payment or activation intent"
            }

    # --- AT RISK signals ---
    for kw in AT_RISK_KEYWORDS:
        if kw in ns:
            return {
                "stage": "Pricing Discussed",
                "stage_id": PRICING_DISCUSSED_STAGE,
                "probability": 0.10,
                "status": "🔴 AT RISK",
                "trigger": kw,
                "confidence": "HIGH",
                "reason": f"Rep flagged '{kw}' — deal in danger. Needs decision: push hard or disqualify"
            }

    # --- DEMO signals ---
    for kw in DEMO_KEYWORDS:
        if kw in ns:
            return {
                "stage": "Demo",
                "stage_id": DEMO_STAGE,
                "probability": 0.30,
                "status": "↩️ MOVE BACK TO DEMO",
                "trigger": kw,
                "confidence": "HIGH",
                "reason": f"Rep noted '{kw}' — pricing not yet shared, deal should be in Demo"
            }

    # --- FOLLOW UP PENDING signals ---
    for kw in FOLLOW_UP_PENDING_KEYWORDS:
        if kw in ns:
            if close_overdue:
                return {
                    "stage": "Pricing Discussed",
                    "stage_id": PRICING_DISCUSSED_STAGE,
                    "probability": 0.20,
                    "status": "🟠 STALE + OVERDUE",
                    "trigger": kw,
                    "confidence": "MEDIUM",
                    "reason": f"Close date passed. Rep noted '{kw}' — needs immediate action or disqualification"
                }
            return {
                "stage": "Pricing Discussed",
                "stage_id": PRICING_DISCUSSED_STAGE,
                "probability": 0.35,
                "status": "🟡 WAITING FOR DECISION",
                "trigger": kw,
                "confidence": "MEDIUM",
                "reason": f"Rep noted '{kw}' — prospect deliberating. Active but no confirmed intent yet"
            }

    # --- EMPTY next step + staleness check ---
    if not ns:
        if close_overdue:
            return {
                "stage": "Pricing Discussed",
                "stage_id": PRICING_DISCUSSED_STAGE,
                "probability": 0.10,
                "status": "🔴 STALE + OVERDUE — NO NEXT STEP",
                "trigger": "no next step + overdue",
                "confidence": "HIGH",
                "reason": f"Close date passed and no next step logged. Rep has abandoned this deal or forgotten it"
            }
        if days_note > 21:
            return {
                "stage": "Pricing Discussed",
                "stage_id": PRICING_DISCUSSED_STAGE,
                "probability": 0.15,
                "status": "🔴 STALE — NO ACTIVITY",
                "trigger": f"no activity {days_note}d",
                "confidence": "HIGH",
                "reason": f"No notes in {days_note} days + no next step. Deal is likely dead or forgotten"
            }
        if days_note > 10:
            return {
                "stage": "Pricing Discussed",
                "stage_id": PRICING_DISCUSSED_STAGE,
                "probability": 0.25,
                "status": "🟠 GOING COLD",
                "trigger": f"no next step, {days_note}d since last note",
                "confidence": "MEDIUM",
                "reason": f"No next step logged. Last note {days_note} days ago — rep needs to follow up urgently"
            }
        # Recent activity but no clear signal
        return {
            "stage": "Pricing Discussed",
            "stage_id": PRICING_DISCUSSED_STAGE,
            "probability": 0.30,
            "status": "🟡 ACTIVE — NO CLEAR SIGNAL",
            "trigger": "recent but unclear",
            "confidence": "LOW",
            "reason": "Recent activity but no next step logged. Rep should update hs_next_step immediately"
        }

    # Has some text in next step but no keyword matched
    if close_overdue:
        return {
            "stage": "Pricing Discussed",
            "stage_id": PRICING_DISCUSSED_STAGE,
            "probability": 0.15,
            "status": "🟠 OVERDUE — REVIEW MANUALLY",
            "trigger": f"overdue: '{ns[:40]}'",
            "confidence": "LOW",
            "reason": f"Close date passed. Next step: '{hs_next_step}'. Needs rep review"
        }

    return {
        "stage": "Pricing Discussed",
        "stage_id": PRICING_DISCUSSED_STAGE,
        "probability": 0.35,
        "status": "🟡 ACTIVE",
        "trigger": f"'{ns[:40]}'",
        "confidence": "LOW",
        "reason": f"Next step noted but unclear intent: '{hs_next_step}'. Rep should clarify"
    }

def get_all_pricing_discussed_deals() -> list:
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
                "dealname", "amount", "closedate", "hubspot_owner_id",
                "hs_lastmodifieddate", "notes_last_updated",
                "hs_next_step", "createdate", "num_associated_contacts"
            ],
            "limit": 100,
            "sorts": [{"propertyName": "amount", "direction": "DESCENDING"}]
        }
        if after:
            payload["after"] = after
        resp = requests.post(f"{BASE_URL}/crm/v3/objects/deals/search", headers=HEADERS, json=payload)
        if resp.status_code != 200:
            print(f"Error: {resp.status_code} {resp.text[:200]}")
            break
        data = resp.json()
        all_deals.extend(data.get("results", []))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
        time.sleep(0.2)
    return all_deals

def get_deal_contacts(deal_id: str) -> list:
    url = f"{BASE_URL}/crm/v3/objects/deals/{deal_id}/associations/contacts"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return []
    contact_ids = [r["id"] for r in resp.json().get("results", [])]
    contacts = []
    for cid in contact_ids[:2]:
        resp2 = requests.get(
            f"{BASE_URL}/crm/v3/objects/contacts/{cid}",
            headers=HEADERS,
            params={"properties": "email,firstname,lastname,company"}
        )
        if resp2.status_code == 200:
            p = resp2.json().get("properties", {})
            contacts.append({
                "email": p.get("email", ""),
                "name": f"{p.get('firstname','')} {p.get('lastname','')}".strip(),
                "company": p.get("company", "")
            })
        time.sleep(0.04)
    return contacts

# ---- MAIN ----
print("Fetching all Pricing Discussed deals...")
deals = get_all_pricing_discussed_deals()
print(f"Found {len(deals)} deals")
deals.sort(key=lambda d: float(d["properties"].get("amount") or 0), reverse=True)

results = []
print(f"Analyzing {len(deals)} deals...")

for idx, deal in enumerate(deals):
    deal_id = deal["id"]
    props = deal["properties"]
    dealname = props.get("dealname", "")
    amount = float(props.get("amount") or 0)
    close_date = (props.get("closedate") or "")[:10]
    hs_next_step = props.get("hs_next_step") or ""
    notes_updated = (props.get("notes_last_updated") or "")[:10]

    # Pull contacts
    contacts = get_deal_contacts(deal_id)

    # Pull latest note (for context display only — not classification)
    latest_note = get_latest_note(deal_id)

    # Classify based ONLY on hs_next_step
    classification = classify_by_next_step(hs_next_step, notes_updated, close_date, amount)

    # Overdue flag
    close_overdue = False
    if close_date:
        try:
            cd = datetime.fromisoformat(close_date + "T00:00:00+00:00")
            close_overdue = cd < TODAY
        except:
            pass

    results.append({
        "deal_id": deal_id,
        "dealname": dealname,
        "amount": amount,
        "close_date": close_date,
        "close_overdue": close_overdue,
        "hs_next_step": hs_next_step,
        "notes_updated": notes_updated,
        "days_since_note": days_since(notes_updated),
        "owner_id": props.get("hubspot_owner_id"),
        "contacts": contacts,
        "latest_note_date": latest_note.get("date", ""),
        "latest_note_text": latest_note.get("text", "")[:300],
        "note_count": latest_note.get("count", 0),
        "classification": classification
    })

    if (idx + 1) % 20 == 0:
        print(f"  Processed {idx+1}/{len(deals)}")

# Save raw
with open(OUTPUT_FILE, "w") as f:
    json.dump({"generated": "2026-03-04", "total": len(results), "results": results}, f, indent=2)
print(f"Saved to {OUTPUT_FILE}")

# ---- GROUPING ----
move_negotiation  = [r for r in results if r["classification"]["stage"] == "Negotiation / Trial Activation"]
at_risk           = [r for r in results if "AT RISK" in r["classification"]["status"] or "OVERDUE" in r["classification"]["status"]]
back_to_demo      = [r for r in results if "MOVE BACK TO DEMO" in r["classification"]["status"]]
waiting_decision  = [r for r in results if "WAITING FOR DECISION" in r["classification"]["status"]]
active_no_signal  = [r for r in results if "ACTIVE" in r["classification"]["status"] and "NO CLEAR SIGNAL" in r["classification"]["status"]]
going_cold        = [r for r in results if "GOING COLD" in r["classification"]["status"]]
stale_no_activity = [r for r in results if "STALE" in r["classification"]["status"] and "OVERDUE" not in r["classification"]["status"]]

def val(lst): return sum(r["amount"] for r in lst)

print(f"\n=== SUMMARY ===")
print(f"Move to Negotiation:   {len(move_negotiation):3d} deals  €{val(move_negotiation):>10,.0f}")
print(f"At Risk / Overdue:     {len(at_risk):3d} deals  €{val(at_risk):>10,.0f}")
print(f"Move back to Demo:     {len(back_to_demo):3d} deals  €{val(back_to_demo):>10,.0f}")
print(f"Waiting for Decision:  {len(waiting_decision):3d} deals  €{val(waiting_decision):>10,.0f}")
print(f"Active, no signal:     {len(active_no_signal):3d} deals  €{val(active_no_signal):>10,.0f}")
print(f"Going Cold:            {len(going_cold):3d} deals  €{val(going_cold):>10,.0f}")
print(f"Stale / No activity:   {len(stale_no_activity):3d} deals  €{val(stale_no_activity):>10,.0f}")

# ---- MARCH FORECAST ----
march = [r for r in results if (r["close_date"] or "").startswith("2026-03")]
march_neg = [r for r in march if r["classification"]["stage"] == "Negotiation / Trial Activation"]
march_risk = [r for r in march if "AT RISK" in r["classification"]["status"] or "OVERDUE" in r["classification"]["status"]]
march_wait = [r for r in march if "WAITING" in r["classification"]["status"]]
march_cold = [r for r in march if "GOING COLD" in r["classification"]["status"] or "STALE" in r["classification"]["status"]]
march_active = [r for r in march if "ACTIVE" in r["classification"]["status"]]

weighted = (
    val(march_neg) * 0.70 +
    val(march_wait) * 0.35 +
    val(march_active) * 0.25 +
    val(march_cold) * 0.10 +
    val(march_risk) * 0.05
)

print(f"\n=== MARCH FORECAST (Pricing Discussed only) ===")
print(f"Total March close date deals: {len(march)}, face value: €{val(march):,.0f}")
print(f"Negotiation (70%):  €{val(march_neg):>10,.0f}  → weighted €{val(march_neg)*0.70:>8,.0f}")
print(f"Waiting (35%):      €{val(march_wait):>10,.0f}  → weighted €{val(march_wait)*0.35:>8,.0f}")
print(f"Active (25%):       €{val(march_active):>10,.0f}  → weighted €{val(march_active)*0.25:>8,.0f}")
print(f"Going Cold (10%):   €{val(march_cold):>10,.0f}  → weighted €{val(march_cold)*0.10:>8,.0f}")
print(f"At Risk (5%):       €{val(march_risk):>10,.0f}  → weighted €{val(march_risk)*0.05:>8,.0f}")
print(f"WEIGHTED FORECAST:  €{weighted:>10,.0f}")

# ---- WRITE REPORT ----
lines = [
    "# Pricing Discussed — Real Status Review (v2)",
    f"**Generated:** 2026-03-04 | **Method:** hs_next_step classification only (no note body keyword matching)",
    f"**Total deals:** {len(results)} | **Total pipeline:** €{val(results):,.0f}",
    "",
    "---",
    "## Summary",
    "",
    "| Status | Deals | Value |",
    "|--------|-------|-------|",
    f"| 🟢 Move → Negotiation / Trial Activation | {len(move_negotiation)} | €{val(move_negotiation):,.0f} |",
    f"| 🔴 At Risk / Overdue | {len(at_risk)} | €{val(at_risk):,.0f} |",
    f"| ↩️ Move back to Demo | {len(back_to_demo)} | €{val(back_to_demo):,.0f} |",
    f"| 🟡 Waiting for Decision | {len(waiting_decision)} | €{val(waiting_decision):,.0f} |",
    f"| 🟡 Active — No Clear Signal | {len(active_no_signal)} | €{val(active_no_signal):,.0f} |",
    f"| 🟠 Going Cold (10+ days no activity) | {len(going_cold)} | €{val(going_cold):,.0f} |",
    f"| 🔴 Stale — No Activity 21+ days | {len(stale_no_activity)} | €{val(stale_no_activity):,.0f} |",
    "",
    "---",
]

def deal_rows(lst, cols="standard"):
    rows = []
    for r in sorted(lst, key=lambda x: x["amount"], reverse=True):
        contacts_str = ", ".join(c["name"] for c in r["contacts"] if c["name"])
        note_preview = (r["latest_note_text"] or "")[:120].replace("|","—").replace("\n"," ")
        ns = (r["hs_next_step"] or "—")[:60]
        overdue = " ⚠️OVERDUE" if r["close_overdue"] else ""
        rows.append(f"| {r['dealname'][:45]} | €{r['amount']:,.0f} | {r['close_date']}{overdue} | {ns} | {note_preview} |")
    return rows

lines += [
    "## 1. 🟢 Move to Negotiation / Trial Activation",
    "",
    "Rep has explicitly noted payment, activation, or onboarding in next step field.",
    "",
    "| Deal | Amount | Close | Rep Next Step | Latest Note Preview |",
    "|------|--------|-------|---------------|---------------------|",
] + deal_rows(move_negotiation) + [""]

lines += [
    "---",
    "## 2. 🔴 At Risk / Overdue — Decide or Disqualify",
    "",
    "These deals are either explicitly flagged at risk, or their close date has passed with no progress.",
    "",
    "| Deal | Amount | Close | Rep Next Step | Latest Note Preview |",
    "|------|--------|-------|---------------|---------------------|",
] + deal_rows(at_risk) + [""]

lines += [
    "---",
    "## 3. ↩️ Move Back to Demo",
    "",
    "Rep next step says 'demo' — pricing was never actually shared.",
    "",
    "| Deal | Amount | Close | Rep Next Step | Latest Note Preview |",
    "|------|--------|-------|---------------|---------------------|",
] + deal_rows(back_to_demo) + [""]

lines += [
    "---",
    "## 4. 🟡 Waiting for Decision",
    "",
    "Pricing shared, prospect is deliberating. Active deals but no confirmed intent signal yet.",
    "",
    "| Deal | Amount | Close | Rep Next Step | Latest Note Preview |",
    "|------|--------|-------|---------------|---------------------|",
] + deal_rows(waiting_decision) + [""]

lines += [
    "---",
    "## 5. 🟠 Going Cold (10–21 days no activity, no next step)",
    "",
    "| Deal | Amount | Close | Days Since Note | Latest Note Preview |",
    "|------|--------|-------|-----------------|---------------------|",
]
for r in sorted(going_cold, key=lambda x: x["amount"], reverse=True):
    note_preview = (r["latest_note_text"] or "")[:100].replace("|","—").replace("\n"," ")
    overdue = " ⚠️" if r["close_overdue"] else ""
    lines.append(f"| {r['dealname'][:45]} | €{r['amount']:,.0f} | {r['close_date']}{overdue} | {r['days_since_note']}d | {note_preview} |")
lines.append("")

lines += [
    "---",
    "## 6. 🔴 Stale — No Activity 21+ Days, No Next Step",
    "",
    "| Deal | Amount | Close | Days Since Note | Latest Note Preview |",
    "|------|--------|-------|-----------------|---------------------|",
]
for r in sorted(stale_no_activity, key=lambda x: x["amount"], reverse=True):
    note_preview = (r["latest_note_text"] or "")[:100].replace("|","—").replace("\n"," ")
    overdue = " ⚠️" if r["close_overdue"] else ""
    lines.append(f"| {r['dealname'][:45]} | €{r['amount']:,.0f} | {r['close_date']}{overdue} | {r['days_since_note']}d | {note_preview} |")
lines.append("")

lines += [
    "---",
    "## 7. March 2026 Forecast (Pricing Discussed only)",
    "",
    f"**{len(march)} deals** with March close dates | Face value: **€{val(march):,.0f}**",
    "",
    "| Bucket | Face Value | Probability | Weighted |",
    "|--------|-----------|-------------|---------|",
    f"| 🟢 Negotiation | €{val(march_neg):,.0f} | 70% | **€{val(march_neg)*0.70:,.0f}** |",
    f"| 🟡 Waiting for Decision | €{val(march_wait):,.0f} | 35% | **€{val(march_wait)*0.35:,.0f}** |",
    f"| 🟡 Active (no signal) | €{val(march_active):,.0f} | 25% | **€{val(march_active)*0.25:,.0f}** |",
    f"| 🟠 Going Cold | €{val(march_cold):,.0f} | 10% | **€{val(march_cold)*0.10:,.0f}** |",
    f"| 🔴 At Risk / Overdue | €{val(march_risk):,.0f} | 5% | **€{val(march_risk)*0.05:,.0f}** |",
    f"| **WEIGHTED TOTAL** | **€{val(march):,.0f}** | | **€{weighted:,.0f}** |",
    "",
    "---",
    "*Classification based on hs_next_step field only. Note body read for display — not used for scoring.*"
]

with open(REPORT_FILE, "w") as f:
    f.write("\n".join(lines))

print(f"\nReport saved to {REPORT_FILE}")
