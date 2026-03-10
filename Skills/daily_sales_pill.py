#!/usr/bin/env python3
"""
Daily Sales Pill — Google Chat
Sends daily HubSpot-powered sales tips to the Google Chat sales channel.
Schedule: 10am Mon–Fri Europe/Rome via crontab or macOS launchd.

Usage:
  python3 daily_sales_pill.py           # auto-detects today's pill
  python3 daily_sales_pill.py --day mon  # force a specific day
"""

import json
import base64
import os
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import sys
import argparse

# ─── Config ───────────────────────────────────────────────────────────────────
HUBSPOT_TOKEN  = os.getenv("HUBSPOT_TOKEN", "")
LEMLIST_KEY    = os.getenv("LEMLIST_KEY", "")
FATHOM_KEY     = os.getenv("FATHOM_KEY", "")
ANTHROPIC_KEY  = os.getenv("ANTHROPIC_API_KEY", "")   # set in crontab or shell profile
OPENAI_KEY     = os.getenv("OPENAI_API_KEY", "")      # alternative — uses gpt-4o-mini
# Keywords that flag post-sale calls (scored lower in rep scorecard)
_POST_SALE_KW  = ("onboarding", "training", "activation", "activación",
                  "activacion", "formazione", "ativação", "llamada de activación")
# Keywords that flag internal meetings — skip entirely from Best Call
_INTERNAL_KW   = ("spoki team", "team meeting", "internal",
                  "1:1", "one on one", "sync", "standup", "stand-up",
                  "riunione", "weekly", "planning", "retrospective")
GOOGLE_CHAT_WEBHOOK = (
    "https://chat.googleapis.com/v1/spaces/AAQAhq1kBCw/messages"
    "?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI"
    "&token=Jf_WY5tsWYm9Z5qIM2o1Qs0jHURvuHdVw7lvGPCc7IM"
)
PIPELINE_ID = "671838099"
STAGES = {
    "986053466": "Discovery",
    "986053467": "Demo",
    "986053468": "Follow-up",
    "2674750700": "Negotiation/Trial",
    "986053469": "Closed Won",
    "986053470": "Closed Lost",
}
OWNERS = {
    # Italy sales
    "75722736": "Cristina",
    "75722777": "Giuseppe",
    "31172513": "Marco",
    "30334309": "Vincenzo",
    "31903434": "Bruno",
    "78556068": "Davide",
    "31766930": "G. Cannistraro",
    "29272207": "Greta",
    # Spain / international sales
    "30727447": "Víctor",
    "30908030": "Manuel",
    "30662769": "Juan Manuel",
    "29797105": "Ana",
    "31920640": "Alejandro",
    "32297908": "Jordi",
    "87805147": "Andres",
    # Other / management
    "31012966": "Stefano",
    "29426066": "Federica",
}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def fmt_eur(value):
    try:
        return f"€{int(float(value)):,}".replace(",", ".")
    except Exception:
        return "€0"

def fmt_k(value):
    """Format as €Xk or €X.Xk for compact inline use."""
    try:
        v = float(value)
        if v >= 1000:
            k = round(v / 1000, 1)
            return f"€{k:.0f}k" if k == int(k) else f"€{k:.1f}k"
        return f"€{int(v)}"
    except Exception:
        return "€?"


def fmt_date(iso_str):
    if not iso_str:
        return "no date"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d %b")
    except Exception:
        return iso_str[:10]


def _week_start_ms():
    """Monday 00:00 Europe/Rome of the current week, as Unix ms (for HubSpot filters)."""
    from zoneinfo import ZoneInfo
    now_rome = datetime.now(ZoneInfo("Europe/Rome"))
    monday   = now_rome - timedelta(days=now_rome.weekday())   # weekday(): 0=Mon
    midnight = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(midnight.astimezone(timezone.utc).timestamp() * 1000)


def owner_name(owner_id):
    return OWNERS.get(str(owner_id), f"owner_{owner_id}")


def stage_name(stage_id):
    return STAGES.get(str(stage_id), stage_id)


def hs_search(filters, sorts, properties, limit=6):
    payload = json.dumps({
        "filterGroups": [{"filters": filters}],
        "properties": properties,
        "sorts": sorts,
        "limit": limit,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.hubapi.com/crm/v3/objects/deals/search",
        data=payload,
        headers={
            "Authorization": f"Bearer {HUBSPOT_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def send_to_gchat(text):
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        GOOGLE_CHAT_WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


OBSIDIAN_PILLS_DIR = os.path.expanduser(
    "~/Documents/Vault Brain/GTM/Sales Pills"
)

DAY_TOPICS = {
    "monday":    "🧹 Data Hygiene",
    "tuesday":   "🌱 New Pipeline Feed",
    "wednesday": "🔥 Big Deal Push",
    "thursday":  "⏱ Stage Velocity",
    "friday":    "🏆 Week Recap",
}


def log_to_obsidian(day_label, message):
    """Append the sent pill to an Obsidian daily log file."""
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Europe/Rome"))
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        topic    = DAY_TOPICS.get(day_label, day_label.capitalize())

        # One file per week: Sales Pills/YYYY-Www.md
        week_str  = now.strftime("%Y-W%V")
        log_path  = os.path.join(OBSIDIAN_PILLS_DIR, f"{week_str}.md")

        # Strip Google Chat bold/italic markers for clean markdown
        clean = message.replace("*", "**").replace("_", "*")

        entry = (
            f"\n---\n\n"
            f"## {date_str} · {time_str} — {topic}\n\n"
            f"{clean}\n"
        )

        os.makedirs(OBSIDIAN_PILLS_DIR, exist_ok=True)

        # Add file header on first write
        if not os.path.exists(log_path):
            header = (
                f"# Sales Pills — Week {week_str}\n\n"
                f"Auto-logged by `daily_sales_pill.py`.\n"
                f"← [[sales-pill-system|System docs]]\n"
            )
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(header)

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)

        print(f"📓 Logged to Obsidian: {log_path}")
    except Exception as e:
        print(f"⚠️  Obsidian log failed (non-fatal): {e}")


# ─── Fathom + Claude helpers ──────────────────────────────────────────────────
def _call_duration_min(meeting):
    """Return recording duration in minutes, or 0 if unavailable."""
    rs = meeting.get("recording_start_time")
    re_ = meeting.get("recording_end_time")
    if not (rs and re_):
        return 0
    try:
        d1 = datetime.fromisoformat(rs.replace("Z", "+00:00"))
        d2 = datetime.fromisoformat(re_.replace("Z", "+00:00"))
        return max(int((d2 - d1).total_seconds() / 60), 0)
    except Exception:
        return 0


def _fathom_get(path):
    req = urllib.request.Request(
        f"https://api.fathom.ai/external/v1{path}",
        headers={"X-Api-Key": FATHOM_KEY, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def fathom_best_call_this_week(top_n=3):
    """
    Returns the top N sales call candidates from the past 7 days (Sales team only).
    Pre-scored by duration with post-sale penalty. Final quality re-ranking
    (using talk ratio) happens inside fathom_rep_scorecard.
    """
    seven_days_ago = (
        datetime.now(timezone.utc) - timedelta(days=7)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        meetings = _fathom_get(
            f"/meetings?created_after={seven_days_ago}&include_transcript=false"
        ).get("items", [])
    except Exception:
        return []

    candidates = []
    for m in meetings:
        # Sales team only — exclude Customer Success, Partner & support, etc.
        team = (m.get("recorded_by") or {}).get("team") or ""
        if team != "Sales":
            continue
        externals = [
            i for i in (m.get("calendar_invitees") or []) if i.get("is_external")
        ]
        if not externals:
            continue
        dur = _call_duration_min(m)
        if dur < 5:
            continue
        title_lower = (m.get("meeting_title") or m.get("title") or "").lower()
        # Skip internal meetings entirely
        if any(kw in title_lower for kw in _INTERNAL_KW):
            continue
        is_post_sale = any(kw in title_lower for kw in _POST_SALE_KW)
        candidates.append({
            **m,
            "_dur_min": dur,
            "_score": dur * (0.4 if is_post_sale else 1.0),
            "_ext_names": [i.get("name") or i.get("email") or "?" for i in externals],
            "_is_post_sale": is_post_sale,
        })
    if not candidates:
        return []
    return sorted(candidates, key=lambda x: x["_score"], reverse=True)[:top_n]


def _compute_talk_ratio(calls, rep_name):
    """Compute rep vs prospect talk ratio from transcript character counts."""
    name_parts = [p.lower() for p in rep_name.split() if len(p) > 2]
    rep_chars = prospect_chars = 0
    for m in calls:
        for seg in (m.get("transcript") or []):
            spk = (seg.get("speaker") or {}).get("display_name", "").lower()
            chars = len(seg.get("text", ""))
            if any(p in spk for p in name_parts):
                rep_chars += chars
            else:
                prospect_chars += chars
    total = rep_chars + prospect_chars
    if not total:
        return None, None
    return round(rep_chars / total * 100), round(prospect_chars / total * 100)


def _extract_call_excerpt(meeting, n_first=12, n_last=8):
    """Return first N + last N transcript lines as a readable text block."""
    segs = []
    for s in (meeting.get("transcript") or []):
        spk = (s.get("speaker") or {}).get("display_name", "?")
        text = (s.get("text") or "").strip()
        if text:
            segs.append(f"{spk}: {text}")
    if len(segs) <= n_first + n_last:
        return "\n".join(segs)
    return "\n".join(segs[:n_first]) + "\n[...]\n" + "\n".join(segs[-n_last:])


def _call_claude(prompt):
    """Call AI for qualitative analysis. Uses Anthropic if key set, else OpenAI. Returns text or None."""
    if ANTHROPIC_KEY:
        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 450,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["content"][0]["text"].strip()

    elif OPENAI_KEY:
        payload = json.dumps({
            "model": "gpt-4o-mini",
            "max_tokens": 450,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "content-type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()

    return None


def _talk_quality_factor(rep_pct):
    """Score multiplier based on talk ratio. Ideal: 35–50% rep talk time."""
    if rep_pct is None:
        return 1.0
    if 35 <= rep_pct <= 50:
        return 1.4   # ideal — rep listens well
    if 25 <= rep_pct < 35 or 50 < rep_pct <= 58:
        return 1.0   # acceptable
    if 58 < rep_pct <= 65:
        return 0.6   # talking too much
    return 0.3       # way off — rep dominates or is silent


def fathom_rep_scorecard(candidates):
    """
    Accepts a list of call candidates (from fathom_best_call_this_week).
    Picks the best by duration score, fetches ONLY that one call's transcript,
    computes talk ratio, then runs AI analysis. Fast: 2 API calls total.
    """
    if not candidates:
        return ["📞 Best Call → _No recorded sales calls this week._", ""]

    best_call  = candidates[0]   # already sorted by score
    rep_info   = best_call.get("recorded_by") or {}
    rep_name   = rep_info.get("name") or "?"
    # Normalise to first name for consistency with rest of the pill
    rep_name_display = rep_name.split()[0] if rep_name != "?" else "?"
    best_dur   = best_call["_dur_min"]
    best_title = (best_call.get("meeting_title") or best_call.get("title") or "Call").strip()
    best_share = best_call.get("share_url") or ""
    recording_id = best_call.get("recording_id") or ""

    # ── Fetch transcript for just this one call ───────────────────────────────
    call_with_transcript = None
    try:
        call_with_transcript = _fathom_get(
            f"/meetings/{recording_id}?include_transcript=true"
        )
    except Exception:
        pass

    # Fallback: use the call without transcript
    if not call_with_transcript:
        call_with_transcript = best_call

    # ── Talk ratio from this call only ────────────────────────────────────────
    rep_pct, prospect_pct = _compute_talk_ratio([call_with_transcript], rep_name)
    if rep_pct is None:
        ratio_str = "n/a"
    else:
        flag = " ✅" if 35 <= rep_pct <= 50 else (" ⚠️" if rep_pct > 55 else "")
        ratio_str = f"*{rep_pct}%* rep · {prospect_pct}% prospect{flag}"

    lines = [
        f"📞 Best Call → {rep_name_display} · {best_title} · {best_dur} min",
        f"🗣 Talk ratio: {ratio_str}",
    ]

    # ── AI metrics + key moment (requires API key) ────────────────────────────
    if ANTHROPIC_KEY or OPENAI_KEY:
        excerpt = _extract_call_excerpt(call_with_transcript)
        prompt = (
            "You are a sales enablement manager at Spoki, a WhatsApp Business automation"
            " platform (Official Meta Partner, Italy & Spain markets).\n\n"
            f"Rep: {rep_name} | Call: '{best_title}' ({best_dur} min)\n"
            f"Talk ratio: {rep_pct}% rep / {prospect_pct}% prospect\n\n"
            "TRANSCRIPT EXCERPT:\n"
            f"{excerpt}\n\n"
            "Analyse this call and return ONLY valid JSON (no markdown fences):\n"
            "{\n"
            '  "discovery": "7-10 words on how rep uncovered pain/needs — positive framing",\n'
            '  "objection_handling": "7-10 words on how rep handled pushback — positive framing",\n'
            '  "prospect_energy": "4-6 words + one short verbatim prospect quote in the original language",\n'
            '  "enterprise_fit": "7-10 words on handling complexity, integrations, or stakeholders",\n'
            '  "key_moment": "2-3 sentences: what obstacle appeared, exactly what the rep did, what the prospect said or did as a result. Be specific and factual from the transcript."\n'
            "}"
        )
        try:
            raw = _call_claude(prompt)
            if raw:
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                a = json.loads(raw.strip())
                lines += [
                    f"🔍 Discovery: {a.get('discovery', '—')}",
                    f"💪 Objections: {a.get('objection_handling', '—')}",
                    f"⚡ Prospect energy: {a.get('prospect_energy', '—')}",
                    f"🏢 Enterprise fit: {a.get('enterprise_fit', '—')}",
                ]
                if a.get("key_moment"):
                    lines += ["", f"🎯 *Key moment:* {a['key_moment']}"]
        except Exception:
            pass  # fails gracefully — pill still sends with talk ratio only

    lines.append("")
    if best_share:
        lines.append(f"🎥 Watch: {best_share}")

    return lines


# ─── Daily Pills ──────────────────────────────────────────────────────────────
def pill_monday():
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    zero_val = hs_search(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "IN",
             "values": ["986053467", "986053468", "2674750700"]},
            {"propertyName": "amount", "operator": "EQ", "value": "0"},
        ],
        sorts=[{"propertyName": "closedate", "direction": "ASCENDING"}],
        properties=["dealname", "dealstage", "amount", "closedate", "hubspot_owner_id"],
        limit=5,
    )

    overdue = hs_search(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "NOT_IN",
             "values": ["986053469", "986053470"]},
            {"propertyName": "closedate", "operator": "LT", "value": str(now_ms)},
            {"propertyName": "amount", "operator": "GT", "value": "0"},
        ],
        sorts=[{"propertyName": "amount", "direction": "DESCENDING"}],
        properties=["dealname", "dealstage", "amount", "closedate", "hubspot_owner_id"],
        limit=5,
    )

    lines = ["hey team, today's tips & focus 🧹",
             "",
             "*📊 Monday — Data Hygiene Day*",
             "Clean pipeline = accurate forecast = hit target.",
             ""]

    if zero_val.get("results"):
        lines.append("*🚨 Advanced deals with €0 value — update NOW:*")
        for d in zero_val["results"][:4]:
            p = d["properties"]
            lines.append(
                f"• *{p['dealname']}* ({stage_name(p['dealstage'])}) "
                f"→ {owner_name(p.get('hubspot_owner_id',''))}, add deal value today"
            )
        lines.append("")

    if overdue.get("results"):
        lines.append("*📅 Overdue close dates — reschedule or close:*")
        for d in overdue["results"][:5]:
            p = d["properties"]
            lines.append(
                f"• *{p['dealname']}* {fmt_eur(p.get('amount'))} "
                f"(overdue {fmt_date(p.get('closedate'))}) "
                f"→ {owner_name(p.get('hubspot_owner_id',''))}"
            )
        lines.append("")

    total_overdue = overdue.get("total", 0)
    total_zero = zero_val.get("total", 0)
    lines.append(
        f"💡 *Why it matters:* {total_overdue} deals with past close dates + "
        f"{total_zero} advanced deals at €0 = wrong forecast. "
        "5 min per deal fixes it 💪"
    )
    return "\n".join(lines)


def pill_tuesday():
    week_start = _week_start_ms()   # Monday 00:00 Rome — excludes last week's deals
    new_deals = hs_search(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "createdate", "operator": "GT",
             "value": str(week_start)},
            {"propertyName": "dealstage", "operator": "NOT_IN",
             "values": ["986053469", "986053470"]},
        ],
        sorts=[{"propertyName": "createdate", "direction": "DESCENDING"}],
        properties=["dealname", "dealstage", "amount", "createdate", "hubspot_owner_id"],
        limit=10,
    )

    results = new_deals.get("results", [])
    total   = new_deals.get("total", 0)

    # Group by rep
    by_rep = {}
    for d in results:
        p   = d["properties"]
        rep = owner_name(p.get("hubspot_owner_id", ""))
        by_rep.setdefault(rep, []).append(p)

    lines = ["hey team, today's tips & focus 🌱",
             "",
             "*🌱 Tuesday — New Pipeline This Week*",
             "Fresh deals entered the funnel. Make sure each has a next step.",
             ""]

    if not results:
        lines.append(
            "_No new deals created this week yet — let's get prospecting!_ 📞"
        )
    else:
        total_value = sum(float(d["properties"].get("amount") or 0) for d in results)
        value_str   = f" — {fmt_eur(total_value)} potential" if total_value > 0 else ""
        lines.append(
            f"*{total} new deal{'s' if total != 1 else ''} this week{value_str}:*"
        )
        lines.append("")
        for rep, deals in sorted(by_rep.items()):
            rep_total  = sum(float(p.get("amount") or 0) for p in deals)
            rep_val_str = f" · {fmt_k(rep_total)}" if rep_total > 0 else ""
            deal_list  = " · ".join(
                f"{p['dealname']} "
                f"({'TBD' if not p.get('amount') else fmt_k(p.get('amount'))}"
                f" · {stage_name(p['dealstage'])})"
                for p in deals[:3]
            )
            suffix = f" +{len(deals)-3} more" if len(deals) > 3 else ""
            lines.append(
                f"• *{rep}* — {len(deals)} deal{'s' if len(deals)!=1 else ''}{rep_val_str}"
            )
            lines.append(f"  ↳ {deal_list}{suffix}")

    lines.append("")
    lines.append(
        "💡 New deal without a next step = lost deal. "
        "Define the next action for each one today! 📋"
    )
    return "\n".join(lines)


def pill_wednesday():
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    hot = hs_search(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "IN",
             "values": ["986053468", "2674750700"]},
            {"propertyName": "amount", "operator": "GT", "value": "5000"},
            {"propertyName": "closedate", "operator": "GT", "value": str(now_ms)},
        ],
        sorts=[{"propertyName": "amount", "direction": "DESCENDING"}],
        properties=["dealname", "dealstage", "amount", "closedate",
                    "hubspot_owner_id", "hs_next_step"],
        limit=5,
    )

    lines = ["hey team, today's tips & focus 🔥",
             "",
             "*🔥 Wednesday — Hot Deals to Push*",
             "Follow-up & Negotiation deals with high potential. Push now!",
             "",
             "*💰 Top deals to close this month:*"]

    for d in hot.get("results", [])[:5]:
        p = d["properties"]
        next_step = (p.get("hs_next_step") or "")[:60]
        lines.append(
            f"• *{p['dealname']}* — {fmt_eur(p.get('amount'))} — "
            f"{stage_name(p['dealstage'])} — close: {fmt_date(p.get('closedate'))}"
        )
        lines.append(f"  ↳ Owner: *{owner_name(p.get('hubspot_owner_id',''))}*")
        if next_step:
            lines.append(f"  ↳ Next step: {next_step}")
        else:
            lines.append("  ↳ ⚠️ No next step — define it today")

    lines.append("")
    lines.append(
        "💡 Make sure every deal has a clear next step. "
        "No next step = frozen deal. 🎯"
    )
    return "\n".join(lines)


def pill_thursday():
    fourteen_days_ago = int(
        (datetime.now(timezone.utc) - timedelta(days=14)).timestamp() * 1000
    )

    def days_since(iso_str):
        if not iso_str:
            return "?"
        try:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return str((datetime.now(timezone.utc) - dt).days)
        except Exception:
            return "?"

    stuck = hs_search(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "IN",
             "values": ["986053466", "986053467", "986053468", "2674750700"]},
            {"propertyName": "hs_lastmodifieddate", "operator": "LT",
             "value": str(fourteen_days_ago)},
            {"propertyName": "amount", "operator": "GT", "value": "0"},
        ],
        sorts=[{"propertyName": "amount", "direction": "DESCENDING"}],
        properties=["dealname", "dealstage", "amount", "hubspot_owner_id",
                    "hs_lastmodifieddate", "hs_next_step"],
        limit=7,
    )

    total_stuck = stuck.get("total", 0)
    results     = stuck.get("results", [])

    lines = ["hey team, today's tips & focus ⏱",
             "",
             "*⏱ Thursday — Stage Velocity Check*",
             "Deals stuck in the same stage for 14+ days. Move them or close them.",
             ""]

    if not results:
        lines += [
            "✅ *No deals stuck for 14+ days — pipeline is moving!*",
            "",
            "💡 Keep the pace — update every deal you touch today. 🚀",
        ]
        return "\n".join(lines)

    lines.append(f"*⚠️ {total_stuck} deals haven't moved in 14+ days:*")
    for d in results[:7]:
        p         = d["properties"]
        days      = days_since(p.get("hs_lastmodifieddate"))
        next_step = (p.get("hs_next_step") or "")[:55]
        lines.append(
            f"• *{p['dealname']}* — {fmt_eur(p.get('amount'))} — "
            f"{stage_name(p['dealstage'])}"
        )
        if next_step:
            lines.append(
                f"  ↳ Stuck *{days} days* → "
                f"*{owner_name(p.get('hubspot_owner_id',''))}* · {next_step}"
            )
        else:
            lines.append(
                f"  ↳ Stuck *{days} days* → "
                f"*{owner_name(p.get('hubspot_owner_id',''))}* · "
                "⚠️ no next step defined"
            )

    lines.append("")
    lines.append(
        f"💡 *{total_stuck} deals need a push.* "
        "One action each: send a follow-up, book a next call, or mark as lost. 🎯"
    )
    return "\n".join(lines)


def pill_friday():
    week_start = _week_start_ms()   # Monday 00:00 Rome — this week's wins only
    wins = hs_search(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ", "value": "986053469"},
            {"propertyName": "closedate", "operator": "GT",
             "value": str(week_start)},
        ],
        sorts=[{"propertyName": "amount", "direction": "DESCENDING"}],
        properties=["dealname", "amount", "closedate", "hubspot_owner_id", "createdate"],
        limit=5,
    )

    closing = hs_search(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ",
             "value": "2674750700"},
            {"propertyName": "amount", "operator": "GT", "value": "3000"},
        ],
        sorts=[{"propertyName": "amount", "direction": "DESCENDING"}],
        properties=["dealname", "amount", "closedate", "hubspot_owner_id"],
        limit=3,
    )

    lines = ["hey team, today's tips & focus 🏆",
             "",
             "*🏆 Friday — Wins & Momentum*",
             ""]

    # — Closed wins: compact single line —
    wins_results = wins.get("results", [])
    if wins_results:
        total_won = sum(float(d["properties"].get("amount") or 0)
                        for d in wins_results)
        win_items = " ".join(
            f"• {d['properties']['dealname']} — "
            f"{fmt_eur(d['properties'].get('amount'))} → "
            f"{owner_name(d['properties'].get('hubspot_owner_id', ''))} 🎉"
            for d in wins_results
        )
        lines.append(f"🎉 Closed this week ({fmt_eur(total_won)} total): {win_items}")
    else:
        lines.append("🎯 No closes this week — let's push the deals in Negotiation!")

    # — Negotiation: compact single line — • first · second · third
    closing_results = closing.get("results", [])
    if closing_results:
        neg_parts = [
            f"{d['properties']['dealname']} "
            f"{fmt_k(d['properties'].get('amount'))} "
            f"→ {owner_name(d['properties'].get('hubspot_owner_id', ''))}"
            for d in closing_results
        ]
        neg_items = "• " + " · ".join(neg_parts)
        lines.append(f"⚡ In Negotiation — push to close next week: {neg_items}")

    # ─── 🏅 Rep Scorecard ─────────────────────────────────────────────────────
    lines.append("")
    lines.append("*🏅 Rep Scorecard*")

    # — Best Deal: single compact line —
    if wins_results:
        star = wins_results[0]
        sp = star["properties"]
        star_rep  = owner_name(sp.get("hubspot_owner_id", ""))
        star_name = sp.get("dealname", "—")
        star_amt  = float(sp.get("amount") or 0)

        close_days = None
        try:
            created_dt = datetime.fromisoformat(
                sp["createdate"].replace("Z", "+00:00")
            )
            closed_dt = datetime.fromisoformat(
                sp["closedate"].replace("Z", "+00:00")
            )
            close_days = max((closed_dt - created_dt).days, 1)
        except Exception:
            pass

        days_str = f" · {close_days} days to close" if close_days is not None else ""
        lines.append(
            f"🥇 Best Deal → {star_rep} · {star_name} · {fmt_k(star_amt)}{days_str} 👏"
        )
    else:
        lines.append("🥇 Best Deal → _No closes this week — push those Negotiation deals!_")

    # — Best Call / Video Call (Fathom) —
    candidates = fathom_best_call_this_week(top_n=1)
    lines.extend(fathom_rep_scorecard(candidates))

    lines.append("Have a great weekend! Next week we close 🚀")
    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────────
PILLS = {
    1: ("monday", pill_monday),
    2: ("tuesday", pill_tuesday),
    3: ("wednesday", pill_wednesday),
    4: ("thursday", pill_thursday),
    5: ("friday", pill_friday),
}
DAY_ALIAS = {
    "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5,
    "monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4, "friday": 5,
}


def main():
    parser = argparse.ArgumentParser(description="Send daily sales pill to Google Chat")
    parser.add_argument("--day", help="Force day: mon|tue|wed|thu|fri", default=None)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print message without sending")
    parser.add_argument("--anthropic-key",
                        help="Anthropic API key (overrides ANTHROPIC_API_KEY env var)",
                        default=None)
    parser.add_argument("--openai-key",
                        help="OpenAI API key (uses gpt-4o-mini, overrides OPENAI_API_KEY env var)",
                        default=None)
    args = parser.parse_args()

    # Allow passing keys via CLI for easy one-off testing
    if args.anthropic_key:
        global ANTHROPIC_KEY
        ANTHROPIC_KEY = args.anthropic_key
    if args.openai_key:
        global OPENAI_KEY
        OPENAI_KEY = args.openai_key

    # Determine day in Europe/Rome timezone (DST-aware via system locale)
    import locale, time as _time
    now_rome_str = datetime.now(timezone.utc).astimezone(
        __import__('zoneinfo', fromlist=['ZoneInfo']).ZoneInfo('Europe/Rome')
    )
    day_num = now_rome_str.isoweekday()  # 1=Mon, 7=Sun

    if args.day:
        day_num = DAY_ALIAS.get(args.day.lower())
        if day_num is None:
            print(f"Unknown day: {args.day}. Use mon/tue/wed/thu/fri")
            sys.exit(1)

    if day_num not in PILLS:
        print(f"Today is weekend (day {day_num}), no pill scheduled.")
        sys.exit(0)

    day_label, pill_fn = PILLS[day_num]
    print(f"📧 Building {day_label} pill...")

    message = pill_fn()

    if args.dry_run:
        print("\n─── PILL PREVIEW ───────────────────────────────────")
        print(message)
        print("────────────────────────────────────────────────────")
        print("✅ Dry run complete — not sent.")
    else:
        result = send_to_gchat(message)
        print(f"✅ Sent! Message ID: {result.get('name', 'unknown')}")
        log_to_obsidian(day_label, message)


if __name__ == "__main__":
    main()
