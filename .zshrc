export EDITOR="micro"
export VISUAL="micro"
export SUDO_EDITOR="micro"

# Terminal YT Music Playlist Player with MPRIS & Polybar integration
ytplay() {
    if [ -z "$1" ]; then
        echo "Usage: ytplay <playlist or song name>"
        return 1
    fi

    echo "Searching YouTube for: $1..."
    
    # Searches YouTube for the query, extracts audio, and streams it via mpv
    mpv --no-video \
        --ytdl-format="bestaudio/best" \
        --script-opts=mpris-enable=yes \
        --loop-playlist=inf \
        "ytdl://ytsearchall:$*"
}


# Added by Antigravity CLI installer
export PATH="/home/kathrina/.local/bin:$PATH"
