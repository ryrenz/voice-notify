# voice-notify

Voice notifications for Claude Code — announces task completion and permission requests. Default mode uses system TTS, **no API key required**.

## Quick start (30 seconds, zero config)

```bash
git clone https://github.com/ryrenz/voice-notify.git
cd voice-notify
./install.sh
```

Then paste this into `~/.claude/settings.json` at the top level (merge with your existing `hooks`, or create a new block):

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

**Done!** Claude Code will now say "task done" on completion and "needs your confirmation" on permission requests, using macOS `say` / Linux `espeak`.

Want more natural character voices (Paimon, Diluc, etc.)? See [Fish Audio upgrade](#upgrade-fish-audio-character-voices) below.

---

## Upgrade: Fish Audio character voices

System TTS sounds robotic? Upgrade to Fish Audio for anime character voices.

### 1. Register a Fish Audio account

Sign up at https://fish.audio.

**Get an API key**: after login → avatar (top right) → API Keys → Create → copy and save.

### 2. Find the character model IDs you want

Go to https://fish.audio/discovery/ and search:

- Search for a character name (e.g. "派蒙" / "Paimon", "Diluc", "曹操" / "Cao Cao")
- Open the model page
- The last path segment of the URL is the `model_id`
  - Example: `https://fish.audio/m/eacc56f8ab48443fa84421c547d3b60e/` → `eacc56f8ab48443fa84421c547d3b60e`
- Preview the voice, and if you like it, copy the `model_id`

### 3. Configure

**Set the API key** — edit `~/.claude/voice-notify/.env`:

```
FISH_API_KEY=the_key_you_copied_from_fish_audio
```

**Add a character** — edit `~/.claude/voice-notify/voices.json`:

```json
{
  "backend": "fish",
  "fish": {
    "current": "Paimon",
    "voices": {
      "Paimon": {
        "name": "Paimon",
        "model_id": "the_model_id_you_copied"
      }
    }
  }
}
```

**Switch to fish backend**:

```bash
python3 ~/.claude/voice-notify/voice_mode.py fish
```

Done. Claude Code will now announce completions in Paimon's voice.

### 4. Two Fish Audio sub-modes

```bash
python3 ~/.claude/voice-notify/voice_mode.py fish api    # Real-time: LLM summarizes what Claude did -> Fish TTS speaks it
python3 ~/.claude/voice-notify/voice_mode.py fish cache  # Cache: pick a random line from 10 pre-generated clips
```

- **api mode** needs an additional DeepSeek or OpenAI API key (set `DEEPSEEK_API_KEY`, or `LLM_API_URL` + `LLM_API_KEY` + `LLM_MODEL` in `.env`).
- **cache mode** takes its lines from `characters.json`. Generate the cache first:

  ```bash
  python3 ~/.claude/voice-notify/generate_cache.py --character 派蒙
  ```

  `characters.json` ships with lines for 13 characters (派蒙 / 迪卢克 / 钟离 / 神子 / 曹操 / 长离 / 姬子 / 蜡笔小新 / 派大星 / 奶龙 / 绿茶 / 丁真 / 黑手). It is a lines library only — it does **not** contain any model IDs. You still need to find each character's model ID on Fish Audio and put it into `voices.json`.

---

## Configuration details

### Local mode: customize voice and text

Edit the `local` section of `~/.claude/voice-notify/voices.json`:

```json
{
  "local": {
    "voice": "Tingting",
    "completion_text": "任务完成",
    "permission_text": "需要你的确认"
  }
}
```

**macOS Chinese voices**: `Tingting` (Mandarin female), `Sinji` (Cantonese), `Meijia` (Taiwan Mandarin).
List all voices: `say -v '?'`.

**Linux**: set `voice` to `zh` (espeak Chinese) or `auto` for the system default.

### Temporary mute

```bash
touch ~/.claude/voice-notify/.voice_mute   # mute
rm ~/.claude/voice-notify/.voice_mute      # unmute
```

### Switch backends

```bash
python3 ~/.claude/voice-notify/voice_mode.py local       # back to local
python3 ~/.claude/voice-notify/voice_mode.py fish        # Fish Audio
python3 ~/.claude/voice-notify/voice_mode.py             # show current
```

> If you switch to `fish` while `voices.json` has no voices or `FISH_API_KEY` isn't set, voice-notify automatically falls back to local TTS so you always hear something.

---

## Requirements

- Python 3.9+
- macOS (ships with `say`) or Linux (install `speech-dispatcher` or `espeak`)
- `curl` (only needed for Fish Audio mode)
- No `pip install` needed — zero third-party Python dependencies

Linux TTS install:

```bash
sudo apt install speech-dispatcher   # recommended, supports Chinese
# or
sudo apt install espeak
```

---

## How it works

```
Claude Code event fires
  |
  +-- Stop (task finished)       --> voice_notify.py
  |                                    +-- backend=local  -> say/espeak speaks static text (or LLM summary)
  |                                    +-- backend=fish   -> LLM summary + Fish TTS, or play cached clip
  |
  +-- Notification (permission)  --> voice_permission.py
                                       +-- backend=local -> say/espeak
                                       +-- backend=fish  -> play cached character prompt
```

---

## Uninstall

```bash
./uninstall.sh
```

Then remove the corresponding hooks from `~/.claude/settings.json`.

---

## FAQ

**Q: Really works with zero API keys?**
Yes. `say` on macOS and `espeak` on Linux are free system utilities.

**Q: Is Fish Audio free?**
New accounts get free credits; heavy use is billed per character. See fish.audio pricing.

**Q: Where are the model IDs for the 13 characters in `characters.json`?**
We don't distribute model IDs in the repo. Look up each character by name at https://fish.audio/discovery/ and paste the ID into `voices.json` yourself.

**Q: Can I use OpenAI instead of DeepSeek?**
Yes. Set `LLM_API_URL` / `LLM_API_KEY` / `LLM_MODEL` in `.env`. Any OpenAI-compatible endpoint works.

**Q: Why do I have to add hooks to `settings.json` manually?**
Automatic JSON edits risk corrupting your existing config. Copy-paste is safer.

**Q: Windows support?**
v1 targets macOS and Linux only. PRs welcome.

---

## License

MIT
