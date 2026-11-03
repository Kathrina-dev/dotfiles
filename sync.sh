#!/usr/bin/env bash
# sync.sh - Synchronize live desktop and shell configs to this dotfiles repo
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="$HOME"

echo "=== Syncing configurations from $HOME_DIR to $SCRIPT_DIR ==="

CONFIG_DIRS=(
    "i3" "polybar" "rofi" "kitty" "Kitty-Efeckt"
    "picom" "dunst" "fastfetch" "neofetch" "btop"
    "cava" "conky" "micro" "gtk-3.0" "gtk-4.0"
    "nwg-look" "xsettingsd" "autostart" "pomodoro" "todo"
)

CONFIG_FILES=(
    "greenclip.toml" "libinput-gestures.conf" "pavucontrol.ini"
    "QtProject.conf" "user-dirs.dirs" "mimeapps.list"
)

ROOT_DOTFILES=(
    ".bash_profile" ".zshrc" ".fehbg"
    ".Xresources" ".gitconfig" ".gtkrc-2.0" ".inputrc"
    ".profile" ".taskrc"
)

mkdir -p "$SCRIPT_DIR/.config"

# Sync .config directories
for dir in "${CONFIG_DIRS[@]}"; do
    if [ -d "$HOME_DIR/.config/$dir" ]; then
        echo "Updating .config/$dir..."
        mkdir -p "$SCRIPT_DIR/.config/$dir"
        rsync -av --delete \
            --exclude '.git' \
            --exclude 'config.backup' \
            --exclude 'config.save' \
            --exclude 'backups' \
            --exclude 'buffers' \
            --exclude '__pycache__' \
            --exclude '*.pyc' \
            --exclude 'tasks.json' \
            "$HOME_DIR/.config/$dir/" "$SCRIPT_DIR/.config/$dir/" > /dev/null
    fi
done

# Sync .config files
for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$HOME_DIR/.config/$file" ]; then
        echo "Updating .config/$file..."
        cp "$HOME_DIR/.config/$file" "$SCRIPT_DIR/.config/$file"
    fi
done

# Sync root dotfiles
for file in "${ROOT_DOTFILES[@]}"; do
    if [ -f "$HOME_DIR/$file" ]; then
        echo "Updating $file..."
        cp "$HOME_DIR/$file" "$SCRIPT_DIR/$file"
    fi
done

# Sanitize .bashrc
if [ -f "$HOME_DIR/.bashrc" ]; then
    echo "Updating and sanitizing .bashrc..."
    sed -E 's/export ANTHROPIC_API_KEY=.*/# API Keys (Keep actual keys in ~\/.bashrc.local)\n[ -f ~\/.bashrc.local ] \&\& source ~\/.bashrc.local\n# export ANTHROPIC_API_KEY="your_api_key_here"/' \
        "$HOME_DIR/.bashrc" > "$SCRIPT_DIR/.bashrc"
fi

# Sanitize rofi commands.json
if [ -f "$SCRIPT_DIR/.config/rofi/commands.json" ]; then
    echo "Ensuring rofi/commands.json is sanitized..."
    sed -i 's/zimW#Vw+J3QCdW5g/your_password_here/g' "$SCRIPT_DIR/.config/rofi/commands.json"
    sed -i 's/185\.191\.228\.131/your_server_ip_here/g' "$SCRIPT_DIR/.config/rofi/commands.json"
fi

echo "=== Sync complete! Check 'git diff' or 'git status' before committing. ==="
