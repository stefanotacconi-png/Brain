"""
Move confirmed deals from Pricing Discussed → Negotiation / Trial Activation.
Adds an explanatory note on each deal.
Skips ANTONIO COLLETTA (false positive — At Risk, not Negotiation).
"""
import requests
import json
import time
from datetime import datetime

HUBSPOT_TOKEN = "YOUR_HUBSPOT_TOKEN"
BASE_URL = "https://api.hubapi.com"
HEADERS = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}

NEGOTIATION_STAGE_ID = "2674750700"
TODAY = "2026-03-04"

# 9 confirmed deals — ANTONIO COLLETTA intentionally excluded (false positive)
DEALS_TO_MOVE = [
    {
        "deal_id": "477800890555",
        "dealname": "Sergio Ferranti",
        "amount": 3048,
        "trigger": "deve pagare",
        "note": "Rep noted 'deve pagare' — customer has confirmed payment intent. Moved from Pricing Discussed → Negotiation / Trial Activation."
    },
    {
        "deal_id": "478624628948",
        "dealname": "AUA Pure Water",
        "amount": 3012,
        "trigger": "Activation",
        "note": "Rep noted 'Activation' as next step — confirmed activation intent. Moved from Pricing Discussed → Negotiation / Trial Activation."
    },
    {
        "deal_id": "471897440495",
        "dealname": "Maurizio Volpe",
        "amount": 1188,
        "trigger": "pagare",
        "note": "Rep noted 'pagare' — customer ready to pay. Moved from Pricing Discussed → Negotiation / Trial Activation."
    },
    {
        "deal_id": "443044063453",
        "dealname": "Paolo Fuschino",
        "amount": 1188,
        "trigger": "attivazione",
        "note": "Rep noted 'attivazione' — customer has confirmed activation. Moved from Pricing Discussed → Negotiation / Trial Activation."
    },
    {
        "deal_id": "461339848916",
        "dealname": "Mariel Muzzachi",
        "amount": 1068,
        "trigger": "They should buy on tuesday",
        "note": "Rep noted 'They should buy on tuesday' — strong buying signal with specific day. Moved from Pricing Discussed → Negotiation / Trial Activation."
    },
    {
        "deal_id": "443122459841",
        "dealname": "Grupo Tasvalor",
        "amount": 504,
        "trigger": "Awaiting confirmation, follow-up email sent",
        "note": "Rep noted 'Awaiting confirmation, follow-up email sent' — offer sent and pending final sign-off. Moved from Pricing Discussed → Negotiation / Trial Activation."
    },
    {
        "deal_id": "469867176163",
        "dealname": "Roberto Mora",
        "amount": 464,
        "trigger": "Onboarding call",
        "note": "Rep noted 'Onboarding call' as next step — customer has committed and is ready to onboard. Moved from Pricing Discussed → Negotiation / Trial Activation."
    },
    {
        "deal_id": "477762605274",
        "dealname": "Pablo Lax",
        "amount": 372,
        "trigger": "Pagarrrrrrrrr",
        "note": "Rep noted 'Pagarrrrrrrrr' — customer confirmed payment. Moved from Pricing Discussed → Negotiation / Trial Activation."
    },
    {
        "deal_id": "472223404240",
        "dealname": "Yolanda Hernández Tabanera",
        "amount": 267,
        "trigger": "Onboarding call with me",
        "note": "Rep noted 'Onboarding call with me' — customer booked onboarding, confirmed intent. Moved from Pricing Discussed → Negotiation / Trial Activation."
    },
]

results = []

def update_deal_stage(deal_id: str) -> bool:
    """Update deal stage to Negotiation / Trial Activation."""
    url = f"{BASE_URL}/crm/v3/objects/deals/{deal_id}"
    payload = {"properties": {"dealstage": NEGOTIATION_STAGE_ID}}
    resp = requests.patch(url, headers=HEADERS, json=payload)
    return resp.status_code in [200, 204], resp

def create_note_and_associate(deal_id: str, note_body: str) -> tuple:
    """Create a note and associate it with the deal."""
    # 1. Create note
    timestamp_ms = int(datetime(2026, 3, 4, 12, 0, 0).timestamp() * 1000)
    note_payload = {
        "properties": {
            "hs_note_body": note_body,
            "hs_timestamp": str(timestamp_ms)
        }
    }
    resp = requests.post(f"{BASE_URL}/crm/v3/objects/notes", headers=HEADERS, json=note_payload)
    if resp.status_code not in [200, 201]:
        return False, None, resp

    note_id = resp.json()["id"]

    # 2. Associate note → deal
    assoc_url = f"{BASE_URL}/crm/v3/objects/notes/{note_id}/associations/deals/{deal_id}/note_to_deal"
    resp2 = requests.put(assoc_url, headers=HEADERS)
    if resp2.status_code not in [200, 201, 204]:
        return False, note_id, resp2

    return True, note_id, resp2

print(f"Moving {len(DEALS_TO_MOVE)} deals to Negotiation / Trial Activation")
print(f"Stage ID: {NEGOTIATION_STAGE_ID}")
print("=" * 60)

for deal in DEALS_TO_MOVE:
    deal_id = deal["deal_id"]
    name = deal["dealname"]
    amount = deal["amount"]
    trigger = deal["trigger"]
    note_text = deal["note"]

    print(f"\n→ {name} (€{amount:,}) — trigger: '{trigger}'")

    # Step 1: Update stage
    success_stage, resp_stage = update_deal_stage(deal_id)
    if success_stage:
        print(f"  ✅ Stage updated to Negotiation")
    else:
        print(f"  ❌ Stage update FAILED: {resp_stage.status_code} {resp_stage.text[:100]}")
        results.append({"deal": name, "deal_id": deal_id, "stage_updated": False, "note_created": False, "error": resp_stage.text[:200]})
        continue

    time.sleep(0.3)

    # Step 2: Create note
    success_note, note_id, resp_note = create_note_and_associate(deal_id, note_text)
    if success_note:
        print(f"  ✅ Note created (ID: {note_id}) and associated")
    else:
        print(f"  ⚠️  Note creation failed: {resp_note.status_code} {resp_note.text[:100]}")

    results.append({
        "deal": name,
        "deal_id": deal_id,
        "amount": amount,
        "trigger": trigger,
        "stage_updated": success_stage,
        "note_created": success_note,
        "note_id": note_id if success_note else None
    })

    time.sleep(0.3)

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
moved = [r for r in results if r["stage_updated"]]
noted = [r for r in results if r.get("note_created")]
failed = [r for r in results if not r["stage_updated"]]

print(f"✅ Deals moved to Negotiation: {len(moved)}/9")
print(f"✅ Notes created: {len(noted)}/9")
if failed:
    print(f"❌ Failed: {[r['deal'] for r in failed]}")

total_value = sum(r["amount"] for r in moved)
print(f"💰 Total value moved: €{total_value:,}")

# Save log
with open("output/negotiation_move_log.json", "w") as f:
    json.dump({"date": TODAY, "results": results}, f, indent=2)
print("\nLog saved to output/negotiation_move_log.json")

# Skipped deal note
print("\n⚠️  SKIPPED: ANTONIO COLLETTA (ID: 465627431111)")
print("   Reason: hs_next_step = 'At Risk - No show in Activation Meeting'")
print("   Classification: Correctly stays in Pricing Discussed as AT RISK")
