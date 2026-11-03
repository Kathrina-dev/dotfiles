# Kathrina's Dotfiles

Personal Linux configuration files, ricing setups, and shell dotfiles (i3-wm, Polybar, Rofi, Kitty, Picom, Dunst, Micro, etc.).

---

## Structure

```
dotfiles/
├── .config/
│   ├── autostart/             # Autostart desktop entries
│   ├── btop/                  # Resource monitor config & themes
│   ├── cava/                  # Audio visualizer config & shaders
│   ├── conky/                 # Conky system stats & widgets
│   ├── dunst/                 # Notification daemon config
│   ├── fastfetch/             # System information display
│   ├── gtk-3.0/ & gtk-4.0/    # GTK styling & theme configurations
│   ├── i3/                    # Window manager config, keybindings & scripts
│   ├── kitty/                 # Kitty terminal config
│   ├── Kitty-Efeckt/          # Terminal ASCII art banner
│   ├── micro/                 # Micro editor bindings, theme & settings
│   ├── neofetch/              # Neofetch configuration
│   ├── nwg-look/              # GTK theme switcher config
│   ├── picom/                 # Picom compositor / blur / shadows
│   ├── polybar/               # Polybar status bar config & scripts
│   ├── pomodoro/              # CLI Pomodoro timer
│   ├── rofi/                  # App launcher, power menu, themes & scripts
│   ├── todo/                  # Python todo manager app
│   ├── xsettingsd/            # X11 settings daemon
│   └── *.toml, *.conf, *.ini  # greenclip, libinput-gestures, pavucontrol, QtProject
├── .bashrc                    # Bash shell configuration
├── .bash_profile              # Login shell profile
├── .zshrc                     # Zsh shell configuration
├── .fehbg                     # Wallpaper restore script
├── .Xresources                # X11 resources (cursor size/theme)
├── .gitconfig                 # Git user configuration
├── .gtkrc-2.0                 # GTK2 appearance settings
├── .inputrc                   # Readline input config
├── .profile                   # Environment variables
├── .taskrc                    # Taskwarrior config
├── sync.sh                    # Helper script to sync live changes into this repo
├── restore.sh                 # Helper script to restore configs if a blunder occurs
└── .gitignore                 # Excludes secrets, caches, and machine-specific data
```

---

## Important Security Notes

To ensure private credentials are never leaked on GitHub:
1. **API Keys**: In `.bashrc`, actual API keys are sourced from `~/.bashrc.local` (which is in `.gitignore`):
   ```bash
   [ -f ~/.bashrc.local ] && source ~/.bashrc.local
   ```
2. **Server Passwords & IPs**: Private passwords and server IPs in `.config/rofi/commands.json` have been sanitized with placeholder values (`your_password_here`, `your_server_ip_here`).
3. **Heavy App Caches**: Large browser profiles (`google-chrome`, `zen`, `BraveSoftware`), IDE state (`Antigravity`, `Code - OSS`), and credential stores (`gh`, `docker-secrets-engine`) remain in `~/.config` and are **not** committed.

---

## How to Use

### 1. Commit and Push to GitHub
```bash
cd ~/projects/dotfiles
git add .
git commit -m "feat: add rice, window manager, and shell dotfiles"
git push origin main
```

### 2. Updating Your Dotfiles
Whenever you change your window manager, terminal, or polybar settings and want to update this repo:
```bash
cd ~/projects/dotfiles
./sync.sh
git diff
git commit -am "chore: update dotfiles"
git push origin main
```

### 3. Restoring After a Blunder
If you break a config while tinkering and want to revert to the saved version:
```bash
cd ~/projects/dotfiles
./restore.sh
```
The script will prompt to create a safety timestamped backup before restoring.
