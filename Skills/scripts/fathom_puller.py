#!/usr/bin/env python3
"""
Fathom Puller — pull meeting transcripts via Fathom API
API base: https://api.fathom.ai/external/v1
Auth:     X-Api-Key header

Fathom field map (actual API response):
  recording_id          → unique ID
  meeting_title         → full title (e.g. "Spoki | Chiamata conoscitiva")
  title                 → short title (calendar event name)
  created_at            → ISO8601 timestamp
  recorded_by           → {name, email, email_domain, team}  ← the REP
  calendar_invitees     → [{name, email, is_external, matched_speaker_display_name}]
  transcript            → [{speaker: {display_name, matched_calendar_invitee_email}, text, timestamp}]
  default_summary       → null | summary text
  action_items          → list
  crm_matches           → null | {contacts, companies, deals}
  share_url             → permalink
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta

# ── Config ──────────────────────────────────────────────────────────────────
FATHOM_API_KEY = os.getenv(
    "FATHOM_API_KEY",
    "YOUR_FATHOM_API_KEY",
)
BASE_URL = "https://api.fathom.ai/external/v1"
OUTPUT_DIR = Path("output/calls")
RATE_SLEEP = 0.6  # ~60 req/min → 1 req/s to be safe

HEADERS = {"X-Api-Key": FATHOM_API_KEY}

# Default: only pull meetings from the last 180 days to keep it manageable
# Override with --after flag for a full historical pull
DEFAULT_DAYS_BACK = 180


# ── API helpers ───────────────────────────────────────────────────────────────
def get_meetings_page(cursor=None, created_after=None, recorded_by=None):
    params = {"include_transcript": "true"}
    if cursor:
        params["cursor"] = cursor
    if created_after:
        params["created_after"] = created_after
    if recorded_by:
        # Filter by specific rep email(s) — reduces noise
        if isinstance(recorded_by, list):
            for email in recorded_by:
                params.setdefault("recorded_by[]", []).append(email)
        else:
            params["recorded_by[]"] = recorded_by

    resp = requests.get(
        f"{BASE_URL}/meetings", headers=HEADERS, params=params, timeout=30
    )
    resp.raise_for_status()
    return resp.json()


# ── Core pull ─────────────────────────────────────────────────────────────────
def pull_all_meetings(
    created_after=None,
    force_refresh=False,
    recorded_by_emails=None,
    max_meetings=None,
):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Default: last 180 days if no date given
    if not created_after:
        cutoff = datetime.utcnow() - timedelta(days=DEFAULT_DAYS_BACK)
        created_after = cutoff.strftime("%Y-%m-%dT00:00:00Z")

    print(f"\n{'='*60}")
    print("FATHOM PULLER")
    print(f"  From:     {created_after}")
    print(f"  Filter:   {recorded_by_emails or 'all reps'}")
    print(f"  Max:      {max_meetings or 'unlimited'}")
    print(f"{'='*60}\n")

    all_meetings = []
    cursor = None
    page = 0
    new_saved = 0
    cached = 0

    while True:
        page += 1
        print(f"  Page {page}...", end=" ", flush=True)

        try:
            data = get_meetings_page(
                cursor=cursor,
                created_after=created_after,
                recorded_by=recorded_by_emails,
            )
        except requests.HTTPError as e:
            print(f"\n  HTTP ERROR: {e.response.status_code} — {e.response.text[:200]}")
            break

        items = data.get("items", [])
        if not items:
            print("0 meetings — done.")
            break

        all_meetings.extend(items)
        print(f"{len(items)} meetings (total: {len(all_meetings)})")

        for meeting in items:
            mid = meeting.get("recording_id") or "unknown"
            fname = OUTPUT_DIR / f"{mid}.json"

            if fname.exists() and not force_refresh:
                cached += 1
                continue

            with open(fname, "w") as f:
                json.dump(meeting, f, indent=2, ensure_ascii=False)
            new_saved += 1

        if max_meetings and len(all_meetings) >= max_meetings:
            print(f"\n  Reached max_meetings limit ({max_meetings})")
            break

        cursor = data.get("next_cursor")
        if not cursor:
            break

        time.sleep(RATE_SLEEP)

    # Save index
    index = {
        "pulled_at": datetime.now().isoformat(),
        "created_after": created_after,
        "total": len(all_meetings),
        "new_saved": new_saved,
        "cached": cached,
        "meetings": [
            {
                "id": m.get("recording_id"),
                "title": m.get("meeting_title") or m.get("title"),
                "date": m.get("created_at"),
                "rep": (m.get("recorded_by") or {}).get("name"),
                "rep_team": (m.get("recorded_by") or {}).get("team"),
                "external_participants": [
                    inv.get("name") or inv.get("email")
                    for inv in (m.get("calendar_invitees") or [])
                    if inv.get("is_external")
                ],
                "has_transcript": bool(m.get("transcript")),
                "share_url": m.get("share_url"),
            }
            for m in all_meetings
        ],
    }

    with open(OUTPUT_DIR / "index.json", "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"\n  New: {new_saved} | Cached: {cached} | Total: {len(all_meetings)}")
    print(f"  Saved to: {OUTPUT_DIR}/")
    return all_meetings


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pull Fathom meeting transcripts")
    parser.add_argument(
        "--after",
        default=None,
        help="Fetch meetings created after this date (ISO8601, e.g. 2025-09-01). Default: last 180 days.",
    )
    parser.add_argument("--refresh", action="store_true", help="Re-fetch even if cached")
    parser.add_argument(
        "--rep",
        action="append",
        default=None,
        metavar="EMAIL",
        help="Filter by rep email (can repeat: --rep a@co.com --rep b@co.com)",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        help="Max meetings to pull (useful for testing)",
    )
    args = parser.parse_args()

    meetings = pull_all_meetings(
        created_after=args.after,
        force_refresh=args.refresh,
        recorded_by_emails=args.rep,
        max_meetings=args.max,
    )

    print(f"\nDone. {len(meetings)} meetings ready.")
    print("Next step: python scripts/call_analyzer.py")
