#!/bin/bash

TMP="/tmp/polybar-wifi-list"

# Show cached results immediately
~/.config/polybar/scripts/wifi-scan.sh >/dev/null 2>&1

# Refresh in background
(
    timeout 10s nmcli device wifi list \
        ifname wlan0 \
        --rescan yes >/dev/null 2>&1

    ~/.config/polybar/scripts/wifi-scan.sh >/dev/null 2>&1
) &

choice=$(
    awk -F'\t' '
    {
        printf "%s %s  %-30s %3s%%  %s\n",
               $1, $2, $3, $4, $5
    }' "$TMP" |
    rofi \
        -dmenu \
        -i \
        -p "Wi-Fi" \
        -no-custom \
        -theme-str '
            window {
                width: 600px;
                border: 2px;
                border-color: #c44582;
                border-radius: 12px;
                background-color: #090909;
            }

            mainbox {
                background-color: #090909;
                children: [inputbar, listview];
            }

            inputbar {
                background-color: #111011;
                border-radius: 8px;
                padding: 8px;
                margin: 8px;
            }

            prompt {
                text-color: #d45a91;
                padding: 0 8px 0 0;
            }

            entry {
                text-color: #d8d4d7;
            }

            listview {
                lines: 10;
                columns: 1;
                scrollbar: false;
                padding: 4px 8px 8px;
            }

            element {
                padding: 8px;
                border-radius: 7px;
            }

            element normal.normal {
                background-color: transparent;
                text-color: #d8d4d7;
            }

            element selected.normal {
                background-color: #1a1016;
                text-color: #d45a91;
            }
        '
)

[ -z "$choice" ] && exit 0

ssid=$(
    awk -F'\t' -v choice="$choice" '
    {
        display=sprintf("%s %s  %-30s %3s%%  %s",
                        $1, $2, $3, $4, $5)

        if (display == choice) {
            print $3
            exit
        }
    }' "$TMP"
)

[ -z "$ssid" ] && exit 1

# Get security type from scan results
security=$(
    awk -F'\t' -v choice="$choice" '
    {
        display=sprintf("%s %s  %-30s %3s%%  %s",
                        $1, $2, $3, $4, $5)

        if (display == choice) {
            print $5
            exit
        }
    }' "$TMP"
)

connection=$(
    nmcli -g NAME connection show 2>/dev/null |
    while IFS= read -r name; do
        profile_ssid=$(
            nmcli -g 802-11-wireless.ssid connection show "$name" 2>/dev/null
        )

        if [ "$profile_ssid" = "$ssid" ]; then
            printf '%s\n' "$name"
            break
        fi
    done
)

if [ -n "$connection" ]; then
    nmcli connection up "$connection" ifname wlan0
    exit $?
fi

ROFI_CRED_THEME='
    * {
        font: "Noto Sans 11";
    }

    window {
        width: 420px;
        border: 2px;
        border-color: #ff1493;
        border-radius: 12px;
        background-color: #090909;
        padding: 10px;
        children: [mainbox];
    }

    mainbox {
        background-color: #090909;
        children: [inputbar];
        padding: 0;
    }

    listview {
        enabled: false;
        lines: 0;
    }

    inputbar {
        background-color: #121012;
        border: 1px;
        border-color: #c44582;
        border-radius: 8px;
        padding: 10px 12px;
        spacing: 10px;
        children: [prompt, entry];
    }

    prompt {
        text-color: #ff1493;
        background-color: transparent;
        padding: 0;
        margin: 0;
    }

    entry {
        text-color: #d8d4d7;
        background-color: transparent;
        placeholder-color: #918a8f;
        border: none;
        padding: 0;
        margin: 0;
    }
'

# Check if network is enterprise (802.1X/EAP)
if echo "$security" | grep -iE "802\.1X|EAP|WPA2-EAP|WPA3-EAP" >/dev/null; then
    # Enterprise network: prompt for username, password, and optional certificate
    username=$(rofi -dmenu -lines 0 -password -p "  Username" -theme-str "$ROFI_CRED_THEME")
    [ -z "$username" ] && exit 1

    password=$(rofi -dmenu -lines 0 -password -p "  Password" -theme-str "$ROFI_CRED_THEME")
    [ -z "$password" ] && exit 1

    cert_path=$(rofi -dmenu -lines 0 -p "  Certificate (optional)" -theme-str "$ROFI_CRED_THEME")

    # Create connection with 802.1X enterprise settings
    con_name="$ssid-$(date +%s)"

    if [ -n "$cert_path" ] && [ -f "$cert_path" ]; then
        nmcli connection add \
            type wifi \
            con-name "$con_name" \
            ifname wlan0 \
            ssid "$ssid" \
            wifi-sec.key-mgmt wpa-eap \
            wifi-sec.auth-alg open \
            802-1x.eap peap \
            802-1x.phase2-auth mschapv2 \
            802-1x.identity "$username" \
            802-1x.password "$password" \
            802-1x.ca-cert "$cert_path"
    else
        nmcli connection add \
            type wifi \
            con-name "$con_name" \
            ifname wlan0 \
            ssid "$ssid" \
            wifi-sec.key-mgmt wpa-eap \
            wifi-sec.auth-alg open \
            802-1x.eap peap \
            802-1x.phase2-auth mschapv2 \
            802-1x.identity "$username" \
            802-1x.password "$password"
    fi

    nmcli connection up "$con_name" ifname wlan0
else
    # Simple WPA2/WPA network: just prompt for password
    password=$(rofi -dmenu -lines 0 -password -p "  Password" -theme-str "$ROFI_CRED_THEME")
    [ -z "$password" ] && exit 1

    nmcli device wifi connect "$ssid" password "$password" ifname wlan0
fi
