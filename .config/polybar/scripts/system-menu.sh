#!/bin/bash

choice=$(
    printf '%s\n' \
        "󰌾  Lock" \
        "󰤄  Suspend" \
        "󰍃  Logout" \
        "󰑐  Reload i3" \
        "󰑓  Restart Polybar" \
        "󰜉  Reboot" \
        "󰐥  Shutdown" |
    rofi \
        -dmenu \
        -i \
        -no-custom \
        -theme-str '
            window {
                width: 320px;
                border: 2px;
                border-color: #c44582;
                border-radius: 12px;
                background-color: #000000;
            }

            mainbox {
                background-color: #000000;
                children: [listview];
            }

            listview {
                lines: 7;
                columns: 1;
                scrollbar: false;
                padding: 8px;
                background-color: #000000;
            }

            element {
                padding: 10px;
                border-radius: 7px;
                background-color: #000000;
            }

            element normal.normal {
                background-color: #000000;
                text-color: #d8d4d7;
            }

            element selected.normal {
                background-color: #000000;
                text-color: #c44582;
            }
        '
)

case "$choice" in
    "󰌾  Lock")
        ~/.config/i3/scripts/blur-lock
        ;;

    "󰤄  Suspend")
        systemctl suspend
        ;;

    "󰍃  Logout")
        i3-msg exit
        ;;

    "󰑐  Reload i3")
        i3-msg reload
        ;;

    "󰑓  Restart Polybar")
        ~/.config/polybar/launch.sh
        ;;

    "󰜉  Reboot")
        systemctl reboot
        ;;

    "󰐥  Shutdown")
        systemctl poweroff
        ;;
esac