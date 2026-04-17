#!/usr/bin/env python3
"""
tts_local.py — System TTS wrapper for voice-notify local backend.

Zero-dependency text-to-speech using platform built-ins:
  - macOS: `say`
  - Linux: `spd-say` (preferred, supports Chinese) or `espeak`
"""

from __future__ import annotations

import shutil
import subprocess
import sys


def local_tts(text: str, voice: str = "auto") -> None:
    """Speak text using system TTS. macOS: say. Linux: spd-say/espeak."""
    if not text:
        return

    if sys.platform == "darwin":
        cmd = ["say"]
        if voice and voice != "auto":
            cmd.extend(["-v", voice])
        cmd.append(text)
        try:
            subprocess.Popen(cmd)  # fire-and-forget
        except (FileNotFoundError, OSError) as e:
            print(f"tts_local: say failed: {e}", file=sys.stderr)
        return

    if sys.platform.startswith("linux"):
        # Try spd-say first (fastest, supports Chinese), then espeak
        if shutil.which("spd-say"):
            try:
                subprocess.Popen(["spd-say", "--wait", text])
            except (FileNotFoundError, OSError) as e:
                print(f"tts_local: spd-say failed: {e}", file=sys.stderr)
            return
        if shutil.which("espeak"):
            voice_arg = voice if voice and voice != "auto" else "zh"
            try:
                subprocess.Popen(["espeak", "-v", voice_arg, text])
            except (FileNotFoundError, OSError) as e:
                print(f"tts_local: espeak failed: {e}", file=sys.stderr)
            return
        print(
            "tts_local: install speech-dispatcher or espeak",
            file=sys.stderr,
        )
        return

    print(f"tts_local: unsupported platform {sys.platform}", file=sys.stderr)
