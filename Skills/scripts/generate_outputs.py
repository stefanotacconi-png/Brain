#!/usr/bin/env python3
"""
Generate Outputs — turn call analyses into playbooks, scorecards, transcript library, enablement topics
Uses Claude to synthesise patterns across all analysed calls
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import anthropic

# ── Config ──────────────────────────────────────────────────────────────────
ANALYSIS_DIR = Path("output/analysis")
PLAYBOOKS_DIR = Path("output/playbooks")
SCORECARDS_DIR = Path("output/scorecards")
LIBRARY_DIR = Path("output/transcript_library")
MODEL = "claude-sonnet-4-6"

client = anthropic.Anthropic()

# ── Load all analyses ─────────────────────────────────────────────────────────
def load_analyses() -> list[dict]:
    agg_path = ANALYSIS_DIR / "all_analyses.json"
    if agg_path.exists():
        with open(agg_path) as f:
            return json.load(f)
    # Fallback: load individual files
    results = []
    for p in sorted(ANALYSIS_DIR.glob("*_analysis.json")):
        with open(p) as f:
            results.append(json.load(f))
    return results


# ── 1. VERTICAL PLAYBOOKS ────────────────────────────────────────────────────
PLAYBOOK_PROMPT = """\
You are a sales enablement expert for a WhatsApp Business automation company.

Below are ALL the sales call analyses for the "{vertical}" vertical:

{analyses_json}

Product context:
- We sell WhatsApp automation: AI chatbots, drip flows, appointment reminders, lead qualification, post-purchase sequences
- ICP: B2C / D2C companies, 10-500 employees, Spain + Italy primary market
- Key pains we solve: no-shows, slow ad lead response, cart abandonment, support overload

Write a detailed sales playbook for the {vertical} vertical in Markdown.

Structure it EXACTLY like this:

# {vertical} Sales Playbook
*Generated from {n_calls} recorded calls — {date}*

## 1. Vertical Quick Profile
- Typical company size, decision maker, deal size, time to close
- Their top 2-3 pains

## 2. Opening Lines That Worked
(Pull actual examples from winning moments — quote them verbatim if possible)

## 3. Discovery Questions That Uncovered Pain
(The specific questions that got prospects talking)

## 4. Demo / Pitch Flow
(What features to lead with, what to leave for later)

## 5. Objection Handling
For each common objection: exact objection text → recommended response → outcome it leads to

## 6. Closing Language
(Phrases that moved deals forward)

## 7. Red Flags to Watch For
(What signals that this prospect is not a good fit or will churn)

## 8. Email/Sequence Templates Specific to This Vertical
(2-3 copy snippets that resonated on calls)

## 9. What NOT to Do
(Specific mistakes observed in calls for this vertical)

Be specific and actionable. Use real examples from the data. If fewer than 3 calls exist for this vertical, flag it.
"""


def generate_vertical_playbook(vertical: str, analyses: list[dict]) -> str:
    if not analyses:
        return f"# {vertical} Playbook\n\n*No calls recorded yet for this vertical.*\n"

    prompt = PLAYBOOK_PROMPT.format(
        vertical=vertical,
        analyses_json=json.dumps(analyses, indent=2)[:60_000],
        n_calls=len(analyses),
        date=datetime.now().strftime("%Y-%m-%d"),
    )

    msg = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── 2. REP SCORECARDS ────────────────────────────────────────────────────────
REP_SCORECARD_PROMPT = """\
You are a sales manager analysing performance data for one of your reps.

Rep name: {rep_name}
Total calls analysed: {n_calls}
Date range: {date_range}

ALL CALL ANALYSES FOR THIS REP:
{analyses_json}

Write a detailed sales rep performance scorecard in Markdown. Be honest and specific — this is for coaching.

Structure:

# Sales Rep Scorecard: {rep_name}
*{n_calls} calls analysed — {date}*

## Summary Metrics
- Average call score: X/10
- Talk ratio (rep vs prospect): X% / X%
- Call outcome breakdown: (booked | demo done | disqualified | etc.)
- Most common verticals called

## Strengths (with evidence)
List 3-5 things this rep does well, with specific examples from transcripts

## Coaching Areas (with evidence)
List 3-5 specific gaps, each with:
- What was observed (quote or paraphrase)
- What should have happened instead
- Priority: HIGH | MEDIUM | LOW

## Objection Handling Summary
How well does this rep handle objections? Which ones do they struggle with most?

## Top Performing Calls
List the 3 highest-scored calls with a brief note on why they worked

## Suggested Training Topics
Prioritised list of enablement sessions this rep should attend

## Manager Action Items
3-5 concrete actions the manager should take in the next 30 days
"""


def generate_rep_scorecard(rep_name: str, analyses: list[dict]) -> str:
    dates = [a.get("_meeting_date", "") for a in analyses if a.get("_meeting_date")]
    date_range = f"{min(dates)[:10]} → {max(dates)[:10]}" if dates else "unknown"

    prompt = REP_SCORECARD_PROMPT.format(
        rep_name=rep_name,
        n_calls=len(analyses),
        date_range=date_range,
        analyses_json=json.dumps(analyses, indent=2)[:60_000],
        date=datetime.now().strftime("%Y-%m-%d"),
    )

    msg = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── 3. TRANSCRIPT LIBRARY ────────────────────────────────────────────────────
def build_transcript_library(analyses: list[dict]) -> str:
    lines = [
        "# Winning Transcript Library",
        f"*Generated {datetime.now().strftime('%Y-%m-%d')} from {len(analyses)} calls*",
        "",
        "Tagged excerpts from best-performing calls — use for onboarding and training.\n",
    ]

    # Group winning moments by tag
    by_tag = defaultdict(list)

    for a in analyses:
        rep = a.get("rep_name", "Unknown")
        vertical = a.get("vertical", "Unknown")
        score = a.get("call_score", 0)
        title = a.get("_meeting_title", "Untitled")
        date = (a.get("_meeting_date") or "")[:10]
        mid = a.get("_meeting_id", "")

        for moment in a.get("winning_moments", []):
            tag = vertical
            by_tag[tag].append({
                "moment": moment.get("moment", ""),
                "why": moment.get("why_it_worked", ""),
                "ts": moment.get("timestamp_approx"),
                "rep": rep,
                "call": f"{title} ({date})",
                "score": score,
                "mid": mid,
            })

    for tag, moments in sorted(by_tag.items()):
        lines.append(f"## {tag}")
        lines.append("")
        # Sort by call score desc
        for m in sorted(moments, key=lambda x: x["score"], reverse=True):
            ts_note = f" `[{m['ts']}]`" if m["ts"] else ""
            lines.append(f"**Rep:** {m['rep']} | **Call:** {m['call']}{ts_note}")
            lines.append(f"> {m['moment']}")
            lines.append(f"*Why it worked: {m['why']}*")
            lines.append("")

    # Also add objection handling wins
    lines.append("---\n## Objection Handling — Successful Responses\n")
    for a in sorted(analyses, key=lambda x: x.get("call_score", 0), reverse=True)[:20]:
        rep = a.get("rep_name", "Unknown")
        vertical = a.get("vertical", "")
        date = (a.get("_meeting_date") or "")[:10]
        for obj in a.get("objections", []):
            if obj.get("outcome") == "overcame":
                lines.append(f"**Objection** ({vertical} — {rep}, {date}):")
                lines.append(f"> _{obj.get('objection', '')}_")
                lines.append(f"**Response that worked:** {obj.get('how_rep_handled', '')}")
                lines.append("")

    return "\n".join(lines)


# ── 4. ENABLEMENT TOPICS ─────────────────────────────────────────────────────
ENABLEMENT_PROMPT = """\
You are a sales enablement manager reviewing coaching flags and missed opportunities across your entire sales team.

Below are all the coaching flags and missed opportunities extracted from {n_calls} sales calls:

COACHING FLAGS (by rep):
{coaching_json}

MISSED OPPORTUNITIES (all calls):
{missed_json}

OBJECTIONS NOT OVERCAME:
{failed_obj_json}

Generate a prioritised Sales Enablement Training Agenda in Markdown.

Format:

# Sales Enablement Topics — Training Agenda
*Based on {n_calls} calls analysed — {date}*

## Priority 1 — Immediate (This Week)
For each topic:
### Topic Name
- **Why urgent:** (frequency + impact)
- **Reps affected:** (names or "all reps")
- **Suggested format:** (role-play | video review | 1:1 coaching | group workshop)
- **Success metric:** (how you'll know it's fixed)
- **Sample exercise:** (1-2 sentence description)

## Priority 2 — This Month

## Priority 3 — Ongoing / Foundational

## Recommended Call Review Sessions
List 3-5 specific calls to review as a team (use call IDs/titles from the data), with a note on what to focus on

## Quick Wins (can be fixed immediately)
3-5 tactical fixes reps can apply in their next call without training
"""


def generate_enablement_topics(analyses: list[dict]) -> str:
    # Aggregate coaching flags by rep
    coaching_by_rep = defaultdict(list)
    missed_opps = []
    failed_objs = []

    for a in analyses:
        rep = a.get("rep_name", "Unknown")
        for flag in a.get("coaching_flags", []):
            coaching_by_rep[rep].append({
                "flag": flag,
                "call": a.get("_meeting_title"),
                "date": (a.get("_meeting_date") or "")[:10],
                "score": a.get("call_score", 0),
            })
        for mo in a.get("missed_opportunities", []):
            missed_opps.append({
                "rep": rep,
                "vertical": a.get("vertical"),
                "moment": mo.get("moment"),
                "recommended": mo.get("what_should_have_been_said"),
            })
        for obj in a.get("objections", []):
            if obj.get("outcome") in ("stalled", "dropped"):
                failed_objs.append({
                    "rep": rep,
                    "objection": obj.get("objection"),
                    "how_handled": obj.get("how_rep_handled"),
                    "vertical": a.get("vertical"),
                })

    prompt = ENABLEMENT_PROMPT.format(
        n_calls=len(analyses),
        coaching_json=json.dumps(dict(coaching_by_rep), indent=2)[:20_000],
        missed_json=json.dumps(missed_opps, indent=2)[:20_000],
        failed_obj_json=json.dumps(failed_objs, indent=2)[:15_000],
        date=datetime.now().strftime("%Y-%m-%d"),
    )

    msg = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── Main orchestrator ─────────────────────────────────────────────────────────
def run(skip_playbooks=False, skip_scorecards=False, skip_library=False, skip_enablement=False):
    PLAYBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    SCORECARDS_DIR.mkdir(parents=True, exist_ok=True)
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("GENERATE OUTPUTS")
    print(f"{'='*60}\n")

    analyses = load_analyses()
    if not analyses:
        print("ERROR: No analyses found. Run call_analyzer.py first.")
        return

    print(f"  Loaded {len(analyses)} call analyses\n")

    # Group by vertical
    by_vertical = defaultdict(list)
    by_rep = defaultdict(list)
    for a in analyses:
        v = a.get("vertical", "Other")
        r = a.get("rep_name", "Unknown")
        by_vertical[v].append(a)
        by_rep[r].append(a)

    # ── Vertical Playbooks ──
    if not skip_playbooks:
        print("  [1/4] Generating vertical playbooks...")
        for vertical, calls in sorted(by_vertical.items()):
            print(f"        {vertical} ({len(calls)} calls)...", end=" ", flush=True)
            playbook = generate_vertical_playbook(vertical, calls)
            slug = vertical.lower().replace("/", "_").replace(" ", "_").replace(",", "")
            out = PLAYBOOKS_DIR / f"playbook_{slug}.md"
            out.write_text(playbook)
            print("saved")

    # ── Rep Scorecards ──
    if not skip_scorecards:
        print("\n  [2/4] Generating rep scorecards...")
        for rep, calls in sorted(by_rep.items()):
            if rep in ("Unknown", "unknown"):
                continue
            print(f"        {rep} ({len(calls)} calls)...", end=" ", flush=True)
            scorecard = generate_rep_scorecard(rep, calls)
            slug = rep.lower().replace(" ", "_")
            out = SCORECARDS_DIR / f"scorecard_{slug}.md"
            out.write_text(scorecard)
            print("saved")

    # ── Transcript Library ──
    if not skip_library:
        print("\n  [3/4] Building transcript library...")
        library = build_transcript_library(analyses)
        out = LIBRARY_DIR / "winning_moments.md"
        out.write_text(library)
        print(f"        Saved → {out}")

    # ── Enablement Topics ──
    if not skip_enablement:
        print("\n  [4/4] Generating enablement topics...")
        enablement = generate_enablement_topics(analyses)
        out = Path("output") / "enablement_topics.md"
        out.write_text(enablement)
        print(f"        Saved → {out}")

    print(f"\n{'='*60}")
    print("ALL OUTPUTS GENERATED")
    print(f"  Playbooks:    output/playbooks/")
    print(f"  Scorecards:   output/scorecards/")
    print(f"  Library:      output/transcript_library/winning_moments.md")
    print(f"  Enablement:   output/enablement_topics.md")
    print(f"{'='*60}\n")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--no-playbooks", action="store_true")
    parser.add_argument("--no-scorecards", action="store_true")
    parser.add_argument("--no-library", action="store_true")
    parser.add_argument("--no-enablement", action="store_true")
    args = parser.parse_args()

    run(
        skip_playbooks=args.no_playbooks,
        skip_scorecards=args.no_scorecards,
        skip_library=args.no_library,
        skip_enablement=args.no_enablement,
    )
