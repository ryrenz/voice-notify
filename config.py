#!/usr/bin/env python3
"""
config.py — Shared configuration for voice-notify hooks.

Handles .env loading, API key resolution, voice config, and install paths.
Works both from the repo directory and when installed to ~/.claude/voice-notify/.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

INSTALL_DIR = Path.home() / ".claude" / "voice-notify"


def _script_dir() -> Path:
    """Directory containing the currently running script."""
    return Path(os.path.dirname(os.path.abspath(__file__)))


def get_install_dir() -> Path:
    """Return INSTALL_DIR, creating it if needed."""
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    return INSTALL_DIR


def _find_file(name: str) -> Path | None:
    """Locate a file by checking install dir first, then script dir."""
    for d in (INSTALL_DIR, _script_dir()):
        p = d / name
        if p.exists():
            return p
    return None


def load_env() -> None:
    """Load .env file into os.environ (does not override existing vars)."""
    env_file = _find_file(".env")
    if not env_file:
        return
    try:
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value
    except OSError as e:
        print(f"config: failed to load .env: {e}", file=sys.stderr)


def get_api_key(name: str) -> str:
    """
    Get an API key by name. Check order:
    1. Environment variable (e.g. FISH_API_KEY)
    2. .env file (loaded by load_env)
    """
    load_env()
    return os.environ.get(name, "")


def load_voice_config() -> dict:
    """Load voice config JSON. Returns the parsed dict or empty dict on failure."""
    config_file = _find_file("voices.json")
    if not config_file:
        return {}
    try:
        return json.loads(config_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"config: voice config error: {e}", file=sys.stderr)
        return {}


def save_voice_config(config: dict) -> None:
    """Save voice config to the install dir (or script dir if not installed)."""
    target = INSTALL_DIR / "voices.json"
    if not target.parent.exists():
        target = _script_dir() / "voices.json"
    try:
        target.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as e:
        print(f"config: failed to save voice config: {e}", file=sys.stderr)


def get_backend() -> str:
    """Return 'local' (default) or 'fish'."""
    config = load_voice_config()
    backend = config.get("backend", "local")
    if backend not in ("local", "fish"):
        return "local"
    return backend


def get_local_config() -> dict:
    """Return the local backend sub-config with sane defaults."""
    config = load_voice_config()
    local = config.get("local", {}) if isinstance(config.get("local"), dict) else {}
    return {
        "voice": local.get("voice", "auto"),
        "completion_text": local.get("completion_text", "任务完成"),
        "permission_text": local.get("permission_text", "需要你的确认"),
    }


def get_fish_config() -> dict:
    """Return the fish backend sub-config (raw dict, may be empty)."""
    config = load_voice_config()
    fish = config.get("fish", {})
    return fish if isinstance(fish, dict) else {}


def get_current_voice() -> tuple[str | None, str]:
    """Return (model_id, character_name) from fish sub-config, or (None, '')."""
    fish = get_fish_config()
    current = fish.get("current", "")
    voices = fish.get("voices", {})
    if current and current in voices:
        voice = voices[current]
        model_id = voice.get("model_id", "")
        name = voice.get("name", current)
        if model_id:
            return model_id, name
    return None, ""


def get_notify_mode() -> str:
    """Return 'cache' or 'api' (default) from fish sub-config."""
    fish = get_fish_config()
    mode = fish.get("notify_mode", "api")
    if mode not in ("cache", "api"):
        return "api"
    return mode


def get_cache_dir() -> Path:
    """Return the notify cache directory path."""
    return INSTALL_DIR / "cache" / "notify"


def get_permission_cache_dir() -> Path:
    """Return the permission audio cache directory path."""
    return INSTALL_DIR / "cache" / "permission"


def get_mute_file() -> Path:
    """Return the mute flag file path."""
    return INSTALL_DIR / ".voice_mute"


def load_characters() -> dict:
    """Load characters.json. Returns dict of character data."""
    char_file = _find_file("characters.json")
    if not char_file:
        print("config: characters.json not found", file=sys.stderr)
        return {}
    try:
        return json.loads(char_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"config: characters.json error: {e}", file=sys.stderr)
        return {}


def get_llm_config() -> tuple[str, str, str]:
    """
    Return (api_url, api_key, model) for LLM summarization.
    Supports custom OpenAI-compatible endpoints via LLM_API_URL/LLM_API_KEY/LLM_MODEL.
    Falls back to DeepSeek.
    """
    load_env()
    api_url = os.environ.get("LLM_API_URL", "https://api.deepseek.com/chat/completions")
    model = os.environ.get("LLM_MODEL", "deepseek-chat")

    # LLM_API_KEY takes priority, then DEEPSEEK_API_KEY
    api_key = os.environ.get("LLM_API_KEY", "")
    if not api_key:
        api_key = get_api_key("DEEPSEEK_API_KEY")

    return api_url, api_key, model
