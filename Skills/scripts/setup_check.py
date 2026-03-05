#!/usr/bin/env python3
"""
Setup Check — verify all API keys and dependencies are configured
Run this before the first pipeline run: python scripts/setup_check.py
"""

import os
import sys
import subprocess

REQUIRED = {
    "ANTHROPIC_API_KEY": {
        "desc": "Anthropic API key for Claude analysis",
        "get": "https://console.anthropic.com/settings/keys",
    },
    "FATHOM_API_KEY": {
        "desc": "Fathom API key for pulling call transcripts",
        "get": "https://app.fathom.video/settings/api",
        "default": "YOUR_FATHOM_API_KEY",
    },
}

OPTIONAL = {
    "LEMLIST_API_KEY": {
        "desc": "Lemlist API key for call step enrichment",
        "get": "https://app.lemlist.com/settings/integration",
    },
}


def check_env():
    ok = True
    print("\n=== ENVIRONMENT VARIABLES ===")
    for var, info in REQUIRED.items():
        val = os.environ.get(var, info.get("default", ""))
        if val:
            print(f"  ✓ {var} ({len(val)} chars)")
        else:
            print(f"  ✗ {var} — MISSING")
            print(f"    {info['desc']}")
            print(f"    Get it: {info['get']}")
            print(f"    Set it: export {var}=<your-key>")
            ok = False

    print()
    for var, info in OPTIONAL.items():
        val = os.environ.get(var, "")
        status = f"✓ set" if val else "○ not set (optional)"
        print(f"  {status} — {var}")
    return ok


def check_packages():
    ok = True
    print("\n=== PYTHON PACKAGES ===")
    for pkg in ["requests", "anthropic"]:
        try:
            __import__(pkg)
            import importlib.metadata
            ver = importlib.metadata.version(pkg)
            print(f"  ✓ {pkg} ({ver})")
        except Exception:
            print(f"  ✗ {pkg} — not installed. Run: pip install {pkg}")
            ok = False
    return ok


def check_fathom():
    print("\n=== FATHOM API CONNECTION ===")
    try:
        import requests
        key = os.environ.get("FATHOM_API_KEY", "YOUR_FATHOM_API_KEY")
        resp = requests.get(
            "https://api.fathom.ai/external/v1/meetings",
            headers={"X-Api-Key": key},
            params={"include_transcript": "false"},
            timeout=10,
        )
        if resp.status_code == 200:
            count = len(resp.json().get("items", []))
            print(f"  ✓ Connected — {count} meetings on first page")
            return True
        else:
            print(f"  ✗ HTTP {resp.status_code}: {resp.text[:100]}")
            return False
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return False


def check_anthropic():
    print("\n=== ANTHROPIC API CONNECTION ===")
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        print("  ✗ ANTHROPIC_API_KEY not set — skipping connection test")
        return False
    try:
        import anthropic
        c = anthropic.Anthropic(api_key=key)
        msg = c.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{"role": "user", "content": "hi"}],
        )
        print(f"  ✓ Connected — model: claude-haiku-4-5-20251001")
        return True
    except Exception as e:
        print(f"  ✗ {e}")
        return False


def check_output_dirs():
    print("\n=== OUTPUT DIRECTORIES ===")
    from pathlib import Path
    dirs = [
        "output/calls",
        "output/analysis",
        "output/playbooks",
        "output/scorecards",
        "output/transcript_library",
        "output/lemlist",
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {d}/")


if __name__ == "__main__":
    print("=" * 50)
    print("CALL INTELLIGENCE — SETUP CHECK")
    print("=" * 50)

    env_ok = check_env()
    pkg_ok = check_packages()
    fathom_ok = check_fathom()
    anthropic_ok = check_anthropic()
    check_output_dirs()

    print("\n" + "=" * 50)
    if env_ok and pkg_ok and fathom_ok and anthropic_ok:
        print("ALL CHECKS PASSED — ready to run the pipeline")
        print("\nRun:")
        print("  python scripts/run_call_intelligence.py --after 2025-09-01")
    else:
        print("SETUP INCOMPLETE — fix the issues above first")
        if not env_ok:
            print("\nQuick setup (add to your ~/.zshrc or ~/.bashrc):")
            print("  export ANTHROPIC_API_KEY=sk-ant-...")
            print("  export FATHOM_API_KEY=T5I2SY6h...")
        sys.exit(1)
