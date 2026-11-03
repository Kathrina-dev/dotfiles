#!/usr/bin/env bash
# restore.sh - Restore configurations from this repo back to ~/.config and ~
# Useful if you make a blunder and want to revert to known good dotfiles.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="$HOME"
BACKUP_DIR="$HOME_DIR/.config-backup-$(date +%Y%m%d-%H%M%S)"

echo "=== Dotfiles Restoration Script ==="
echo "This will restore configs from: $SCRIPT_DIR"
echo "To: $HOME_DIR"
echo ""
read -rp "Create a safety backup of your current ~/.config first? (y/n): " confirm_backup
if [[ "$confirm_backup" =~ ^[Yy]$ ]]; then
    echo "Backing up current configs to $BACKUP_DIR..."
    mkdir -p "$BACKUP_DIR/.config"
    cp -r "$HOME_DIR/.config/i3" "$BACKUP_DIR/.config/" 2>/dev/null || true
    cp -r "$HOME_DIR/.config/polybar" "$BACKUP_DIR/.config/" 2>/dev/null || true
    cp -r "$HOME_DIR/.config/rofi" "$BACKUP_DIR/.config/" 2>/dev/null || true
    cp -r "$HOME_DIR/.config/kitty" "$BACKUP_DIR/.config/" 2>/dev/null || true
    cp -r "$HOME_DIR/.config/picom" "$BACKUP_DIR/.config/" 2>/dev/null || true
    cp "$HOME_DIR/.bashrc" "$BACKUP_DIR/" 2>/dev/null || true
    cp "$HOME_DIR/.zshrc" "$BACKUP_DIR/" 2>/dev/null || true
    echo "Backup created at $BACKUP_DIR"
fi

read -rp "Proceed with restoration? (y/n): " confirm_restore
if [[ ! "$confirm_restore" =~ ^[Yy]$ ]]; then
    echo "Restoration aborted."
    exit 0
fi

echo "Restoring .config items..."
mkdir -p "$HOME_DIR/.config"
cp -r "$SCRIPT_DIR/.config/"* "$HOME_DIR/.config/"

echo "Restoring home dotfiles..."
for file in .bash_profile .zshrc .fehbg .Xresources .gitconfig .gtkrc-2.0 .inputrc .profile .taskrc; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        cp "$SCRIPT_DIR/$file" "$HOME_DIR/$file"
    fi
done

# Note on .bashrc:
if [ -f "$SCRIPT_DIR/.bashrc" ]; then
    read -rp "Restore .bashrc? Note: You'll need to set your ANTHROPIC_API_KEY in ~/.bashrc.local (y/n): " restore_bashrc
    if [[ "$restore_bashrc" =~ ^[Yy]$ ]]; then
        cp "$SCRIPT_DIR/.bashrc" "$HOME_DIR/.bashrc"
    fi
fi

echo "=== Restoration complete! ==="
