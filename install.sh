#!/bin/bash
# install.sh — Install voice-notify for Claude Code.
#
# Creates ~/.claude/voice-notify/, copies scripts, and prints hook config.
# Default mode is local TTS — no API key required.

set -e

INSTALL_DIR="$HOME/.claude/voice-notify"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}voice-notify installer${NC}"
echo "========================"
echo ""

# 1. Check Python version
PYTHON="python3"
if ! command -v "$PYTHON" &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3.9+." >&2
    exit 1
fi

PY_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 9 ]); then
    echo "Error: Python 3.9+ required, found $PY_VERSION" >&2
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $PY_VERSION"

# 2. Check TTS availability (local backend)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v say &> /dev/null; then
        echo -e "${GREEN}✓${NC} TTS: say (macOS)"
    else
        echo -e "${YELLOW}!${NC} say not found (unusual on macOS)"
    fi
elif [[ "$OSTYPE" == "linux"* ]]; then
    if command -v spd-say &> /dev/null; then
        echo -e "${GREEN}✓${NC} TTS: spd-say"
    elif command -v espeak &> /dev/null; then
        echo -e "${GREEN}✓${NC} TTS: espeak"
    else
        echo -e "${YELLOW}!${NC} No Linux TTS found. Install one of:"
        echo "    sudo apt install speech-dispatcher   # recommended (supports Chinese)"
        echo "    sudo apt install espeak"
    fi
fi

# 3. Check audio player (Fish backend, optional)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v afplay &> /dev/null; then
        echo -e "${GREEN}✓${NC} Audio player: afplay"
    fi
elif [[ "$OSTYPE" == "linux"* ]]; then
    PLAYER=""
    for cmd in paplay aplay mpv; do
        if command -v "$cmd" &> /dev/null; then
            PLAYER="$cmd"
            break
        fi
    done
    if [ -n "$PLAYER" ]; then
        echo -e "${GREEN}✓${NC} Audio player: $PLAYER (needed for Fish Audio mode)"
    fi
fi

# 4. Create install directory
mkdir -p "$INSTALL_DIR"
echo -e "${GREEN}✓${NC} Install dir: $INSTALL_DIR"

# 5. Copy Python files and characters.json
for file in config.py audio.py tts_local.py voice_notify.py voice_permission.py generate_cache.py voice_mode.py characters.json; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/$file"
    else
        echo "Warning: $file not found in $SCRIPT_DIR" >&2
    fi
done
echo -e "${GREEN}✓${NC} Scripts copied"

# 6. Set up voices.json
if [ ! -f "$INSTALL_DIR/voices.json" ]; then
    cp "$SCRIPT_DIR/voices.example.json" "$INSTALL_DIR/voices.json"
    echo -e "${GREEN}✓${NC} Default voice config created (backend: local)"
else
    echo -e "${GREEN}✓${NC} voices.json already exists (not overwritten)"
fi

# 7. Set up .env (optional)
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/.env"
    echo -e "${GREEN}✓${NC} .env template created (optional — only for Fish Audio upgrade)"
else
    echo -e "${GREEN}✓${NC} .env already exists (not overwritten)"
fi

# 8. Print hook configuration
echo ""
echo "========================"
echo -e "${CYAN}Almost done! Add these hooks to ~/.claude/settings.json:${NC}"
echo ""
cat <<'EOF'
  "hooks": {
    "Stop": [
      {"hooks": [{"type": "command", "command": "python3 ~/.claude/voice-notify/voice_notify.py"}]}
    ],
    "Notification": [
      {"hooks": [{"type": "command", "command": "python3 ~/.claude/voice-notify/voice_permission.py"}]}
    ]
  }
EOF
echo ""
echo -e "Default mode is ${GREEN}local TTS${NC} — no API key required."
echo "To upgrade to Fish Audio character voices: see README.md"
echo ""
echo -e "${GREEN}Installation complete!${NC}"
