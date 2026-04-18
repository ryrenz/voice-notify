#!/usr/bin/env python3
"""
voice_mode.py — Switch voice-notify backend and Fish sub-mode.

Usage:
  python3 voice_mode.py                # Show current config
  python3 voice_mode.py local          # Switch to local TTS (zero-config)
  python3 voice_mode.py fish           # Switch to Fish Audio (keep current sub-mode)
  python3 voice_mode.py fish cache     # Switch to Fish Audio + cache sub-mode
  python3 voice_mode.py fish api       # Switch to Fish Audio + api sub-mode
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Allow importing sibling modules when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config


FISH_SETUP_HINT = """\
Next steps:
  1. Get a Fish Audio API key: https://fish.audio (Account -> API Keys)
  2. Find voice model IDs at: https://fish.audio/discovery/
  3. Add them to ~/.claude/voice-notify/voices.json under the "fish.voices" section
  4. Set FISH_API_KEY in ~/.claude/voice-notify/.env

See README.md -> "Fish Audio Setup" for detailed steps.
"""


def _fish_has_voices(voice_config: dict) -> bool:
    """Return True if fish.voices has at least one entry with a model_id."""
    fish = voice_config.get("fish", {})
    if not isinstance(fish, dict):
        return False
    voices = fish.get("voices", {})
    if not isinstance(voices, dict) or not voices:
        return False
    for voice in voices.values():
        if isinstance(voice, dict) and voice.get("model_id"):
            return True
    return False


def _load_or_seed() -> dict:
    """Load voices.json, seeding from voices.example.json if missing."""
    cfg = config.load_voice_config()
    if cfg:
        return cfg

    # Seed from example file
    example = Path(os.path.dirname(os.path.abspath(__file__))) / "voices.example.json"
    if example.exists():
        try:
            return json.loads(example.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _show_current() -> None:
    """Print the current backend and relevant sub-config."""
    backend = config.get_backend()
    print(f"Backend: {backend}")
    if backend == "local":
        local = config.get_local_config()
        print(f"  voice: {local['voice']}")
        print(f"  completion_text: {local['completion_text']}")
        print(f"  permission_text: {local['permission_text']}")
    else:
        fish = config.get_fish_config()
        print(f"  current character: {fish.get('current', '(unset)')}")
        print(f"  notify_mode: {config.get_notify_mode()}")


def main():
    if len(sys.argv) < 2:
        _show_current()
        return

    target = sys.argv[1]
    if target not in ("local", "fish"):
        print(
            "Usage: python3 voice_mode.py [local|fish [cache|api]]",
            file=sys.stderr,
        )
        sys.exit(1)

    voice_config = _load_or_seed()
    if not voice_config:
        print(
            "Error: no voice config found. Run install.sh first or copy "
            "voices.example.json to voices.json.",
            file=sys.stderr,
        )
        sys.exit(1)

    voice_config["backend"] = target

    if target == "fish" and len(sys.argv) >= 3:
        sub_mode = sys.argv[2]
        if sub_mode not in ("cache", "api"):
            print(
                "Usage: python3 voice_mode.py fish [cache|api]",
                file=sys.stderr,
            )
            sys.exit(1)
        fish = voice_config.get("fish")
        if not isinstance(fish, dict):
            fish = {}
            voice_config["fish"] = fish
        fish["notify_mode"] = sub_mode

    config.save_voice_config(voice_config)

    if target == "fish":
        notify_mode = voice_config.get("fish", {}).get("notify_mode", "api")
        print(f"Backend set to: fish ({notify_mode} mode)")

        # Warn if no voices are configured — common on first switch
        if not _fish_has_voices(voice_config):
            print()
            print("Switched to fish backend, but no voices are configured yet.")
            print()
            print(FISH_SETUP_HINT, end="")
    else:
        print("Backend set to: local")


if __name__ == "__main__":
    main()
