# voice-notify

Voice notifications for Claude Code — announces task completion and permission requests.

## Quick start (30 seconds, zero config)

```bash
git clone https://github.com/ryrenz/voice-notify.git
cd voice-notify
./install.sh
```

Then paste this into the `hooks` section of `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {"hooks": [{"type": "command", "command": "python3 ~/.claude/voice-notify/voice_notify.py"}]}
    ],
    "Notification": [
      {"hooks": [{"type": "command", "command": "python3 ~/.claude/voice-notify/voice_permission.py"}]}
    ]
  }
}
```

Done. Every time Claude Code finishes a task it says "任务完成" (task done); on permission requests it says "需要你的确认" (needs your confirmation), using your system's built-in TTS voice.

## Upgrade: anime character voices (Fish Audio)

Tired of the default system voice? Upgrade to Fish Audio TTS and get Paimon, Diluc, Cao Cao and other character voices.

### Steps

**1. Register a Fish Audio account**

Sign up at https://fish.audio, grab your API key from the settings page.

**2. Find a voice model_id you like**

- Visit https://fish.audio/text-to-speech/?modality=tts
- Search for a character (e.g. "派蒙", "Diluc", "曹操")
- Open the model page — the last path segment in the URL is the `model_id`
  - Example: `https://fish.audio/m/eacc56f8ab48443fa84421c547d3b60e/` → model_id = `eacc56f8ab48443fa84421c547d3b60e`

**3. Configure the API key**

Edit `~/.claude/voice-notify/.env`:
```bash
FISH_API_KEY=your_fish_audio_key_here
```

**4. Switch to Fish Audio backend**

```bash
python3 ~/.claude/voice-notify/voice_mode.py fish
```

**5. (Optional) Add custom characters**

Edit `~/.claude/voice-notify/voices.json`:
```json
{
  "backend": "fish",
  "fish": {
    "current": "YourCharacter",
    "voices": {
      "YourCharacter": {
        "name": "YourCharacter",
        "model_id": "model_id_from_fish_audio"
      }
    }
  }
}
```

### Two Fish Audio sub-modes

```bash
python3 ~/.claude/voice-notify/voice_mode.py fish api    # Real-time: LLM summary + TTS (needs DEEPSEEK_API_KEY)
python3 ~/.claude/voice-notify/voice_mode.py fish cache  # Cache: random pick from 10 pre-generated clips
```

Cache mode needs a one-time cache generation:
```bash
python3 ~/.claude/voice-notify/generate_cache.py --character 派蒙
```

## Configuration

### Local mode voice and text

Edit the `local` section of `voices.json`:
```json
{
  "local": {
    "voice": "Tingting",
    "completion_text": "任务完成",
    "permission_text": "需要你的确认"
  }
}
```

macOS Chinese voices: `Tingting` (Mandarin female), `Sinji` (Cantonese), `Meijia` (Taiwan).
List all voices: `say -v '?'`.

### Show current mode

```bash
python3 ~/.claude/voice-notify/voice_mode.py
```

### Temporary mute
```bash
touch ~/.claude/voice-notify/.voice_mute     # mute
rm ~/.claude/voice-notify/.voice_mute        # unmute
```

## Requirements

- Python 3.9+
- macOS or Linux
  - macOS: ships with `say` (zero deps)
  - Linux: install `speech-dispatcher` or `espeak`
- curl (only needed for Fish Audio mode)

## FAQ

**Q: Really works with zero API keys?**

Yes. The default `local` backend uses system TTS — built into macOS, one `apt install` away on Linux.

**Q: Is Fish Audio free?**

New Fish Audio accounts get some credits. Heavy use is billed per character.

**Q: Can I use OpenAI instead of DeepSeek for summarization?**

Yes. Set `LLM_API_URL`, `LLM_API_KEY`, `LLM_MODEL` in `.env` — any OpenAI-compatible endpoint works.

**Q: Can local mode use LLM summarization too?**

Yes. If `DEEPSEEK_API_KEY` or `LLM_API_KEY` is set in `.env`, local mode replaces the static text with a one-sentence summary of Claude's last turn, then reads it through the system TTS.

**Q: Why do I have to add the Claude Code hook by hand?**

Auto-patching `settings.json` is risky (easy to corrupt existing config). Pasting a few JSON lines is safer.

## Uninstall

```bash
chmod +x uninstall.sh && ./uninstall.sh
# Then remove hooks from Claude Code
```

## License

MIT
