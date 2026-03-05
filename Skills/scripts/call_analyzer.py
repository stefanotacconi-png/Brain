#!/usr/bin/env python3
"""
Call Analyzer — Claude-powered analysis of Fathom meeting transcripts
Extracts rep performance signals, vertical patterns, objections, winning moments
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

import anthropic

# ── Config ──────────────────────────────────────────────────────────────────
CALLS_DIR = Path("output/calls")
ANALYSIS_DIR = Path("output/analysis")
MODEL = "claude-sonnet-4-6"

KNOWN_REPS = []   # Auto-detected from transcripts; pre-seed if known
KNOWN_VERTICALS = [
    "Beauty / Wellness", "Real Estate", "Fashion / Apparel", "Travel / Hospitality",
    "Education", "Pet Retail", "Electronics / Retail", "Home / Furniture",
    "Healthcare", "Automotive", "Finance / Insurance", "Events", "Energy",
    "Food / GDO", "Logistics",
]

# Fathom API (for any additional fetches needed)
FATHOM_API_KEY = os.getenv("FATHOM_API_KEY", "YOUR_FATHOM_API_KEY")
FATHOM_HEADERS = {"X-Api-Key": FATHOM_API_KEY}

_anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
if not _anthropic_key:
    print("ERROR: ANTHROPIC_API_KEY is not set.")
    print("Get your key at: https://console.anthropic.com/settings/keys")
    print("Then: export ANTHROPIC_API_KEY=sk-ant-...")
    import sys; sys.exit(1)
client = anthropic.Anthropic(api_key=_anthropic_key)


# ── Per-call extraction prompt ─────────────────────────────────────────────
EXTRACTION_PROMPT = """\
You are a sales call analyst for a WhatsApp Business automation company.

Meeting title: {title}
Date: {date}
Participants: {participants}

TRANSCRIPT:
{transcript}

SUMMARY (if available):
{summary}

Analyse this sales call and return a JSON object with EXACTLY these fields:

{{
  "rep_name": "name of the sales rep / SDR (person from our company)",
  "rep_role": "SDR | AE | SE | unknown",
  "company_name": "prospect company name",
  "vertical": "one of: Beauty/Wellness | Real Estate | Fashion/Apparel | Travel/Hospitality | Education | Pet Retail | Electronics/Retail | Home/Furniture | Healthcare | Automotive | Finance/Insurance | Events | Energy | Food/GDO | Logistics | Other",
  "call_stage": "cold outreach | discovery | demo | follow-up | negotiation | closing | other",
  "call_outcome": "booked | no-show | disqualified | proposal sent | demo done | deal closed | no response | objection raised | unclear",
  "duration_minutes": 0,
  "talk_ratio": {{
    "rep_pct": 0,
    "prospect_pct": 0
  }},
  "pain_points_mentioned": ["list of pain points the prospect mentioned"],
  "our_solution_pitched": ["list of features/use cases we pitched"],
  "objections": [
    {{
      "objection": "what they said",
      "how_rep_handled": "what rep said back",
      "outcome": "overcame | stalled | dropped"
    }}
  ],
  "winning_moments": [
    {{
      "moment": "exact quote or paraphrase",
      "why_it_worked": "brief reason",
      "timestamp_approx": "MM:SS or null"
    }}
  ],
  "missed_opportunities": [
    {{
      "moment": "what happened",
      "what_should_have_been_said": "recommended response"
    }}
  ],
  "competitor_mentioned": ["Charles | ManyChat | Twilio | Zendesk | Respond.io | none"],
  "next_steps_agreed": "what was agreed at the end, if anything",
  "coaching_flags": ["list of coaching points for this rep"],
  "call_score": 0,
  "call_score_reasoning": "1-2 sentences explaining the score (1=very poor, 10=excellent)"
}}

Be precise. Only include factual observations from the transcript. Return ONLY the JSON object, no markdown.
"""


# ── Helpers ───────────────────────────────────────────────────────────────────
def load_call(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def extract_transcript_text(meeting: dict) -> str:
    """
    Fathom transcript format:
      List of {speaker: {display_name, matched_calendar_invitee_email}, text, timestamp}
    """
    transcript = meeting.get("transcript")
    if not transcript:
        return ""

    # Standard Fathom format: list of utterances
    if isinstance(transcript, list):
        lines = []
        for utt in transcript:
            speaker_obj = utt.get("speaker") or {}
            if isinstance(speaker_obj, dict):
                speaker = speaker_obj.get("display_name") or speaker_obj.get("name") or "Unknown"
            else:
                speaker = str(speaker_obj)
            text = utt.get("text") or utt.get("content") or ""
            ts = utt.get("timestamp") or utt.get("start_time") or ""
            lines.append(f"[{ts}] {speaker}: {text}" if ts else f"{speaker}: {text}")
        return "\n".join(lines)[:50_000]

    # Fallback: plain string
    if isinstance(transcript, str):
        return transcript[:50_000]

    return str(transcript)[:50_000]


def extract_summary_text(meeting: dict) -> str:
    summary = meeting.get("default_summary") or meeting.get("summary") or ""
    if isinstance(summary, dict):
        return summary.get("text") or summary.get("content") or str(summary)
    return str(summary)[:3000]


def extract_participants(meeting: dict) -> tuple[str, list[str]]:
    """Returns (rep_name, [external_participant_names])"""
    rep = (meeting.get("recorded_by") or {}).get("name", "Unknown")
    invitees = meeting.get("calendar_invitees") or []
    externals = [
        inv.get("name") or inv.get("email") or inv.get("matched_speaker_display_name", "?")
        for inv in invitees
        if inv.get("is_external")
    ]
    return rep, externals


def analyse_call(meeting: dict) -> dict | None:
    transcript = extract_transcript_text(meeting)
    if len(transcript) < 100:
        return None  # Skip empty/too short

    # Fathom field names
    title = meeting.get("meeting_title") or meeting.get("title") or "Untitled meeting"
    date = meeting.get("created_at") or "unknown"
    rep_name, external_participants = extract_participants(meeting)
    all_participants = external_participants + [rep_name]
    participant_names = all_participants

    prompt = EXTRACTION_PROMPT.format(
        title=title,
        date=date,
        participants=", ".join(participant_names) or "unknown",
        transcript=transcript,
        summary=extract_summary_text(meeting),
    )

    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        analysis = json.loads(raw)
        analysis["_meeting_id"] = meeting.get("recording_id") or meeting.get("id")
        analysis["_meeting_title"] = title
        analysis["_meeting_date"] = date
        analysis["_share_url"] = meeting.get("share_url")
        analysis["_rep_team"] = (meeting.get("recorded_by") or {}).get("team")
        # Override rep_name with ground truth from recorded_by if Claude missed it
        if analysis.get("rep_name") in ("Unknown", "unknown", None, ""):
            analysis["rep_name"] = rep_name
        return analysis

    except Exception as e:
        print(f"    ERROR analysing {title}: {e}")
        return None


# ── Main pipeline ─────────────────────────────────────────────────────────────
def run_analysis(force_refresh=False):
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    call_files = sorted(CALLS_DIR.glob("*.json"))
    call_files = [f for f in call_files if f.name != "index.json"]

    print(f"\n{'='*60}")
    print(f"CALL ANALYZER — {len(call_files)} transcripts to analyse")
    print(f"{'='*60}\n")

    results = []
    skipped = 0

    for i, fpath in enumerate(call_files, 1):
        meeting = load_call(fpath)
        mid = fpath.stem
        out_path = ANALYSIS_DIR / f"{mid}_analysis.json"

        if out_path.exists() and not force_refresh:
            print(f"  [{i}/{len(call_files)}] {meeting.get('title','?')[:50]} — cached")
            with open(out_path) as f:
                results.append(json.load(f))
            continue

        print(f"  [{i}/{len(call_files)}] Analysing: {meeting.get('title','?')[:50]}...", end=" ", flush=True)

        analysis = analyse_call(meeting)
        if analysis:
            with open(out_path, "w") as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            results.append(analysis)
            print(f"OK ({analysis.get('call_score','?')}/10 — {analysis.get('rep_name','?')})")
        else:
            skipped += 1
            print("SKIP (no/short transcript)")

        time.sleep(0.3)  # Small delay between Claude calls

    # Save aggregated results
    agg_path = ANALYSIS_DIR / "all_analyses.json"
    with open(agg_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n  Analysed: {len(results)} | Skipped: {skipped}")
    print(f"  Saved to: {ANALYSIS_DIR}/")
    return results


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyse call transcripts with Claude")
    parser.add_argument("--refresh", action="store_true", help="Re-analyse even if cached")
    args = parser.parse_args()

    results = run_analysis(force_refresh=args.refresh)
    print(f"\nDone. Run next: python scripts/generate_outputs.py")
