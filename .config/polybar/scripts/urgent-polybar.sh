#!/bin/bash

# Prevent duplicate listener instances on i3 reload
killall -q -9 -w urgent-polybar.sh 2>/dev/null

# Wait for i3 IPC socket to fully initialize
sleep 1

export PATH="/usr/bin:/bin:/usr/local/bin:$PATH"

while read -r event; do
    if echo "$event" | grep -q '"change":"urgent"' &&
       echo "$event" | grep -q '"urgent":true'; then

        if ! pgrep -x polybar >/dev/null; then
            ~/.config/polybar/launch.sh >/dev/null 2>&1 &
        fi
    fi
done < <(
    i3-msg -t subscribe -m '[ "window" ]' 2>/dev/null
)