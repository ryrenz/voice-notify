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

Want more expressive voices (Perky Girl, Mature Female, Alpha Male, etc.)? See [Fish Audio upgrade](#upgrade-fish-audio-character-voices) below.

---

## Upgrade: Fish Audio character voices

System TTS sounds robotic? Upgrade to Fish Audio and pick from **13 built-in voice profiles**: Perky Girl (萝莉音), Mature Female (御姐音), Young Boy (正太音), Alpha Male (霸总音), Sweet Schemer (绿茶音), Streetwise (社会人音), and more.

### 1. Register a Fish Audio account

Sign up at https://fish.audio.

**Get an API key**: after login → avatar (top right) → API Keys → Create → copy and save.

### 2. Find the voice model IDs you want

Go to https://fish.audio/discovery/ and search by voice type:

- Search by keyword, e.g. "萝莉" (perky girl), "御姐" (mature female), "正太" (young boy), "霸总" (alpha male)
- Open the model page
- The last path segment of the URL is the `model_id`
  - Example: `https://fish.audio/m/eacc56f8ab48443fa84421c547d3b60e/` → `eacc56f8ab48443fa84421c547d3b60e`
- Preview the voice, and if you like it, copy the `model_id`

### 3. Configure

**Set the API key** — edit `~/.claude/voice-notify/.env`:

```
FISH_API_KEY=the_key_you_copied_from_fish_audio
```

**Add a voice** — edit `~/.claude/voice-notify/voices.json` (keys must match the voice names in `characters.json`, which are in Chinese):

```json
{
  "backend": "fish",
  "fish": {
    "current": "萝莉音",
    "voices": {
      "萝莉音": {
        "name": "萝莉音",
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

Done. Claude Code will now announce completions in the Perky Girl (萝莉音) voice.

### 4. Two Fish Audio sub-modes

```bash
python3 ~/.claude/voice-notify/voice_mode.py fish api    # Real-time: LLM summarizes what Claude did -> Fish TTS speaks it
python3 ~/.claude/voice-notify/voice_mode.py fish cache  # Cache: pick a random line from 10 pre-generated clips
```

- **api mode** needs an additional DeepSeek or OpenAI API key (set `DEEPSEEK_API_KEY`, or `LLM_API_URL` + `LLM_API_KEY` + `LLM_MODEL` in `.env`).
- **cache mode** takes its lines from `characters.json`. Generate the cache first:

  ```bash
  python3 ~/.claude/voice-notify/generate_cache.py --character 萝莉音
  ```

  `characters.json` ships with 13 voice-type templates, each with 10 representative lines:
  Perky Girl (萝莉音) / Mature Female (御姐音) / Young Boy (正太音) / Alpha Male (霸总音) /
  Cold Male (冷酷男声) / Classical Male (古风男声) / Gentle Sister (温柔姐姐音) /
  Intellectual Sister (知性姐姐音) / Derp (呆萌音) / Cute Baby (萌宝音) /
  Sweet Schemer (绿茶音) / Teen Boy (少年音) / Streetwise (社会人音).
  It is a lines library only — it does **not** contain any model IDs. You still need to pick a matching model on Fish Audio and put its ID into `voices.json`.

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

**Q: Where are the model IDs for the 13 voice profiles in `characters.json`?**
We don't distribute model IDs in the repo. Pick a matching voice at https://fish.audio/discovery/ by searching the voice-type keyword (萝莉/御姐/正太/霸总 etc.) and paste the ID into `voices.json` yourself.

**Q: Can I use OpenAI instead of DeepSeek?**
Yes. Set `LLM_API_URL` / `LLM_API_KEY` / `LLM_MODEL` in `.env`. Any OpenAI-compatible endpoint works.

**Q: Why do I have to add hooks to `settings.json` manually?**
Automatic JSON edits risk corrupting your existing config. Copy-paste is safer.

**Q: Windows support?**
v1 targets macOS and Linux only. PRs welcome.

---

## License

MIT
