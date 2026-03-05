#!/usr/bin/env python3
"""
Lemlist Puller — pull campaign stats and lead engagement data from Lemlist
API: https://api.lemlist.com/api
Auth: Basic auth with empty username and API key as password: ('', KEY)

What we can get:
  - Campaign list (38 campaigns)
  - Lead states per campaign (scanned → emailed → opened → replied etc.)
  - Contact details including engagement timeline

Lead states:
  scanned         → added to campaign (sequence started)
  inProgress      → currently in sequence
  emailsOpened    → opened at least one email
  interested      → replied positively (hot lead)
  notInterested   → unsubscribed / opted out
  done            → completed sequence
  review          → in manual review queue
  reviewed        → reviewed manually
  paused          → paused
  stopped         → stopped

Note: The /activities endpoint returns HTML (not implemented in public API).
      Stats are derived from counting lead states.
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from collections import Counter

# ── Config ──────────────────────────────────────────────────────────────────
LEMLIST_API_KEY = os.getenv("LEMLIST_API_KEY", "YOUR_LEMLIST_API_KEY")
BASE_URL = "https://api.lemlist.com/api"
OUTPUT_DIR = Path("output/lemlist")
RATE_SLEEP = 0.5

AUTH = ("", LEMLIST_API_KEY)  # Basic auth: empty username, key as password


def _get(path, params=None, timeout=30):
    resp = requests.get(f"{BASE_URL}{path}", auth=AUTH, params=params or {}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# ── Pull campaigns ────────────────────────────────────────────────────────────
def get_campaigns():
    data = _get("/campaigns")
    return data if isinstance(data, list) else data.get("campaigns", [])


# ── Count lead states for a campaign (= engagement stats) ────────────────────
def get_campaign_stats(campaign_id: str, campaign_name: str, max_pages: int = 20) -> dict:
    """
    Paginate through leads (capped at max_pages × 100) and count states.
    Some campaigns have 37k+ leads so we cap at 2000 leads (20 pages) for a
    representative sample — enough to compute reliable engagement rates.

    Derived mapping:
      scanned + inProgress  → sent
      emailsOpened          → opened
      interested            → replied (positive / hot)
      notInterested         → opted out
      done                  → sequence completed
    """
    state_counts = Counter()
    offset = 0
    limit = 100
    pages = 0

    while pages < max_pages:
        try:
            leads = _get(
                f"/campaigns/{campaign_id}/leads",
                params={"limit": limit, "offset": offset},
                timeout=10,
            )
        except (requests.HTTPError, requests.Timeout) as e:
            print(f"    HTTP error — {campaign_name}: {e}")
            break

        if not isinstance(leads, list) or not leads:
            break

        for lead in leads:
            state_counts[lead.get("state", "unknown")] += 1

        offset += len(leads)
        pages += 1
        if len(leads) < limit:
            break

    total = sum(state_counts.values())
    # Leads with email activity (opened, clicked, replied, interested)
    engaged = (
        state_counts.get("emailsOpened", 0)
        + state_counts.get("emailsClicked", 0)
        + state_counts.get("emailsReplied", 0)
        + state_counts.get("emailsInterested", 0)
        + state_counts.get("emailsNotInterested", 0)
    )
    sent = engaged + state_counts.get("emailsSent", 0)  # at least emailed
    opened = engaged  # everyone in engaged bucket opened at minimum
    replied = state_counts.get("emailsReplied", 0) + state_counts.get("emailsInterested", 0)
    interested = state_counts.get("emailsInterested", 0)
    not_interested = state_counts.get("emailsNotInterested", 0) + state_counts.get("variableUnsubscribed", 0)
    linkedin_done = state_counts.get("linkedinVisitDone", 0)

    return {
        "total_leads": total,
        "sent": sent,
        "opened": opened,
        "open_rate_pct": round(opened / sent * 100, 1) if sent else 0,
        "replied": replied,
        "interested": interested,
        "reply_rate_pct": round(replied / sent * 100, 1) if sent else 0,
        "not_interested": not_interested,
        "linkedin_done": linkedin_done,
        "state_breakdown": dict(state_counts),
    }


# ── Pull full campaign summary ────────────────────────────────────────────────
def pull_campaign_summary():
    if not LEMLIST_API_KEY:
        print("ERROR: LEMLIST_API_KEY not set.")
        return []

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("LEMLIST — pulling campaign stats")
    print(f"{'='*60}\n")

    campaigns = get_campaigns()
    print(f"  Found {len(campaigns)} campaigns\n")

    summary = []
    for i, camp in enumerate(campaigns, 1):
        cid = camp.get("_id") or camp.get("id")
        cname = camp.get("name", "unnamed")
        status = camp.get("status", "?")

        print(f"  [{i}/{len(campaigns)}] {cname} ({status})...", end=" ", flush=True)

        stats = get_campaign_stats(cid, cname)
        entry = {
            "_id": cid,
            "name": cname,
            "status": status,
            "created_at": camp.get("createdAt"),
            **stats,
        }
        summary.append(entry)
        print(
            f"{stats['total_leads']} leads | "
            f"{stats['opened']} opens ({stats['open_rate_pct']}%) | "
            f"{stats['replied']} replies ({stats['reply_rate_pct']}%)"
        )
        time.sleep(RATE_SLEEP)

    # Sort by total leads desc
    summary.sort(key=lambda x: x["total_leads"], reverse=True)

    out_path = OUTPUT_DIR / "campaigns_summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n  Saved → {out_path}")
    return summary


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    summary = pull_campaign_summary()

    print("\n" + "=" * 60)
    print("CAMPAIGN PERFORMANCE OVERVIEW")
    print("=" * 60)

    active = [c for c in summary if c["status"] in ("running", "paused", "ended")]
    total_leads = sum(c["total_leads"] for c in active)
    total_opened = sum(c["opened"] for c in active)
    total_replied = sum(c["replied"] for c in active)
    total_interested = sum(c["interested"] for c in active)

    print(f"\n  Active campaigns: {len(active)}")
    print(f"  Total leads:      {total_leads:,}")
    print(f"  Total opens:      {total_opened:,} ({total_opened/total_leads*100:.1f}%)" if total_leads else "")
    print(f"  Total replies:    {total_replied:,} ({total_replied/total_leads*100:.1f}%)" if total_leads else "")
    print(f"  Positive replies: {total_interested:,} ({total_interested/total_leads*100:.1f}%)" if total_leads else "")

    print("\n  Top campaigns by replies:")
    for camp in sorted(active, key=lambda x: x["replied"], reverse=True)[:10]:
        print(
            f"    {camp['name']:45s} | "
            f"{camp['total_leads']:4d} leads | "
            f"{camp['replied']:3d} replies ({camp['reply_rate_pct']}%)"
        )

    print(f"\nDone. Run: python scripts/run_call_intelligence.py --skip-lemlist")
