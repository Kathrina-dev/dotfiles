#!/bin/bash

IFACE="wlan0"
TMP="/tmp/polybar-wifi-list"

scan_networks() {
    LC_ALL=C nmcli -t -e no \
        -f IN-USE,SSID,SIGNAL,SECURITY \
        device wifi list \
        ifname "$IFACE" \
        "$@" 2>/dev/null |
    awk -F: '
    {
        active=$1
        signal=$(NF-1)
        security=$NF

        ssid=$2
        for (i=3; i<=NF-2; i++)
            ssid=ssid ":" $i

        if (ssid == "")
            next

        if (!(ssid in best) || signal > best[ssid]) {
            best[ssid]=signal
            best_active[ssid]=active
            best_security[ssid]=security
        }
    }

    END {
        for (ssid in best) {
            signal=best[ssid]
            active=best_active[ssid]
            security=best_security[ssid]

            if (signal >= 75)
                icon="󰤨"
            else if (signal >= 50)
                icon="󰤥"
            else if (signal >= 25)
                icon="󰤢"
            else
                icon="󰤟"

            if (active == "*")
                marker="●"
            else
                marker=" "

            if (security == "--")
                security="Open"

            printf "%s\t%s\t%s\t%s\t%s\n",
                   marker, icon, ssid, signal, security
        }
    }' |
    sort -t$'\t' -k3,3
}

# Immediately use NetworkManager's existing scan cache.
scan_networks --rescan no > "$TMP"
