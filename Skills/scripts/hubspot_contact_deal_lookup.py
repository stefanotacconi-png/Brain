"""
HubSpot Contact + Deal Lookup
For each prospect email from Fathom calls + Lemlist cold calls,
finds their HubSpot contact and associated deals, then analyzes conversion.
"""
import json
import time
import requests
from pathlib import Path
from collections import defaultdict, Counter

HUBSPOT_TOKEN = "YOUR_HUBSPOT_TOKEN"
BASE_URL = "https://api.hubapi.com"
HEADERS = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}

EMAIL_MAP_FILE = Path("output/all_contact_emails.json")
OUTPUT_FILE = Path("output/hubspot_deal_analysis.json")
REPORT_FILE = Path("output/conversion_analysis_report.md")

# Deal stage labels (HubSpot internal names → readable)
DEAL_STAGE_LABELS = {
    # Standard stages – update if your pipeline differs
    "appointmentscheduled": "Demo/Meeting Booked",
    "qualifiedtobuy": "Qualified",
    "presentationscheduled": "Proposal Sent",
    "decisionmakerboughtin": "Decision Maker Engaged",
    "contractsent": "Contract Sent",
    "closedwon": "Closed Won",
    "closedlost": "Closed Lost",
}

def search_contacts_by_emails(emails: list) -> list:
    """Search HubSpot contacts for a list of emails (up to 5 per call via OR filterGroups)."""
    contacts = []
    batch_size = 5
    for i in range(0, len(emails), batch_size):
        batch = emails[i:i+batch_size]
        filter_groups = [
            {"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}
            for email in batch
        ]
        payload = {
            "filterGroups": filter_groups,
            "properties": [
                "email", "firstname", "lastname", "jobtitle", "company",
                "lifecyclestage", "hs_lead_status", "num_associated_deals",
                "hs_object_id", "createdate", "hs_latest_source"
            ],
            "limit": 100
        }
        resp = requests.post(f"{BASE_URL}/crm/v3/objects/contacts/search", headers=HEADERS, json=payload)
        if resp.status_code == 200:
            contacts.extend(resp.json().get("results", []))
        else:
            print(f"  Error {resp.status_code} for batch {i//batch_size}: {resp.text[:200]}")
        time.sleep(0.15)  # rate limit safety
    return contacts

def get_contact_deals(contact_id: str) -> list:
    """Get all deals associated with a contact."""
    url = f"{BASE_URL}/crm/v3/objects/contacts/{contact_id}/associations/deals"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return []
    deal_ids = [r["id"] for r in resp.json().get("results", [])]
    if not deal_ids:
        return []

    # Batch fetch deal details
    deals = []
    for did in deal_ids:
        resp2 = requests.get(
            f"{BASE_URL}/crm/v3/objects/deals/{did}",
            headers=HEADERS,
            params={"properties": "dealname,dealstage,amount,closedate,pipeline,hs_deal_stage_probability,owner_id,createdate,hs_is_closed_won,hs_is_closed"}
        )
        if resp2.status_code == 200:
            deals.append(resp2.json())
        time.sleep(0.05)
    return deals

def get_pipeline_stages() -> dict:
    """Fetch all pipeline stages from HubSpot."""
    resp = requests.get(f"{BASE_URL}/crm/v3/pipelines/deals", headers=HEADERS)
    stage_map = {}
    if resp.status_code == 200:
        for pipeline in resp.json().get("results", []):
            for stage in pipeline.get("stages", []):
                stage_map[stage["id"]] = {
                    "label": stage["label"],
                    "pipeline": pipeline["label"],
                    "displayOrder": stage.get("displayOrder", 0),
                    "probability": stage.get("metadata", {}).get("probability", "0")
                }
    return stage_map

# ---- MAIN ----
print("Loading email map...")
with open(EMAIL_MAP_FILE) as f:
    email_data = json.load(f)

email_map = email_data["email_map"]
all_emails = list(email_map.keys())
print(f"Total emails to look up: {len(all_emails)}")

print("\nFetching pipeline stages...")
stage_map = get_pipeline_stages()
print(f"  Found {len(stage_map)} deal stages")
for sid, s in stage_map.items():
    print(f"    [{s['pipeline']}] {sid} → {s['label']}")

print(f"\nSearching {len(all_emails)} contacts in HubSpot...")
all_contacts = search_contacts_by_emails(all_emails)
print(f"  Found {len(all_contacts)} matching contacts")

# Index by email
contact_by_email = {}
for c in all_contacts:
    email = c["properties"].get("email", "").lower()
    contact_by_email[email] = c

print(f"\nFetching associated deals for {len(all_contacts)} contacts...")
contact_deal_data = []
for idx, contact in enumerate(all_contacts):
    cid = contact["id"]
    email = contact["properties"].get("email", "").lower()
    deals = get_contact_deals(cid)
    source_info = email_map.get(email, {})

    entry = {
        "contact_id": cid,
        "email": email,
        "name": f"{contact['properties'].get('firstname','')} {contact['properties'].get('lastname','')}".strip(),
        "jobtitle": contact["properties"].get("jobtitle", ""),
        "company": contact["properties"].get("company", ""),
        "lifecyclestage": contact["properties"].get("lifecyclestage", ""),
        "lead_status": contact["properties"].get("hs_lead_status", ""),
        "num_deals": len(deals),
        "fathom_calls": source_info.get("fathom_calls", []),
        "lemlist_info": source_info.get("lemlist", None),
        "deals": []
    }

    for deal in deals:
        dp = deal["properties"]
        stage_id = dp.get("dealstage", "")
        stage_info = stage_map.get(stage_id, {"label": stage_id, "pipeline": "unknown", "probability": "0"})
        entry["deals"].append({
            "deal_id": deal["id"],
            "dealname": dp.get("dealname", ""),
            "stage_id": stage_id,
            "stage_label": stage_info.get("label", stage_id),
            "pipeline": stage_info.get("pipeline", ""),
            "probability": stage_info.get("probability", "0"),
            "amount": dp.get("amount", ""),
            "closedate": dp.get("closedate", ""),
            "createdate": dp.get("createdate", ""),
            "is_won": dp.get("hs_is_closed_won", "false") == "true",
            "is_closed": dp.get("hs_is_closed", "false") == "true"
        })

    contact_deal_data.append(entry)
    if (idx+1) % 10 == 0:
        print(f"  Processed {idx+1}/{len(all_contacts)}")

print(f"\nSaving raw data to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, "w") as f:
    json.dump({
        "generated": "2026-03-04",
        "total_emails_searched": len(all_emails),
        "contacts_found_in_hubspot": len(all_contacts),
        "stage_map": stage_map,
        "contacts": contact_deal_data
    }, f, indent=2)

# ---- ANALYSIS ----
print("\n=== ANALYSIS ===")

contacts_with_deals = [c for c in contact_deal_data if c["num_deals"] > 0]
contacts_no_deals = [c for c in contact_deal_data if c["num_deals"] == 0]
not_in_hubspot = [e for e in all_emails if e not in contact_by_email]

print(f"\nContacts found in HubSpot: {len(all_contacts)} / {len(all_emails)}")
print(f"  With deals: {len(contacts_with_deals)}")
print(f"  No deals: {len(contacts_no_deals)}")
print(f"  Not in HubSpot at all: {len(not_in_hubspot)}")

# Deal stage breakdown
all_deals = [deal for c in contact_deal_data for deal in c["deals"]]
stage_counts = Counter(d["stage_label"] for d in all_deals)
won_deals = [d for d in all_deals if d["is_won"]]
closed_lost = [d for d in all_deals if d["is_closed"] and not d["is_won"]]
open_deals = [d for d in all_deals if not d["is_closed"]]

print(f"\n--- All {len(all_deals)} deals ---")
print(f"Won: {len(won_deals)}")
print(f"Lost: {len(closed_lost)}")
print(f"Open: {len(open_deals)}")
print("\nDeal stage distribution:")
for stage, count in stage_counts.most_common():
    print(f"  {stage}: {count}")

# Lifecycle stage breakdown
lifecycle_counts = Counter(c["lifecyclestage"] for c in contact_deal_data)
print(f"\n--- Contact lifecycle stages ---")
for stage, count in lifecycle_counts.most_common():
    print(f"  {stage}: {count}")

# Source breakdown (fathom vs lemlist)
fathom_contacts = [c for c in contact_deal_data if c["fathom_calls"]]
lemlist_contacts_found = [c for c in contact_deal_data if c["lemlist_info"]]
fathom_with_deals = [c for c in fathom_contacts if c["num_deals"] > 0]
lemlist_with_deals = [c for c in lemlist_contacts_found if c["num_deals"] > 0]

print(f"\n--- Source breakdown ---")
print(f"From Fathom calls: {len(fathom_contacts)} in HubSpot, {len(fathom_with_deals)} with deals")
print(f"From Lemlist cold calls: {len(lemlist_contacts_found)} in HubSpot, {len(lemlist_with_deals)} with deals")

# Won deals details
print(f"\n--- Won deals ---")
for c in contact_deal_data:
    for d in c["deals"]:
        if d["is_won"]:
            print(f"  {c['name']} ({c['company']}) - {d['dealname']} - €{d.get('amount','?')}")

# Open deals (pipeline)
print(f"\n--- Open deals in pipeline ---")
for c in contact_deal_data:
    for d in c["deals"]:
        if not d["is_closed"]:
            print(f"  {c['name']} ({c['company']}) | {d['stage_label']} | {d['dealname']} | €{d.get('amount','?')}")

print(f"\nAnalysis complete. See {OUTPUT_FILE}")
