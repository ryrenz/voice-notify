<!-- For Claude Code / other coding agents helping a user install this repo.
     This is NOT project-level agent rules — it's a script for an agent
     installing voice-notify on a user's machine. -->

# voice-notify — Agent Install Guide

When the user asks an agent (Claude Code, Codex, etc.) to "set up voice-notify
from this GitHub link", follow this guide. It assumes the user wants the
**Fish Audio + LLM summary** path (the "api" sub-mode). For the zero-dep `say`
path or local TTS path, point them to README.md instead — those don't need an
agent.

## Inputs to ask the user for

Before doing anything, confirm you have all of these. If any are missing, ask:

1. `FISH_API_KEY` — from https://fish.audio account page
2. `DEEPSEEK_API_KEY` (or an OpenAI-compatible `LLM_API_URL` + `LLM_API_KEY` + `LLM_MODEL`) — for the per-turn summary
3. One or more Fish Audio voices, each as a pair `(角色名, model_id)`. Example: `("派蒙", "eacc56f8ab48443fa84421c547d3b60e")`. Get `model_id` from the URL of any voice page on https://fish.audio/discovery/.
4. Which voice should be the **default** (the `current` field)

## Install steps (in order)

### 1. Clone and run install.sh

```bash
git clone https://github.com/ryrenz/voice-notify.git
cd voice-notify
./install.sh
```

`install.sh` copies scripts to `~/.claude/voice-notify/`, creates a default
`voices.json` (backend=local) and a `.env` template. It does **not** edit
`settings.json` — that's step 2.

### 2. Merge the Stop / Notification hooks into `~/.claude/settings.json`

`install.sh` prints the hook JSON. **Merge, don't overwrite.** If the user
already has a `hooks.Stop` or `hooks.Notification` array, append to it; do not
replace existing entries.

Use the **absolute path** to `python3` in the hook command, not bare `python3`.
Hooks run in a minimal shell environment and `python3` may not be on PATH. Resolve it:

```bash
command -v python3   # e.g. /opt/homebrew/bin/python3
```

Resulting hook entry should look like:

```json
{"type": "command", "command": "/opt/homebrew/bin/python3 ~/.claude/voice-notify/voice_notify.py"}
```

### 3. Fill in `~/.claude/voice-notify/.env`

Uncomment and set the keys the user provided:

```
FISH_API_KEY=...
DEEPSEEK_API_KEY=...
```

### 4. Edit `~/.claude/voice-notify/voices.json`

Switch backend to `fish`, register each voice, and set `current`:

```json
{
  "backend": "fish",
  "fish": {
    "current": "派蒙",
    "notify_mode": "api",
    "voices": {
      "派蒙": { "name": "派蒙", "model_id": "eacc56f8ab48443fa84421c547d3b60e" }
    }
  }
}
```

**Character-name constraint:** if the user wants `notify_mode: "cache"` later,
the key under `voices` must match a built-in template name in
`characters.json` — currently `御姐音`, `正太音`, `绿茶音`. For `notify_mode: "api"`
(the recommended path) any name works.

### 5. Verify with `voice_mode.py`

```bash
python3 ~/.claude/voice-notify/voice_mode.py
```

Should print `backend: fish`, the chosen `current`, and `notify_mode: api`. If
it falls back to `local`, `voices.json` or `.env` is wrong — re-check.

### 6. Test end-to-end

Tell the user: "say something simple to me so the Stop hook fires." After your
reply ends, they should hear the configured voice say a one-sentence summary.

If they hear nothing:
- `tail -n 50 ~/.claude/logs/*.log` for hook errors (path may vary)
- Run the hook manually to surface errors:
  `echo '{}' | /opt/homebrew/bin/python3 ~/.claude/voice-notify/voice_notify.py`
- Confirm `afplay` (macOS) or `paplay`/`aplay`/`mpv` (Linux) is installed

## Things NOT to do

- Don't write keys into `voices.json` — keys belong in `.env`.
- Don't hardcode keys into the hook command in `settings.json`.
- Don't replace an existing `hooks.Stop` array — append.
- Don't run `generate_cache.py` unless the user explicitly asks for cache mode.
  It calls Fish Audio 10×/character and consumes their quota.
