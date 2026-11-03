#!/bin/bash

# Kill all running instances cleanly
killall -q polybar

# Wait until polybar processes are completely gone
while pgrep -u $UID -x polybar >/dev/null; do sleep 0.05; done

# Launch Polybar
polybar main &

# Wait for the Polybar window to map onto screen
xdotool search --sync --onlyvisible --class '^polybar$' >/dev/null 2>&1

# Raise window and set 'above' hint
for window in $(xdotool search --class '^polybar$' 2>/dev/null); do
    xdotool windowraise "$window" 2>/dev/null
    wmctrl -i -r "$window" -b add,above 2>/dev/null
done