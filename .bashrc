#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Aliases
alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias chrome='google-chrome-stable --ozone-platform=x11'

PS1='[\u@\h \W]\$ '

# Shell integrations & prompt
fastfetch
eval "$(starship init bash)"

# Cleaned PATH entries (deduplicated)
export PATH="$HOME/.local/bin:$PATH"
export PATH="$PATH:$HOME/.latentcode/bin"
export PATH="$PATH:$HOME/.npm-global/bin"
export PATH="$PATH:$HOME/development/flutter/bin"
export PATH="$PATH:$HOME/Android/Sdk/platform-tools"

# Added by Antigravity CLI installer
export PATH="/home/kathrina/.local/bin:$PATH"

# Local private settings & secrets (not committed to git)
if [ -f "$HOME/.bashrc.local" ]; then
    source "$HOME/.bashrc.local"
fi
