#!/usr/bin/env python3
"""
Spoki Sales Cockpit — Local Dashboard
Tracks team pipeline performance from HubSpot.

Usage:
  cd Skills/cockpit
  pip install flask
  python app.py
  → Open http://localhost:5050
"""

import csv
import io
import json
import os
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, render_template

# ─── Config ───────────────────────────────────────────────────────────────────

HUBSPOT_TOKEN  = os.getenv("HUBSPOT_TOKEN", "")
LEMLIST_TOKEN  = os.getenv("LEMLIST_TOKEN", "")
LEMLIST_BASE   = "https://api.lemlist.com/api"
FATHOM_TOKEN   = os.getenv("FATHOM_TOKEN", "")
FATHOM_BASE    = "https://api.fathom.ai/external/v1"
BASE_URL      = "https://api.hubapi.com"
PIPELINE_ID   = "671838099"
TZ            = ZoneInfo("Europe/Rome")
CACHE_TTL     = 300  # seconds (5 min)

STAGES = {
    "986053466":  "Discovery",
    "986053467":  "Demo",
    "986053468":  "Follow-up",
    "2674750700": "Negotiation/Trial",
    "986053469":  "Closed Won",
    "986053470":  "Closed Lost",
}

STAGE_ORDER = ["986053466", "986053467", "986053468", "2674750700"]
STAGE_WON   = "986053469"
STAGE_LOST  = "986053470"

# Friendly names for deal owners
OWNERS = {
    # Italy
    "75722736": "Cristina",
    "75722777": "Giuseppe",
    "31172513": "Marco",
    "30334309": "Vincenzo",
    "31903434": "Bruno",
    "78556068": "Davide",
    "31766930": "G. Cannistraro",
    "29272207": "Greta",
    # Spain / international
    "30727447": "Víctor",
    "30908030": "Manuel",
    "30662769": "Juan Manuel",
    "29797105": "Ana",
    "31920640": "Alejandro",
    "32297908": "Jordi",
    "87805147": "Andres",
    # Other
    "31012966": "Stefano",
    "29426066": "Federica",
    "30133195": "Mattia",
}

# Reps to exclude from the leaderboard (bots, management who don't carry quota)
EXCLUDE_FROM_LB = {"26271015"}  # Spoki App

# ─── Flask app ────────────────────────────────────────────────────────────────

app        = Flask(__name__)
_cache: dict = {}
_data_lock  = threading.Lock()  # prevents parallel HubSpot fetches on cold cache

# ─── Helpers ──────────────────────────────────────────────────────────────────

def month_start_ms() -> int:
    now = datetime.now(TZ)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return int(start.astimezone(timezone.utc).timestamp() * 1000)


def week_start_ms() -> int:
    now = datetime.now(TZ)
    monday = now - timedelta(days=now.weekday())
    start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(start.astimezone(timezone.utc).timestamp() * 1000)


def hs_get(path: str, params: Optional[dict] = None) -> dict:
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def get_owners() -> dict:
    """Fetch all HubSpot owners and return {owner_id_str: first_name last_name}."""
    now = time.time()
    if "owners" in _cache and now - _cache["owners"]["ts"] < 3600:  # 1h cache
        return _cache["owners"]["data"]

    owners_map = dict(OWNERS)  # start with known overrides
    after = None
    for _ in range(20):
        params = {"limit": 100, "archived": "false"}
        if after:
            params["after"] = after
        data   = hs_get("/crm/v3/owners", params)
        for o in data.get("results", []):
            oid  = str(o.get("id", ""))
            fn   = (o.get("firstName") or "").strip()
            ln   = (o.get("lastName") or "").strip()
            name = f"{fn} {ln}".strip() or f"#{oid}"
            if oid not in owners_map:
                owners_map[oid] = name
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break

    _cache["owners"] = {"ts": now, "data": owners_map}
    return owners_map


def hs_post(path: str, payload: dict, _retries: int = 3) -> dict:
    url  = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(
        url, data=data,
        headers={
            "Authorization": f"Bearer {HUBSPOT_TOKEN}",
            "Content-Type":  "application/json",
        },
        method="POST",
    )
    for attempt in range(_retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < _retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s …
                time.sleep(wait)
            else:
                raise


DEAL_PROPS = [
    "dealname", "dealstage", "amount", "closedate",
    "hubspot_owner_id", "hs_deal_stage_probability",
    "hs_lastmodifieddate", "createdate", "dealtype",
    "spoki_contact_source",
]

# Canonical source labels for display
SOURCE_LABELS = {
    "Inbound":      "Inbound",
    "Outbound":     "Outbound",
    "product_led":  "Product Led",
    "partner":      "Partner",
}

# Filter that excludes existing-business/renewal deals from every query
NB_FILTER = {"propertyName": "dealtype", "operator": "NEQ", "value": "existingbusiness"}


def hs_search_all(filters: list, sorts: Optional[list] = None, max_pages: int = 20) -> list:
    """Paginate through all results of a HubSpot deal search."""
    results = []
    after   = None
    payload = {
        "filterGroups": [{"filters": filters}],
        "sorts":        sorts or [{"propertyName": "hs_lastmodifieddate", "direction": "DESCENDING"}],
        "properties":   DEAL_PROPS,
        "limit":        100,
    }
    for _ in range(max_pages):
        if after:
            payload["after"] = after
        data = hs_post("/crm/v3/objects/deals/search", payload)
        results.extend(data.get("results", []))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
    return results


# ─── Data layer ───────────────────────────────────────────────────────────────

def get_all_data() -> dict:
    """Fetch all required deals from HubSpot, with 5-min caching.
    Lock ensures only one thread does the HubSpot fetch on a cold cache —
    all other threads wait and then read from cache (double-checked locking)."""
    now = time.time()
    if "deals" in _cache and now - _cache["deals"]["ts"] < CACHE_TTL:
        return _cache["deals"]["data"]

    with _data_lock:
        # Re-check inside the lock — another thread may have populated cache
        now = time.time()
        if "deals" in _cache and now - _cache["deals"]["ts"] < CACHE_TTL:
            return _cache["deals"]["data"]

        ms  = month_start_ms()
        wk  = week_start_ms()
        # 8 weeks back (for trend chart)
        eight_wk_ago = datetime.now(TZ) - timedelta(weeks=8)
        eight_wk_ago = eight_wk_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        eight_wk_ms  = int(eight_wk_ago.astimezone(timezone.utc).timestamp() * 1000)

        # 1. All open deals in the pipeline (new business only)
        open_deals = hs_search_all([
            {"propertyName": "pipeline",  "operator": "EQ",  "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "NEQ", "value": STAGE_WON},
            {"propertyName": "dealstage", "operator": "NEQ", "value": STAGE_LOST},
            NB_FILTER,
        ])

        # 2. Won deals — current month (new business only)
        won_month = hs_search_all([
            {"propertyName": "pipeline",  "operator": "EQ",  "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ",  "value": STAGE_WON},
            {"propertyName": "closedate", "operator": "GTE", "value": str(ms)},
            NB_FILTER,
        ])

        # 3. Lost deals — current month (new business only)
        lost_month = hs_search_all([
            {"propertyName": "pipeline",  "operator": "EQ",  "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ",  "value": STAGE_LOST},
            {"propertyName": "closedate", "operator": "GTE", "value": str(ms)},
            NB_FILTER,
        ])

        # 4. Won deals — current week (new business only)
        won_week = hs_search_all([
            {"propertyName": "pipeline",  "operator": "EQ",  "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ",  "value": STAGE_WON},
            {"propertyName": "closedate", "operator": "GTE", "value": str(wk)},
            NB_FILTER,
        ])

        # 5. All deals created this month (new business only) — new pipeline per rep
        created_month = hs_search_all([
            {"propertyName": "pipeline",  "operator": "EQ",  "value": PIPELINE_ID},
            {"propertyName": "createdate","operator": "GTE", "value": str(ms)},
            NB_FILTER,
        ])

        # 6. Won deals — last 8 weeks (new business only) — for weekly trend chart
        won_8weeks = hs_search_all([
            {"propertyName": "pipeline",  "operator": "EQ",  "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ",  "value": STAGE_WON},
            {"propertyName": "closedate", "operator": "GTE", "value": str(eight_wk_ms)},
            NB_FILTER,
        ])

        data = {
            "open":          open_deals,
            "won_month":     won_month,
            "lost_month":    lost_month,
            "won_week":      won_week,
            "created_month": created_month,
            "won_8weeks":    won_8weeks,
            "fetched_at":    datetime.now(TZ).strftime("%d %b %H:%M:%S"),
        }
        _cache["deals"] = {"ts": now, "data": data}
        return data


def safe_float(val) -> float:
    try:
        return float(val or 0)
    except (ValueError, TypeError):
        return 0.0


# ─── Lemlist helpers ──────────────────────────────────────────────────────────

import base64 as _b64

def lemlist_get(path: str) -> bytes:
    """GET request to Lemlist API using basic auth (empty user, token as password)."""
    import base64
    url  = f"{LEMLIST_BASE}{path}"
    auth = base64.b64encode(f":{LEMLIST_TOKEN}".encode()).decode()
    req  = urllib.request.Request(url, headers={
        "Authorization": f"Basic {auth}",
        "User-Agent":    "Mozilla/5.0 (compatible; cockpit-dashboard/1.0)",
        "Accept":        "application/json, text/csv, */*",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def get_cold_calls() -> dict:
    """Returns {rep_name: {"7d": N, "opps_7d": N}} from Lemlist cold-call campaigns — rolling 7 days."""
    now = time.time()
    if "cold_calls" in _cache and now - _cache["cold_calls"]["ts"] < CACHE_TTL:
        return _cache["cold_calls"]["data"]

    try:
        camps = json.loads(lemlist_get("/campaigns?limit=100"))
    except Exception:
        return {}

    cold_camps = [
        c for c in camps
        if not c.get("archived")
        and "cold" in c.get("name", "").lower()
        and "call" in c.get("name", "").lower()
    ]

    now_dt     = datetime.now(TZ)
    seven_days = now_dt - timedelta(days=7)

    reps: dict = {}

    for camp in cold_camps:
        try:
            raw    = lemlist_get(f"/campaigns/{camp['_id']}/export")
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
            call_cols: Optional[list] = None
            interested_cols: Optional[list] = None
            for row in reader:
                if call_cols is None:
                    call_cols       = [k for k in row.keys() if k.startswith("callDoneAt")]
                    interested_cols = [
                        k for k in row.keys()
                        if ("InterestedAt" in k or k == "interestedAt")
                        and "Not" not in k
                        and not k.startswith("linkedin")
                        and not k.startswith("api")
                    ]
                send_user = (row.get("sendUser") or "").split(":")[0].strip()
                if not send_user:
                    continue
                if send_user not in reps:
                    reps[send_user] = {"7d": 0, "opps_7d": 0}

                # Count calls (deduplicated by timestamp)
                seen: set = set()
                for col in call_cols:
                    val = (row.get(col) or "").strip()
                    if not val or val in seen:
                        continue
                    seen.add(val)
                    try:
                        dt = datetime.fromisoformat(val.replace("Z", "+00:00")).astimezone(TZ)
                        if dt >= seven_days:
                            reps[send_user]["7d"] += 1
                    except Exception:
                        pass

                # Count opportunities (once per lead, rolling 7 days)
                opp_counted = False
                for col in interested_cols:
                    if opp_counted:
                        break
                    val = (row.get(col) or "").strip()
                    if not val:
                        continue
                    try:
                        dt = datetime.fromisoformat(val.replace("Z", "+00:00")).astimezone(TZ)
                        if dt >= seven_days:
                            reps[send_user]["opps_7d"] += 1
                            opp_counted = True
                    except Exception:
                        pass
        except Exception:
            pass

    _cache["cold_calls"] = {"ts": now, "data": reps}
    return reps


def get_meetings() -> dict:
    """Returns {rep_name: {"7d": N}} from Fathom — Sales team only, rolling 7 days."""
    now = time.time()
    if "meetings" in _cache and now - _cache["meetings"]["ts"] < CACHE_TTL:
        return _cache["meetings"]["data"]

    try:
        import requests as req_lib
    except ImportError:
        return {}

    now_dt     = datetime.now(TZ)
    seven_days = now_dt - timedelta(days=7)

    reps: dict = {}
    cursor: Optional[str] = None

    while True:
        params: dict = {"limit": 100, "created_after": seven_days.isoformat()}
        if cursor:
            params["cursor"] = cursor
        try:
            resp = req_lib.get(
                f"{FATHOM_BASE}/meetings",
                headers={"X-Api-Key": FATHOM_TOKEN},
                params=params,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            break

        for item in data.get("items", []):
            recorded_by = item.get("recorded_by") or {}
            if recorded_by.get("team") != "Sales":
                continue
            name = recorded_by.get("name", "").strip()
            if not name:
                continue
            created_at = item.get("created_at", "")
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(TZ)
            except Exception:
                continue
            if name not in reps:
                reps[name] = {"7d": 0}
            if dt >= seven_days:
                reps[name]["7d"] += 1

        cursor = data.get("next_cursor")
        if not cursor:
            break

    _cache["meetings"] = {"ts": now, "data": reps}
    return reps


# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.route("/api/summary")
def api_summary():
    data = get_all_data()

    open_deals  = data["open"]
    won_month   = data["won_month"]
    lost_month  = data["lost_month"]
    won_week    = data["won_week"]

    total_pipeline = sum(safe_float(d["properties"].get("amount")) for d in open_deals)
    weighted       = sum(
        safe_float(d["properties"].get("amount")) *
        safe_float(d["properties"].get("hs_deal_stage_probability"))
        for d in open_deals
    )
    won_value_month = sum(safe_float(d["properties"].get("amount")) for d in won_month)
    won_value_week  = sum(safe_float(d["properties"].get("amount")) for d in won_week)

    # Deals closing this calendar month — count + value + weighted
    now = datetime.now(TZ)
    closing_this_month       = 0
    closing_this_month_value = 0.0
    closing_this_month_wtd   = 0.0
    for d in open_deals:
        cd = d["properties"].get("closedate")
        if cd:
            try:
                dt = datetime.fromisoformat(cd.replace("Z", "+00:00")).astimezone(TZ)
                if dt.year == now.year and dt.month == now.month:
                    closing_this_month += 1
                    amt  = safe_float(d["properties"].get("amount"))
                    prob = safe_float(d["properties"].get("hs_deal_stage_probability"))
                    closing_this_month_value += amt
                    closing_this_month_wtd   += amt * prob
            except Exception:
                pass

    total_closed = len(won_month) + len(lost_month)
    win_rate     = round(len(won_month) / total_closed * 100, 1) if total_closed else 0

    return jsonify({
        "total_pipeline":            round(total_pipeline, 0),
        "weighted_forecast":         round(weighted, 0),
        "won_count_month":           len(won_month),
        "won_value_month":           round(won_value_month, 0),
        "won_count_week":            len(won_week),
        "won_value_week":            round(won_value_week, 0),
        "open_count":                len(open_deals),
        "closing_this_month":        closing_this_month,
        "closing_this_month_value":  round(closing_this_month_value, 0),
        "closing_this_month_wtd":    round(closing_this_month_wtd, 0),
        "win_rate":                  win_rate,
        "total_closed":              total_closed,
        "fetched_at":                data["fetched_at"],
    })


@app.route("/api/funnel")
def api_funnel():
    data       = get_all_data()
    open_deals = data["open"]

    stages = {sid: {"name": STAGES[sid], "count": 0, "value": 0.0}
              for sid in STAGE_ORDER}

    for deal in open_deals:
        sid = deal["properties"].get("dealstage", "")
        if sid in stages:
            stages[sid]["count"] += 1
            stages[sid]["value"] += safe_float(deal["properties"].get("amount"))

    return jsonify([
        {"stage": v["name"], "count": v["count"], "value": round(v["value"], 0)}
        for v in stages.values()
    ])


@app.route("/api/leaderboard")
def api_leaderboard():
    data   = get_all_data()
    owners = get_owners()
    reps: dict = {}

    def rep(owner_id: str) -> dict:
        if owner_id not in reps:
            reps[owner_id] = {
                "owner_id":   owner_id,
                "name":       owners.get(owner_id, f"#{owner_id}"),
                "won_count":  0, "won_value":  0.0,
                "lost_count": 0,
                "open_count": 0, "open_value": 0.0,
                "new_deals":  0,
                "won_days":   0,  # sum of days-to-close for avg calc
                # source breakdown for open pipeline deals
                "sources": {"Inbound": 0, "Outbound": 0, "product_led": 0, "partner": 0},
            }
        return reps[owner_id]

    for d in data["won_month"]:
        oid = str(d["properties"].get("hubspot_owner_id") or "").strip()
        if not oid or oid in EXCLUDE_FROM_LB:
            continue
        r = rep(oid)
        r["won_count"] += 1
        r["won_value"] += safe_float(d["properties"].get("amount"))
        try:
            created  = d["properties"].get("createdate") or ""
            closed   = d["properties"].get("closedate")  or ""
            if created and closed:
                dt_c = datetime.fromisoformat(created.replace("Z", "+00:00"))
                dt_w = datetime.fromisoformat(closed.replace("Z",  "+00:00"))
                r["won_days"] += max(0, (dt_w - dt_c).days)
        except Exception:
            pass

    for d in data["lost_month"]:
        oid = str(d["properties"].get("hubspot_owner_id") or "").strip()
        if not oid or oid in EXCLUDE_FROM_LB:
            continue
        rep(oid)["lost_count"] += 1

    for d in data["open"]:
        oid = str(d["properties"].get("hubspot_owner_id") or "").strip()
        if not oid or oid in EXCLUDE_FROM_LB:
            continue
        r = rep(oid)
        r["open_count"] += 1
        r["open_value"] += safe_float(d["properties"].get("amount"))
        src = (d["properties"].get("spoki_contact_source") or "").strip()
        if src in r["sources"]:
            r["sources"][src] += 1

    for d in data["created_month"]:
        oid = str(d["properties"].get("hubspot_owner_id") or "").strip()
        if not oid or oid in EXCLUDE_FROM_LB:
            continue
        rep(oid)["new_deals"] += 1

    board = []
    for r in reps.values():
        total = r["won_count"] + r["lost_count"]
        board.append({
            **r,
            "won_value":     round(r["won_value"], 0),
            "open_value":    round(r["open_value"], 0),
            "win_rate":          round(r["won_count"] / total * 100, 1) if total else None,
            "avg_deal_size":     round(r["won_value"] / r["won_count"], 0) if r["won_count"] else None,
            "avg_days_to_close": round(r["won_days"] / r["won_count"]) if r["won_count"] else None,
            "sources":           r["sources"],
        })

    board.sort(key=lambda x: x["won_value"], reverse=True)
    return jsonify(board)


@app.route("/api/recent-wins")
def api_recent_wins():
    data   = get_all_data()
    owners = get_owners()
    wins   = sorted(
        data["won_month"],
        key=lambda d: d["properties"].get("closedate") or "",
        reverse=True,
    )[:15]

    hs_base = "https://app-eu1.hubspot.com/contacts/47964451/record/0-3"
    return jsonify([
        {
            "name":      d["properties"].get("dealname", "—"),
            "amount":    safe_float(d["properties"].get("amount")),
            "owner":     owners.get(str(d["properties"].get("hubspot_owner_id", "")), "—"),
            "closedate": (d["properties"].get("closedate") or "")[:10],
            "url":       f"{hs_base}/{d['id']}",
        }
        for d in wins
    ])


@app.route("/api/stale")
def api_stale():
    """Open deals with no HubSpot modification in 7+ days."""
    data      = get_all_data()
    owners    = get_owners()
    threshold = time.time() - (7 * 86400)
    hs_base   = "https://app-eu1.hubspot.com/contacts/47964451/record/0-3"
    stale     = []

    for d in data["open"]:
        last_mod = d["properties"].get("hs_lastmodifieddate", "")
        if not last_mod:
            continue
        try:
            ts = datetime.fromisoformat(last_mod.replace("Z", "+00:00")).timestamp()
            if ts < threshold:
                stale.append({
                    "name":          d["properties"].get("dealname", "—"),
                    "stage":         STAGES.get(d["properties"].get("dealstage", ""), "—"),
                    "amount":        safe_float(d["properties"].get("amount")),
                    "owner":         owners.get(str(d["properties"].get("hubspot_owner_id", "")), "—"),
                    "last_modified": last_mod[:10],
                    "days_stale":    int((time.time() - ts) / 86400),
                    "url":           f"{hs_base}/{d['id']}",
                })
        except Exception:
            pass

    stale.sort(key=lambda x: x["days_stale"], reverse=True)
    return jsonify(stale[:25])


@app.route("/api/at-risk")
def api_at_risk():
    """
    Deals that need immediate manager attention:
    - Any open deal whose close date has already passed (slipped forecast)
    - Negotiation/Trial deals with no activity in 5+ days (hot deals going cold)
    Sorted by urgency score (overdue days + deal amount proxy).
    """
    data     = get_all_data()
    owners   = get_owners()
    now_ts   = time.time()
    hs_base  = "https://app-eu1.hubspot.com/contacts/47964451/record/0-3"
    STAGE_LATE  = "2674750700"   # Negotiation/Trial
    COLD_DAYS   = 5              # days idle before a late-stage deal is "at risk"

    at_risk = []
    for d in data["open"]:
        props     = d["properties"]
        stage     = props.get("dealstage", "")
        last_mod  = props.get("hs_lastmodifieddate", "") or ""
        closedate = props.get("closedate", "") or ""
        amount    = safe_float(props.get("amount"))
        owner     = owners.get(str(props.get("hubspot_owner_id", "")), "—")

        reasons = []
        urgency = 0

        # Risk 1: close date already passed
        if closedate:
            try:
                cd_ts = datetime.fromisoformat(closedate.replace("Z", "+00:00")).timestamp()
                days_over = int((now_ts - cd_ts) / 86400)
                if days_over > 0:
                    reasons.append({"type": "overdue", "label": f"Past due {days_over}d"})
                    urgency += 10 + days_over
            except Exception:
                pass

        # Risk 2: late stage + not touched in COLD_DAYS days
        if stage == STAGE_LATE and last_mod:
            try:
                lm_ts     = datetime.fromisoformat(last_mod.replace("Z", "+00:00")).timestamp()
                idle_days = int((now_ts - lm_ts) / 86400)
                if idle_days >= COLD_DAYS:
                    reasons.append({"type": "cold", "label": f"Late stage idle {idle_days}d"})
                    urgency += idle_days
            except Exception:
                pass

        if reasons:
            at_risk.append({
                "name":    props.get("dealname", "—"),
                "stage":   STAGES.get(stage, "—"),
                "amount":  amount,
                "owner":   owner,
                "reasons": reasons,
                "urgency": urgency,
                "url":     f"{hs_base}/{d['id']}",
            })

    at_risk.sort(key=lambda x: (-x["urgency"], -x["amount"]))
    return jsonify(at_risk[:30])


@app.route("/api/weekly-trend")
def api_weekly_trend():
    """Won deals per week for the last 8 weeks — shows momentum."""
    data = get_all_data()
    now  = datetime.now(TZ)

    # Build 8 Monday-anchored week buckets, oldest first
    weeks = []
    for i in range(7, -1, -1):
        wk_start = now - timedelta(weeks=i)
        wk_start = wk_start - timedelta(days=wk_start.weekday())  # align to Monday
        wk_start = wk_start.replace(hour=0, minute=0, second=0, microsecond=0)
        wk_end   = wk_start + timedelta(days=7)
        weeks.append({
            "start":  wk_start,
            "end":    wk_end,
            "label":  wk_start.strftime("%-d %b"),
            "count":  0,
            "value":  0.0,
        })

    for d in data["won_8weeks"]:
        cd = d["properties"].get("closedate")
        if not cd:
            continue
        try:
            dt = datetime.fromisoformat(cd.replace("Z", "+00:00")).astimezone(TZ)
            for w in weeks:
                if w["start"] <= dt < w["end"]:
                    w["count"] += 1
                    w["value"] += safe_float(d["properties"].get("amount"))
                    break
        except Exception:
            pass

    return jsonify([
        {"label": w["label"], "count": w["count"], "value": round(w["value"], 0)}
        for w in weeks
    ])


@app.route("/api/activity")
def api_activity():
    """Team activity: cold calls per rep from Lemlist + meetings from Fathom."""
    calls    = get_cold_calls()
    meetings = get_meetings()
    # Merge: build unified rep set from both sources
    all_reps = set(calls.keys()) | set(meetings.keys())
    result = []
    for name in all_reps:
        c = calls.get(name, {"7d": 0, "opps_7d": 0})
        m = meetings.get(name, {"7d": 0})
        result.append({
            "name":         name,
            "calls_7d":     c["7d"],
            "opps_7d":      c.get("opps_7d", 0),
            "meetings_7d":  m["7d"],
        })
    result.sort(key=lambda x: -x["calls_7d"])
    return jsonify(result)


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """Bust all caches and force a fresh fetch on the next request."""
    _cache.clear()
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    return render_template("index.html")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀  Spoki Sales Cockpit → http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=False)
