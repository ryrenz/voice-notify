#!/bin/bash
# install.sh — Install voice-notify for Claude Code.
#
# Creates ~/.claude/voice-notify/, copies scripts, and prints hook config.
# Does NOT modify Claude Code settings — you add hooks manually.

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

# 2. Check audio player
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v afplay &> /dev/null; then
        echo -e "${GREEN}✓${NC} Audio: afplay (macOS)"
    else
        echo "Warning: afplay not found" >&2
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
        echo -e "${GREEN}✓${NC} Audio: $PLAYER (Linux)"
    else
        echo "Warning: no audio player found. Install pulseaudio, alsa-utils, or mpv." >&2
    fi
fi

# 3. Create install directory
mkdir -p "$INSTALL_DIR"
echo -e "${GREEN}✓${NC} Install dir: $INSTALL_DIR"

# 4. Copy Python files and characters.json
for file in config.py audio.py voice_notify.py voice_permission.py generate_cache.py voice_mode.py characters.json; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/$file"
    else
        echo "Warning: $file not found in $SCRIPT_DIR" >&2
    fi
done
echo -e "${GREEN}✓${NC} Scripts copied"

# 5. Set up .env
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/.env"
    echo -e "${YELLOW}!${NC} Created $INSTALL_DIR/.env — please edit it to add your API keys"
    echo ""
    echo "  Required keys:"
    echo "    FISH_API_KEY    — Get from https://fish.audio"
    echo "    DEEPSEEK_API_KEY — Get from https://platform.deepseek.com (API mode only)"
    echo ""
else
    echo -e "${GREEN}✓${NC} .env already exists (not overwritten)"
fi

# 6. Set up voices.json
if [ ! -f "$INSTALL_DIR/voices.json" ]; then
    cp "$SCRIPT_DIR/voices.example.json" "$INSTALL_DIR/voices.json"
    echo -e "${GREEN}✓${NC} Default voice config created (派蒙, 迪卢克, 曹操)"
else
    echo -e "${GREEN}✓${NC} voices.json already exists (not overwritten)"
fi

# 7. Print hook configuration
echo ""
echo "========================"
echo -e "${CYAN}Almost done! Add these hooks to Claude Code:${NC}"
echo ""
echo "  Stop hook (task completion voice):"
echo -e "    ${GREEN}python3 $INSTALL_DIR/voice_notify.py${NC}"
echo ""
echo "  Notification hook (permission request voice):"
echo -e "    ${GREEN}python3 $INSTALL_DIR/voice_permission.py${NC}"
echo ""
echo "  Run 'claude /hooks' to add them, or edit ~/.claude/settings.json"
echo ""

# 8. Optional: generate cache
echo -e "Generate voice cache now? This pre-generates audio clips for offline use."
echo -e "Requires FISH_API_KEY in .env. Each character takes ~15 seconds."
read -p "Generate cache? [y/N] " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $PYTHON "$INSTALL_DIR/generate_cache.py"
else
    echo "Skipped. Run later with: python3 $INSTALL_DIR/generate_cache.py"
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
