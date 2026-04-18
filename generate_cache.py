#!/usr/bin/env python3
"""
generate_cache.py — Pre-generate task completion voice cache for all characters.

Generates 10 audio files per character using Fish Audio TTS, stored in:
  ~/.claude/voice-notify/cache/notify/{model_id}/01.mp3 ... 10.mp3

Usage:
  python3 generate_cache.py                    # Generate all (skip existing)
  python3 generate_cache.py --dry-run          # Print plan only
  python3 generate_cache.py --character 蜡笔小新  # Single character
  python3 generate_cache.py --force            # Regenerate even if exists
  python3 generate_cache.py --delay 2          # Seconds between API calls
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Allow importing sibling modules when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config


def load_voice_map() -> dict[str, str]:
    """Load fish sub-config and return {character_name: model_id} map."""
    fish = config.get_fish_config()
    voices = fish.get("voices", {})
    result = {}
    for key, voice in voices.items():
        model_id = voice.get("model_id", "")
        if model_id and model_id != "x":
            result[key] = model_id
    return result


def generate_audio(model_id: str, text: str, output_path: Path, api_key: str) -> bool:
    """Call Fish Audio TTS and save to output_path atomically."""
    request_body = json.dumps({
        "text": text,
        "reference_id": model_id,
        "format": "mp3",
    })
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp3", dir=str(output_path.parent))
    os.close(tmp_fd)
    try:
        result = subprocess.run(
            [
                "curl", "-sS", "--fail-with-body",
                "--connect-timeout", "5",
                "--max-time", "20",
                "-X", "POST",
                "https://api.fish.audio/v1/tts",
                "-H", f"Authorization: Bearer {api_key}",
                "-H", "Content-Type: application/json",
                "-H", "model: s1",
                "-d", request_body,
                "--output", tmp_path,
            ],
            capture_output=True, text=True, timeout=25,
        )
        if result.returncode != 0:
            print(f"  FAILED: {result.stderr[:200]}", file=sys.stderr)
            return False
        if Path(tmp_path).stat().st_size == 0:
            print("  FAILED: empty audio response", file=sys.stderr)
            return False
        os.rename(tmp_path, str(output_path))
        return True
    except (subprocess.TimeoutExpired, OSError) as e:
        print(f"  FAILED: {e}", file=sys.stderr)
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="Generate notify voice cache for all characters"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Print plan without generating audio")
    parser.add_argument("--character", type=str,
                        help="Generate for a single character only")
    parser.add_argument("--force", action="store_true",
                        help="Regenerate even if files exist")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Seconds between API calls (default: 1.0)")
    args = parser.parse_args()

    characters = config.load_characters()
    if not characters:
        print("Error: no characters found in characters.json", file=sys.stderr)
        sys.exit(1)

    voices = load_voice_map()
    if not voices:
        print(
            "No voices configured. Add at least one voice to "
            "~/.claude/voice-notify/voices.json (see README -> Fish Audio Setup).",
            file=sys.stderr,
        )
        sys.exit(1)

    # Filter characters
    char_names = list(characters.keys())
    if args.character:
        if args.character not in characters:
            print(f"Error: character '{args.character}' not found in characters.json",
                  file=sys.stderr)
            print(f"Available: {', '.join(characters.keys())}", file=sys.stderr)
            sys.exit(1)
        if args.character not in voices:
            print(f"Error: character '{args.character}' not found in voice config",
                  file=sys.stderr)
            sys.exit(1)
        char_names = [args.character]

    cache_dir = config.get_cache_dir()

    if not args.dry_run:
        api_key = config.get_api_key("FISH_API_KEY")
        if not api_key:
            print("Error: FISH_API_KEY not set", file=sys.stderr)
            sys.exit(1)

    total = 0
    skipped = 0
    failed = 0
    generated = 0

    for char in char_names:
        if char not in voices:
            print(f"Skipping {char}: not in voice config")
            continue

        model_id = voices[char]
        lines = characters[char].get("completion_lines", [])
        if not lines:
            print(f"Skipping {char}: no completion_lines")
            continue

        char_dir = cache_dir / model_id

        print(f"\n{'=' * 40}")
        print(f"Character: {char} ({model_id})")
        print(f"Cache dir: {char_dir}")
        print(f"{'=' * 40}")

        if not args.dry_run:
            char_dir.mkdir(parents=True, exist_ok=True)

        for i, line in enumerate(lines, 1):
            filename = f"{i:02d}.mp3"
            filepath = char_dir / filename
            total += 1

            if args.dry_run:
                status = "[EXISTS]" if filepath.exists() else "[PENDING]"
                print(f"  {filename} {status} \"{line}\"")
                continue

            if filepath.exists() and not args.force:
                print(f"  {filename} [SKIP] already exists")
                skipped += 1
                continue

            print(f"  {filename} generating: \"{line}\"")
            if generate_audio(model_id, line, filepath, api_key):
                size = filepath.stat().st_size
                print(f"  {filename} [OK] {size} bytes")
                generated += 1
            else:
                failed += 1

            if i < len(lines):
                time.sleep(args.delay)

        # Brief pause between characters
        if not args.dry_run and char != char_names[-1]:
            time.sleep(args.delay * 2)

    print(f"\n{'=' * 40}")
    print(f"Summary: {total} total, {generated} generated, {skipped} skipped, {failed} failed")
    if args.dry_run:
        print("(dry-run mode -- no files were generated)")
    print(f"{'=' * 40}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
