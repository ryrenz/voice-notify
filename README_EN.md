# voice-notify

Voice notifications for Claude Code — announces task completion and permission requests.

Two tracks: **5-second zero-dependency version** (what most people want), **Full version** (for character voices or LLM summary).

---

## 🥇 5-second zero-dependency version

No clone, no install — just merge the **hook fragment** below into `~/.claude/settings.json`:

- If your `settings.json` doesn't have a `"hooks"` field yet: add the whole `"hooks": { ... }` block to the top-level object.
- If you already have `"hooks"`: merge the `Stop` and `Notification` entries into it.

**macOS**:
```json
  "hooks": {
    "Stop": [{"hooks": [{"type": "command", "command": "say 'Task complete'"}]}],
    "Notification": [{"hooks": [{"type": "command", "command": "say 'Needs approval'"}]}]
  }
```

**Linux** (install TTS first: `sudo apt install speech-dispatcher`):
```json
  "hooks": {
    "Stop": [{"hooks": [{"type": "command", "command": "spd-say 'Task complete'"}]}],
    "Notification": [{"hooks": [{"type": "command", "command": "spd-say 'Needs approval'"}]}]
  }
```

Done. Claude Code will now announce task completions and permission requests through your system TTS.

**Prefer Chinese?** Replace `'Task complete'` with `'任务完成'` and `'Needs approval'` with `'需要确认'`.

**Want a different voice?** On macOS add `-v`: `say -v Samantha 'Task complete'`. List all voices: `say -v '?'`.

**Want more?** For character voices or LLM summaries of what Claude just did, see the Full version below.

**Want to uninstall?** Just remove the `Stop` and `Notification` hook entries you added to `~/.claude/settings.json`.

---

## 🥈 Full version (character voices / LLM summary)

Want anime-style character voices (Sweet Schemer, Mature Female, Young Boy)? Want Claude Code to **summarize what it just did** in a character voice? Take this path.

### Prerequisite: Python 3.9+

```bash
# macOS
brew install python3
# or download from https://www.python.org/downloads/

# Ubuntu / Debian (usually pre-installed)
sudo apt install python3

# Fedora / RHEL
sudo dnf install python3

# Arch
sudo pacman -S python
```

Verify: `python3 --version` should show 3.9+.

### Install

```bash
git clone https://github.com/ryrenz/voice-notify.git
cd voice-notify
./install.sh
```

Then paste the JSON that `install.sh` prints into `~/.claude/settings.json`.

After installation the default backend is still local TTS (equivalent to the zero-dependency version), but now with configurable options (custom phrases, voice switching, etc.).

### Upgrade to Fish Audio character voices

System TTS sounds too robotic? Upgrade to Fish Audio for real character voices. The repo ships with **line templates** for 3 voice types (Sweet Schemer / Mature Female / Young Boy, used by Cache mode); **you pick the actual voice models from Fish Audio yourself** (see Step 2 below).

#### 1. Register a Fish Audio account

Sign up at https://fish.audio.

**Get an API key**: after login → avatar (top right) → API Keys → Create → copy and save.

#### 2. Find the voice model IDs you want

Go to https://fish.audio/discovery/ and search by voice type:

- Search by keyword, e.g. "绿茶" (sweet schemer), "御姐" (mature female), "正太" (young boy)
- Open the model page
- The last path segment of the URL is the `model_id`
  - Example: `https://fish.audio/m/eacc56f8ab48443fa84421c547d3b60e/` → `eacc56f8ab48443fa84421c547d3b60e`
- Preview the voice, and if you like it, copy the `model_id`

#### 3. Configure

**Set the API key** — edit `~/.claude/voice-notify/.env`:

```
FISH_API_KEY=the_key_you_copied_from_fish_audio
```

**Add a voice** — edit `~/.claude/voice-notify/voices.json` (keys must match the voice names in `characters.json`, which are in Chinese):

```json
{
  "backend": "fish",
  "fish": {
    "current": "绿茶音",
    "voices": {
      "绿茶音": {
        "name": "绿茶音",
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

Done. Claude Code will now announce completions in the Sweet Schemer (绿茶音) voice.

#### 4. Two Fish Audio sub-modes

```bash
python3 ~/.claude/voice-notify/voice_mode.py fish api    # Real-time: LLM summarizes what Claude did -> Fish TTS speaks it
python3 ~/.claude/voice-notify/voice_mode.py fish cache  # Cache: pick a random line from 10 pre-generated clips
```

- **api mode** needs an additional DeepSeek or OpenAI API key (set `DEEPSEEK_API_KEY`, or `LLM_API_URL` + `LLM_API_KEY` + `LLM_MODEL` in `.env`).
- **cache mode** takes its lines from `characters.json`. Generate the cache first:

  ```bash
  python3 ~/.claude/voice-notify/generate_cache.py --character 绿茶音
  ```

  > ⚠️ Generating cache makes 10 Fish Audio API calls per character (one per line) and will consume your API quota.

  `characters.json` ships with 3 voice-type templates, each with 10 representative lines:
  Sweet Schemer (绿茶音) / Mature Female (御姐音) / Young Boy (正太音).
  It is a lines library only — it does **not** contain any model IDs. You still need to pick a matching model on Fish Audio and put its ID into `voices.json`. Want more profiles? Just append your own to `characters.json` following the same format.

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

| Track | Dependencies |
|-------|--------------|
| Zero-dependency version | macOS (ships with `say`) or Linux (`spd-say` / `espeak`) |
| Full version | Above + Python 3.9+ |
| Fish Audio character voices | Full version + `curl` + Fish Audio API key |

Linux TTS install:

```bash
sudo apt install speech-dispatcher   # recommended, supports Chinese
# or
sudo apt install espeak
```

The full version has zero third-party Python dependencies — no `pip install` needed.

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

**Q: Where are the model IDs for the 3 voice profiles in `characters.json`?**
We don't distribute model IDs in the repo. Pick a matching voice at https://fish.audio/discovery/ by searching the voice-type keyword (绿茶/御姐/正太) and paste the ID into `voices.json` yourself.

**Q: Only 3 voice templates?**

Yes. We ship just Sweet Schemer (绿茶音), Mature Female (御姐音), and Young Boy (正太音) as defaults for cache mode. Want more? Append your own entries to `~/.claude/voice-notify/characters.json` using the same format as the existing three.

**Q: Can I use OpenAI instead of DeepSeek?**
Yes. Set `LLM_API_URL` / `LLM_API_KEY` / `LLM_MODEL` in `.env`. Any OpenAI-compatible endpoint works.

**Q: Why do I have to add hooks to `settings.json` manually?**
Automatic JSON edits risk corrupting your existing config. Copy-paste is safer.

**Q: Windows support?**
v1 targets macOS and Linux only. PRs welcome.

---

## License

MIT
