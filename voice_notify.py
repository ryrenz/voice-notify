#!/usr/bin/env python3
"""
voice_notify.py — Claude Code Stop hook.

Announces task completion via AI-generated character voices.
- Cache mode: plays a random pre-generated audio clip (no API calls).
- API mode: summarizes the last assistant response with an LLM, then generates
  TTS audio via Fish Audio in real time.

Hook registration (Claude Code settings.json):
  {"event": "stop", "command": "python3 ~/.claude/voice-notify/voice_notify.py"}

Input: reads JSON from stdin (Claude Code hook protocol).
"""

from __future__ import annotations

import json
import os
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Allow importing sibling modules when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import audio
import tts_local

MAX_CONTEXT_CHARS = 1500


def read_hook_input() -> dict:
    """Read JSON hook input from stdin."""
    try:
        return json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return {}


def extract_last_turn(transcript_path: str) -> str:
    """Extract the last user message + final assistant text blocks from transcript."""
    if not transcript_path or not Path(transcript_path).exists():
        return ""

    last_user_text = ""
    assistant_text_blocks: list[str] = []

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entry_type = entry.get("type", "")
                    if entry_type not in ("user", "assistant"):
                        continue

                    message = entry.get("message", {})
                    content = message.get("content", "")

                    if entry_type == "user":
                        blocks: list[str] = []
                        if isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    text = block.get("text", "").strip()
                                    if text:
                                        blocks.append(text)
                        elif isinstance(content, str) and content.strip():
                            blocks.append(content.strip())
                        if blocks:
                            last_user_text = "\n".join(blocks)
                            assistant_text_blocks = []

                    elif entry_type == "assistant":
                        if isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    text = block.get("text", "").strip()
                                    if text:
                                        assistant_text_blocks.append(text)
                        elif isinstance(content, str) and content.strip():
                            assistant_text_blocks.append(content.strip())

                except json.JSONDecodeError:
                    continue
    except (IOError, PermissionError) as e:
        print(f"voice_notify: transcript read error: {e}", file=sys.stderr)

    if not last_user_text:
        return ""

    parts = [f"[用户]: {last_user_text}"]
    # Take last 2 individual text blocks: substance + conclusion
    for block in assistant_text_blocks[-2:]:
        parts.append(f"[助手]: {block}")

    return "\n\n".join(parts)


def summarize_with_llm(text: str, character: str = "") -> str | None:
    """Call LLM API to produce a one-sentence voice-friendly summary in character."""
    import urllib.request

    # Strip fenced code blocks and inline code to reduce noise
    cleaned = re.sub(r'```[\s\S]*?```', '', text)
    cleaned = re.sub(r'`[^`]+`', '', cleaned)
    cleaned = cleaned.strip()[:MAX_CONTEXT_CHARS]

    system_parts = [
        "你是一个语音播报助手。根据用户提供的对话内容，用一句口语化的中文总结完成了什么。",
        "要求：10-20字，自然可朗读，只输出总结本身，禁止输出任何元描述或提示词。",
    ]
    if character:
        system_parts.append(
            f"语气模仿{character}，但绝对不能出现「{character}」这个名字或任何角色名。"
        )
    system_prompt = "\n".join(system_parts)

    api_url, api_key, model = config.get_llm_config()
    if not api_key:
        print("voice_notify: LLM API key not found", file=sys.stderr)
        return None

    payload = json.dumps({
        "model": model,
        "max_tokens": 50,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": cleaned},
        ],
    }).encode("utf-8")

    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            body = json.loads(response.read().decode("utf-8"))
            choices = body.get("choices", [])
            if choices:
                result = choices[0].get("message", {}).get("content", "").strip()
                # Strip wrapping quotes/brackets that LLM sometimes adds
                result = result.strip('"\'「」『』""''')
                return result
    except Exception as e:
        print(f"voice_notify: LLM API error: {e}", file=sys.stderr)

    return None


def tts_and_play(text: str) -> None:
    """Generate TTS audio via Fish Audio API, then play it."""
    fish_key = config.get_api_key("FISH_API_KEY")
    if not fish_key:
        print("voice_notify: FISH_API_KEY not set", file=sys.stderr)
        return

    model_id, _ = config.get_current_voice()
    if not model_id:
        print("voice_notify: no voice model_id configured", file=sys.stderr)
        return

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    request_body = json.dumps({
        "text": text,
        "reference_id": model_id,
        "format": "mp3",
    })

    try:
        result = subprocess.run(
            [
                "curl", "-sS", "--fail-with-body",
                "--connect-timeout", "5",
                "--max-time", "15",
                "-X", "POST",
                "https://api.fish.audio/v1/tts",
                "-H", f"Authorization: Bearer {fish_key}",
                "-H", "Content-Type: application/json",
                "-H", "model: s1",
                "-d", request_body,
                "--output", tmp_path,
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )

        if result.returncode != 0:
            print(f"voice_notify: Fish Audio API failed: {result.stderr[:200]}", file=sys.stderr)
            return

        if Path(tmp_path).stat().st_size == 0:
            print("voice_notify: Fish Audio returned empty audio", file=sys.stderr)
            return

        audio.play_audio(tmp_path)
    except subprocess.TimeoutExpired:
        print("voice_notify: Fish Audio request timed out", file=sys.stderr)
    except (FileNotFoundError, OSError) as e:
        print(f"voice_notify: error: {e}", file=sys.stderr)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def play_cached_notify() -> None:
    """Pick a random cached notify audio and play it."""
    model_id, _ = config.get_current_voice()
    if not model_id:
        return

    cache_dir = config.get_cache_dir() / model_id
    if not cache_dir.is_dir():
        print(f"voice_notify: no cache dir for {model_id}", file=sys.stderr)
        return

    files = sorted(cache_dir.glob("*.mp3"))
    if not files:
        print(f"voice_notify: no cached files in {cache_dir}", file=sys.stderr)
        return

    chosen = random.choice(files)
    audio.play_audio(str(chosen))


def main():
    if config.get_mute_file().exists():
        return

    backend = config.get_backend()

    # Local backend: zero-config system TTS (optionally LLM-enhanced)
    if backend == "local":
        local_cfg = config.get_local_config()
        text = local_cfg.get("completion_text", "任务完成")

        # If an LLM key is available, replace static text with a summary
        _, llm_key, _ = config.get_llm_config()
        if llm_key:
            hook_input = read_hook_input()
            raw_text = extract_last_turn(hook_input.get("transcript_path", ""))
            if raw_text:
                summary = summarize_with_llm(raw_text, "")
                if summary:
                    if summary[-1] not in "。！？!?.~～":
                        summary += "。"
                    text = summary

        tts_local.local_tts(text, local_cfg.get("voice", "auto"))
        return

    # Fish backend: existing cache/api logic
    # Cache mode: play pre-generated audio, skip all API calls
    if config.get_notify_mode() == "cache":
        play_cached_notify()
        return

    # API mode: LLM summarize + Fish Audio TTS
    hook_input = read_hook_input()
    transcript_path = hook_input.get("transcript_path", "")

    raw_text = extract_last_turn(transcript_path)
    if not raw_text:
        return

    _, character = config.get_current_voice()
    summary = summarize_with_llm(raw_text, character)

    if not summary:
        return

    # Ensure sentence-ending punctuation for natural TTS prosody
    if summary and summary[-1] not in "。！？!?.~～":
        summary += "。"

    tts_and_play(summary)


if __name__ == "__main__":
    main()
