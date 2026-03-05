#!/usr/bin/env python3
"""
Call Intelligence Pipeline — full end-to-end runner
Pulls Fathom transcripts → analyses with Claude → generates playbooks, scorecards, library, enablement topics
"""

import subprocess
import sys
import os
from pathlib import Path

SCRIPTS = Path(__file__).parent


def run_step(script: str, args: list[str] = None):
    cmd = [sys.executable, str(SCRIPTS / script)] + (args or [])
    print(f"\n>>> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    if result.returncode != 0:
        print(f"\nERROR: {script} failed with code {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Full call intelligence pipeline")
    parser.add_argument("--after", help="Only fetch meetings after this date (e.g. 2025-01-01)")
    parser.add_argument("--refresh", action="store_true", help="Re-fetch and re-analyse all")
    parser.add_argument("--skip-pull", action="store_true", help="Skip Fathom pull (use cached)")
    parser.add_argument("--skip-lemlist", action="store_true", help="Skip Lemlist enrichment")
    parser.add_argument("--skip-analyse", action="store_true", help="Skip Claude analysis (use cached)")
    args = parser.parse_args()

    print("=" * 60)
    print("CALL INTELLIGENCE PIPELINE")
    print("=" * 60)

    # Step 1: Pull Fathom transcripts
    if not args.skip_pull:
        pull_args = []
        if args.after:
            pull_args += ["--after", args.after]
        if args.refresh:
            pull_args.append("--refresh")
        run_step("fathom_puller.py", pull_args)
    else:
        print("\n>>> [SKIP] Fathom pull (using cache)")

    # Step 2: Pull Lemlist call activities (optional enrichment)
    if not args.skip_lemlist and os.getenv("LEMLIST_API_KEY"):
        run_step("lemlist_calls.py")
    else:
        print("\n>>> [SKIP] Lemlist enrichment (no LEMLIST_API_KEY or --skip-lemlist)")

    # Step 3: Analyse with Claude
    if not args.skip_analyse:
        analyse_args = ["--refresh"] if args.refresh else []
        run_step("call_analyzer.py", analyse_args)
    else:
        print("\n>>> [SKIP] Claude analysis (using cache)")

    # Step 4: Generate all outputs
    run_step("generate_outputs.py")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print("""
  output/
  ├── calls/              raw Fathom transcripts (JSON)
  ├── lemlist/            Lemlist call activities (JSON)
  ├── analysis/           per-call Claude analysis (JSON)
  ├── playbooks/          vertical playbooks (Markdown)
  ├── scorecards/         per-rep scorecards (Markdown)
  ├── transcript_library/ winning moments (Markdown)
  └── enablement_topics.md prioritised training agenda
""")
