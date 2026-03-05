import json
import os
from pathlib import Path
from collections import defaultdict

CALLS_DIR = Path("output/calls")
LEMLIST_FILE = Path("output/lemlist/connected_cold_calls.json")
OUTPUT_FILE = Path("output/all_contact_emails.json")

SPOKI_DOMAINS = {"spoki.it", "spoki.com"}

def get_external_emails_from_call(filepath):
    """Extract non-Spoki emails and metadata from a call file."""
    try:
        with open(filepath) as f:
            data = json.load(f)
    except Exception:
        return None

    external_emails = set()
    for turn in data.get("transcript", []):
        email = turn.get("speaker", {}).get("matched_calendar_invitee_email", "")
        if email and "@" in email:
            domain = email.split("@")[-1].lower()
            if domain not in SPOKI_DOMAINS:
                external_emails.add(email.lower())

    if not external_emails:
        return None

    return {
        "recording_id": data.get("recording_id"),
        "title": data.get("meeting_title", data.get("title", "")),
        "created_at": data.get("created_at", ""),
        "url": data.get("url", ""),
        "emails": list(external_emails),
        "source": "fathom"
    }

# Load all calls, sort by date, take last 100
print("Scanning Fathom call files...")
all_calls = []
for f in CALLS_DIR.glob("*.json"):
    result = get_external_emails_from_call(f)
    if result and result.get("created_at"):
        all_calls.append(result)

all_calls.sort(key=lambda x: x["created_at"], reverse=True)
last_100 = all_calls[:100]
print(f"  Total calls with external emails: {len(all_calls)}")
print(f"  Taking last 100 (from {last_100[-1]['created_at'][:10]} to {last_100[0]['created_at'][:10]})")

# Load Lemlist cold call contacts
print("Loading Lemlist cold calls...")
with open(LEMLIST_FILE) as f:
    lemlist_leads = json.load(f)

lemlist_contacts = []
for lead in lemlist_leads:
    email = lead.get("email", "").lower().strip()
    if email and "@" in email:
        lemlist_contacts.append({
            "email": email,
            "full_name": lead.get("full_name", ""),
            "job_title": lead.get("job_title", ""),
            "company": lead.get("company", ""),
            "industry": lead.get("industry", ""),
            "lead_state": lead.get("lead_state", ""),
            "source": "lemlist_cold_call",
            "first_contacted": lead.get("first_contacted", "")
        })

# Build flat email lookup
email_map = {}  # email -> {fathom_calls: [], lemlist: {}}

for call in last_100:
    for email in call["emails"]:
        if email not in email_map:
            email_map[email] = {"fathom_calls": [], "lemlist": None}
        email_map[email]["fathom_calls"].append({
            "recording_id": call["recording_id"],
            "title": call["title"],
            "date": call["created_at"][:10],
            "url": call["url"]
        })

for lead in lemlist_contacts:
    email = lead["email"]
    if email not in email_map:
        email_map[email] = {"fathom_calls": [], "lemlist": None}
    email_map[email]["lemlist"] = lead

# Summary
fathom_only = sum(1 for v in email_map.values() if v["fathom_calls"] and not v["lemlist"])
lemlist_only = sum(1 for v in email_map.values() if not v["fathom_calls"] and v["lemlist"])
both = sum(1 for v in email_map.values() if v["fathom_calls"] and v["lemlist"])
print(f"\nTotal unique prospect emails: {len(email_map)}")
print(f"  Fathom only: {fathom_only}")
print(f"  Lemlist only: {lemlist_only}")
print(f"  Both: {both}")

# Save
output = {
    "fathom_calls_count": len(last_100),
    "fathom_date_range": f"{last_100[-1]['created_at'][:10]} to {last_100[0]['created_at'][:10]}",
    "lemlist_leads_count": len(lemlist_contacts),
    "unique_emails": len(email_map),
    "email_map": email_map
}
with open(OUTPUT_FILE, "w") as f:
    json.dump(output, f, indent=2)

print(f"\nSaved to {OUTPUT_FILE}")

# Print all unique emails for HubSpot lookup
all_emails = sorted(email_map.keys())
print(f"\nAll {len(all_emails)} unique emails:")
for e in all_emails:
    print(e)

