# voice-notify

AI character voice notifications for Claude Code — announces task completion and permission requests.

When a task finishes, an LLM summarizes the last conversation turn into one sentence, then Fish Audio TTS speaks it in your chosen character's voice. Permission requests play a cached character-specific prompt.

## Features

- **Task completion announcements** — real-time LLM summary + TTS (API mode) or pre-generated cached audio (Cache mode)
- **Permission request alerts** — auto-cached character voice prompts, no repeated API calls
- **13 built-in characters** — Paimon, Diluc, Zhongli, Yae Miko, Cao Cao, Crayon Shin-chan, and more, each with unique personality and lines

## Quick Start

```bash
# 1. Clone
git clone https://github.com/ryrenz/voice-notify.git
cd voice-notify

# 2. Install
chmod +x install.sh && ./install.sh

# 3. Add API keys
nano ~/.claude/voice-notify/.env
# Fill in FISH_API_KEY and DEEPSEEK_API_KEY

# 4. Add hooks (follow install.sh output)
claude /hooks
# Stop hook: python3 ~/.claude/voice-notify/voice_notify.py
# Notification hook: python3 ~/.claude/voice-notify/voice_permission.py
```

Done! You'll hear character voice notifications whenever Claude Code completes a task or requests permission.

## Configuration

### API Keys

Edit `~/.claude/voice-notify/.env`:

```bash
# Required: Fish Audio TTS
FISH_API_KEY=your_key_here

# Required for API mode: DeepSeek (for conversation summarization)
DEEPSEEK_API_KEY=your_key_here

# Optional: Use any OpenAI-compatible API instead of DeepSeek
# LLM_API_URL=https://api.openai.com/v1/chat/completions
# LLM_API_KEY=your_key
# LLM_MODEL=gpt-4o-mini
```

### Switch Character

Edit `~/.claude/voice-notify/voices.json`, change the `"current"` field:

```json
{
  "current": "曹操",
  "voices": { ... }
}
```

### Switch Mode

```bash
python3 ~/.claude/voice-notify/voice_mode.py cache  # Cache mode (offline, low latency)
python3 ~/.claude/voice-notify/voice_mode.py api    # API mode (real-time summary, more natural)
python3 ~/.claude/voice-notify/voice_mode.py        # Show current mode
```

### Generate Cache

Cache mode requires pre-generated audio. Each character takes ~15 seconds:

```bash
python3 ~/.claude/voice-notify/generate_cache.py                     # All characters
python3 ~/.claude/voice-notify/generate_cache.py --character 派蒙     # Single character
python3 ~/.claude/voice-notify/generate_cache.py --dry-run           # Preview only
python3 ~/.claude/voice-notify/generate_cache.py --force             # Force regenerate
```

## Adding Custom Characters

1. Find a voice model on [Fish Audio](https://fish.audio), copy its model_id

2. Add to `voices.json`:
```json
{
  "current": "YourCharacter",
  "voices": {
    "YourCharacter": {
      "name": "YourCharacter",
      "model_id": "model_id_from_fish_audio"
    }
  }
}
```

3. Add character lines to `characters.json` (optional, needed for Cache mode):
```json
{
  "YourCharacter": {
    "permission_prompt": "What to say on permission requests",
    "completion_lines": [
      "Task done line 1",
      "Task done line 2"
    ]
  }
}
```

4. Generate cache if using Cache mode:
```bash
python3 ~/.claude/voice-notify/generate_cache.py --character YourCharacter
```

## How It Works

```
Claude Code task complete (Stop hook)
  │
  ├─ Cache mode → pick random pre-generated audio → play
  │
  └─ API mode → read transcript → LLM summarize → Fish Audio TTS → play

Claude Code permission request (Notification hook)
  │
  └─ check cache → generate & cache if missing → play character prompt
```

## Requirements

- Python 3.9+
- macOS (afplay) or Linux (paplay / aplay / mpv)
- curl
- No pip dependencies

## Uninstall

```bash
chmod +x uninstall.sh && ./uninstall.sh
# Then remove hooks from Claude Code
```

## FAQ

**Q: Are both API keys required?**

Cache mode only needs FISH_API_KEY (used once to generate cache). API mode needs both.

**Q: Can I use OpenAI or another LLM instead of DeepSeek?**

Yes. Set `LLM_API_URL`, `LLM_API_KEY`, and `LLM_MODEL` in .env. Any OpenAI-compatible endpoint works.

**Q: How do I mute temporarily?**

```bash
touch ~/.claude/voice-notify/.voice_mute   # Mute
rm ~/.claude/voice-notify/.voice_mute      # Unmute
```

**Q: Windows support?**

v1 supports macOS and Linux only.

## License

MIT
