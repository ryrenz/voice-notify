#!/usr/bin/env python3
"""
voice_mode.py — Switch voice notify mode between 'cache' and 'api'.

Usage:
  python3 voice_mode.py          # Show current mode
  python3 voice_mode.py cache    # Use pre-cached audio (no API calls)
  python3 voice_mode.py api      # Use real-time LLM + Fish Audio TTS
"""

from __future__ import annotations

import os
import sys

# Allow importing sibling modules when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config


def main():
    if len(sys.argv) < 2:
        # Show current mode
        mode = config.get_notify_mode()
        print(f"Current voice notify mode: {mode}")
        return

    mode = sys.argv[1]
    if mode not in ("cache", "api"):
        print("Usage: python3 voice_mode.py [cache|api]", file=sys.stderr)
        sys.exit(1)

    voice_config = config.load_voice_config()
    if not voice_config:
        print("Error: no voice config found. Run install.sh first or copy "
              "voices.example.json to voices.json.", file=sys.stderr)
        sys.exit(1)

    voice_config["notify_mode"] = mode
    config.save_voice_config(voice_config)
    print(f"Voice notify mode set to: {mode}")


if __name__ == "__main__":
    main()
