#!/usr/bin/env python3
"""
voice_permission.py — Claude Code Notification hook.

Plays a character-appropriate voice prompt when Claude Code requests permission.
Caches generated audio per voice model to avoid repeated API calls.

Hook registration (Claude Code settings.json):
  {"event": "notification", "command": "python3 ~/.claude/voice-notify/voice_permission.py"}

Input: reads JSON from stdin (Claude Code hook protocol).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Allow importing sibling modules when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import audio
import tts_local

DEFAULT_PROMPT = "需要你的确认。"


def load_permission_prompt(character: str) -> str:
    """Load the permission prompt for a character from characters.json."""
    characters = config.load_characters()
    if character in characters:
        return characters[character].get("permission_prompt", DEFAULT_PROMPT)
    return DEFAULT_PROMPT


def generate_audio(model_id: str, text: str, output_path: Path, api_key: str) -> bool:
    """Call Fish Audio TTS and save to output_path atomically."""
    cache_dir = output_path.parent
    cache_dir.mkdir(parents=True, exist_ok=True)

    request_body = json.dumps({
        "text": text,
        "reference_id": model_id,
        "format": "mp3",
    })

    # Write to temp file first, then atomic rename to avoid partial cache
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp3", dir=str(cache_dir))
    os.close(tmp_fd)

    try:
        result = subprocess.run(
            [
                "curl", "-sS", "--fail-with-body",
                "--connect-timeout", "5",
                "--max-time", "15",
                "-X", "POST",
                "https://api.fish.audio/v1/tts",
                "-H", f"Authorization: Bearer {api_key}",
                "-H", "Content-Type: application/json",
                "-H", "model: s1",
                "-d", request_body,
                "--output", tmp_path,
            ],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0:
            print(f"voice_permission: Fish Audio failed: {result.stderr[:200]}",
                  file=sys.stderr)
            return False
        if Path(tmp_path).stat().st_size == 0:
            return False
        os.rename(tmp_path, str(output_path))
        return True
    except (subprocess.TimeoutExpired, OSError) as e:
        print(f"voice_permission: error: {e}", file=sys.stderr)
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def main():
    if config.get_mute_file().exists():
        return

    backend = config.get_backend()

    # Local backend: zero-config system TTS
    if backend == "local":
        local_cfg = config.get_local_config()
        text = local_cfg.get("permission_text", "需要你的确认")
        tts_local.local_tts(text, local_cfg.get("voice", "auto"))
        return

    # Fish backend: cached permission audio
    model_id, character = config.get_current_voice()
    if not model_id:
        print("voice_permission: no voice configured", file=sys.stderr)
        return

    prompt = load_permission_prompt(character)

    cache_dir = config.get_permission_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached_file = cache_dir / f"{model_id}.mp3"

    if not cached_file.exists():
        api_key = config.get_api_key("FISH_API_KEY")
        if not api_key:
            print("voice_permission: FISH_API_KEY not set", file=sys.stderr)
            return
        if not generate_audio(model_id, prompt, cached_file, api_key):
            return

    # Fire-and-forget playback so the Notification hook returns immediately
    audio.play_audio_fire_and_forget(str(cached_file))


if __name__ == "__main__":
    main()
