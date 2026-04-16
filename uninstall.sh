#!/bin/bash
# uninstall.sh — Remove voice-notify installation.

set -e

INSTALL_DIR="$HOME/.claude/voice-notify"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "voice-notify uninstaller"
echo "========================"
echo ""

if [ ! -d "$INSTALL_DIR" ]; then
    echo "Not installed ($INSTALL_DIR does not exist)."
    exit 0
fi

echo -e "${YELLOW}This will remove:${NC}"
echo "  $INSTALL_DIR"
echo "  (including cached audio files and .env)"
echo ""
read -p "Continue? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

rm -rf "$INSTALL_DIR"
echo -e "${GREEN}✓${NC} Removed $INSTALL_DIR"
echo ""
echo -e "${YELLOW}Reminder:${NC} Remove the hooks from Claude Code settings:"
echo "  Run 'claude /hooks' to remove them, or edit ~/.claude/settings.json"
echo "  Delete the Stop and Notification hooks pointing to voice_notify.py / voice_permission.py"
echo ""
echo "Done."
