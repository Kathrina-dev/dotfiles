#!/bin/bash

IFACE="wlan0"

ssid=$(nmcli -g GENERAL.CONNECTION device show "$IFACE" 2>/dev/null)

if [ -z "$ssid" ] || [ "$ssid" = "--" ]; then
    printf '%%{F#ff1493}󰤮%%{F-} offline\n'
    exit 0
fi

signal=$(
    nmcli -g IN-USE,SIGNAL device wifi list \
        ifname "$IFACE" \
        --rescan no 2>/dev/null |
    awk -F: '$1=="*" {print $2; exit}'
)

[ -z "$signal" ] && signal=0

if [ "$signal" -ge 75 ]; then
    icon="󰤨"
elif [ "$signal" -ge 50 ]; then
    icon="󰤥"
elif [ "$signal" -ge 25 ]; then
    icon="󰤢"
else
    icon="󰤟"
fi

printf '%%{F#ff1493}%s%%{F-} %s\n' "$icon" "$ssid"