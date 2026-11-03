#!/usr/bin/env bash

JSON="$HOME/.config/rofi/commands.json"
THEME="$HOME/.config/rofi/neon-pink.rasi"

# Ensure JSON exists with valid structure
if [ ! -f "$JSON" ]; then
    mkdir -p "$(dirname "$JSON")"
    printf '%s\n' '{"commands":[]}' > "$JSON"
fi

# Remember the X11 window BEFORE Rofi takes focus
target_window="$(xdotool getactivewindow 2>/dev/null)"

while true; do

    # Fetch command names
    items="$(jq -r '.commands[] | .name' "$JSON" 2>/dev/null)"

    if [ -z "$items" ]; then
        items="No commands saved yet"
    fi

    # Open primary Rofi menu
    rofi_output="$(
        printf '%s\n' "$items" |
        rofi \
            -dmenu \
            -i \
            -no-custom \
            -format i \
            -p "Commands" \
            -mesg "＋  Add Command    •    Alt+A" \
            -kb-custom-1 "Alt+a" \
            -theme "$THEME"
    )"

    rofi_exit=$?

    # Alt+A -> Add new command
    if [ "$rofi_exit" -eq 10 ]; then

        new_command="$(
            rofi \
                -dmenu \
                -p "New command" \
                -theme "$THEME"
        )"

        [ -z "$new_command" ] && continue

        new_name="$(
            rofi \
                -dmenu \
                -p "Command name" \
                -theme "$THEME"
        )"

        [ -z "$new_name" ] && new_name="$new_command"

        tmp="$(mktemp)"

        if jq \
            --arg name "$new_name" \
            --arg command "$new_command" \
            '.commands += [{"name": $name, "command": $command}]' \
            "$JSON" > "$tmp"
        then
            mv "$tmp" "$JSON"
        else
            rm -f "$tmp"
        fi

        continue
    fi

    # Exit if user pressed Escape
    [ "$rofi_exit" -ne 0 ] && exit 0

    # Get selected item index
    selected_index="$rofi_output"

    selected="$(
        printf '%s\n' "$items" |
        sed -n "$((selected_index + 1))p"
    )"

    [ -z "$selected" ] && exit 0
    [ "$selected" = "No commands saved yet" ] && exit 0

    # Get chosen command from JSON
    chosen_command="$(
        jq -r \
            --arg name "$selected" \
            '.commands[]
             | select(.name == $name)
             | .command' \
            "$JSON" |
        head -n 1
    )"

    [ -z "$chosen_command" ] && exit 0

    # Return window focus
    if [ -n "$target_window" ]; then
        xdotool windowactivate --sync "$target_window" 2>/dev/null
        sleep 0.15
    fi

    # If execution script or interactive command, launch in terminal/background; otherwise type string
    if [[ "$chosen_command" == *"kitty"* ]] || [[ "$chosen_command" == *"~/"* ]] || [[ "$chosen_command" == *"sudo"* ]]; then
        eval "$chosen_command" &
    else
        xdotool type --clearmodifiers --delay 2 -- "$chosen_command"
    fi

    exit 0

done