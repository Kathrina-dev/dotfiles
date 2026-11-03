#!/usr/bin/env python3

from asyncio import base_futures
import argparse
import atexit
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time

# 7-Line Tall ASCII Font
DIGITS = {
    '0': [" ██████ ", "██    ██", "██    ██", "██    ██", "██    ██", "██    ██", " ██████ "],
    '1': ["   ██   ", " ████   ", "   ██   ", "   ██   ", "   ██   ", "   ██   ", " ██████ "],
    '2': [" ██████ ", "██    ██", "      ██", " ██████ ", "██      ", "██      ", "████████"],
    '3': [" ██████ ", "██    ██", "      ██", " ██████ ", "      ██", "██    ██", " ██████ "],
    '4': ["██    ██", "██    ██", "██    ██", "████████", "      ██", "      ██", "      ██"],
    '5': ["████████", "██      ", "███████ ", "      ██", "      ██", "██    ██", " ██████ "],
    '6': [" ██████ ", "██      ", "███████ ", "██    ██", "██    ██", "██    ██", " ██████ "],
    '7': ["████████", "      ██", "     ██ ", "    ██  ", "   ██   ", "  ██    ", " ██     "],
    '8': [" ██████ ", "██    ██", "██    ██", " ██████ ", "██    ██", "██    ██", " ██████ "],
    '9': [" ██████ ", "██    ██", "██    ██", " ███████", "      ██", "██    ██", " ██████ "],
    ':': ["        ", "   ██   ", "   ██   ", "        ", "   ██   ", "   ██   ", "        "],
}

# ANSI Colors
COLOR_FOCUS = "\033[1;35m"
COLOR_BREAK = "\033[1;32m"
COLOR_CYAN  = "\033[1;36m"
COLOR_MUTED = "\033[0;37m"
COLOR_RESET = "\033[0m"

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def strip_ansi(text: str) -> str:
    """Strip ANSI escape sequences to compute true visible line width."""
    return ANSI_ESCAPE.sub('', text)


def render_big_time(time_str: str, color_code: str) -> list[str]:
    """Renders MM:SS string into 7 lines of colored ASCII blocks."""
    lines = [""] * 7
    for char in time_str:
        glyph = DIGITS.get(char, ["        "] * 7)
        for i in range(7):
            lines[i] += glyph[i] + "  "

    return [color_code + line + COLOR_RESET for line in lines]


def center_line(line: str, term_cols: int) -> str:
    """Pad line with spaces to center it horizontally."""
    vis_length = len(strip_ansi(line))
    pad_left = max(0, (term_cols - vis_length) // 2)
    return " " * pad_left + line


def play_sound():
    """Play a short system alert sound."""
    sound_commands = [
        ["canberra-gtk-play", "-i", "complete"],
        ["canberra-gtk-play", "-i", "bell"],
        ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
        ["paplay", "/usr/share/sounds/freedesktop/stereo/bell.oga"],
        ["aplay", "-q", "/usr/share/sounds/alsa/Front_Center.wav"],
    ]

    for cmd in sound_commands:
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if res.returncode == 0:
                return
        except FileNotFoundError:
            continue

    sys.stdout.write("\a")
    sys.stdout.flush()


def notify(title, message, urgency="normal", icon="alarm"):
    """Send a system notification using notify-send."""
    subprocess.run(
        ["notify-send", "-u", urgency, "-i", icon, title, message],
        check=False,
    )


def set_dnd(enabled: bool):
    """Enable or disable Dunst Do-Not-Disturb mode."""
    state = "true" if enabled else "false"
    subprocess.run(["dunstctl", "set-paused", state], check=False)


def cleanup():
    """Ensure DND is disabled and terminal cursor is restored on exit."""
    set_dnd(False)
    sys.stdout.write("\033[?25h\033[0m\n")  # Show cursor & reset text
    sys.stdout.flush()


atexit.register(cleanup)


def signal_handler(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def prompt_for_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """Renders a centered input box and prompt for timer configuration."""
    term_cols, term_rows = shutil.get_terminal_size()

    setup_lines = [
        f"{COLOR_FOCUS}━━━ POMODORO SESSION SETUP ━━━{COLOR_RESET}",
        "",
        f"Enter configuration flags or press {COLOR_FOCUS}[ENTER]{COLOR_RESET} for default (25m work / 5m break):",
        "",
        f"{COLOR_MUTED}Examples:{COLOR_RESET}",
        f"  {COLOR_CYAN}pomo -w 45 -b 10 -l 20{COLOR_RESET}",
        f"  {COLOR_CYAN}pomo -w 50 --once{COLOR_RESET}",
        "",
    ]

    total_height = len(setup_lines) + 2
    top_padding = max(0, (term_rows - total_height) // 2)

    frame = ["\033[H\033[J"]  # Clear terminal
    frame.extend([""] * top_padding)

    for line in setup_lines:
        frame.append(center_line(line, term_cols))

    sys.stdout.write("\n".join(frame) + "\n")

    # Draw centered input prompt arrow
    pad_left = max(0, (term_cols - 50) // 2)
    prompt_str = " " * pad_left + f"{COLOR_FOCUS}❯ {COLOR_RESET}"
    sys.stdout.write(prompt_str)
    sys.stdout.flush()

    sys.stdout.write("\033[?25h")  # Ensure cursor is visible for typing

    try:
        user_input = input().strip()
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)

    if not user_input:
        return parser.parse_args([])

    # Tokenize input and strip leading 'pomo' command if typed by user
    tokens = shlex.split(user_input)
    if tokens and tokens[0] in ("pomo", "pomo.py", "./pomo.py"):
        tokens = tokens[1:]

    try:
        return parser.parse_args(tokens)
    except SystemExit:
        time.sleep(2)
        sys.exit(0)


def run_timer(duration_minutes: float, label: str, is_focus: bool = False):
    total_seconds = int(duration_minutes * 60)
    color = COLOR_FOCUS if is_focus else COLOR_BREAK

    if is_focus:
        set_dnd(True)
        notify(
            "Focus Session Started",
            f"Locked in for {int(duration_minutes)} minutes.",
        )
    else:
        set_dnd(False)
        notify(
            "Break Started",
            f"Relax for {int(duration_minutes)} minutes.",
        )

    start_time = time.time()
    sys.stdout.write("\033[?25l")  # Hide cursor

    for elapsed in range(total_seconds + 1):
        remaining = total_seconds - elapsed
        mins = remaining // 60
        secs = remaining % 60
        time_str = f"{mins:02d}:{secs:02d}"

        progress = elapsed / total_seconds if total_seconds > 0 else 1.0
        bar_len = 32
        filled = int(bar_len * progress)
        bar = "█" * filled + "░" * (bar_len - filled)

        term_cols, term_rows = shutil.get_terminal_size()

        clock_lines = render_big_time(time_str, color)
        content_lines = (
            [
                f"{color}━━━ {label} ━━━{COLOR_RESET}",
                "",
            ]
            + clock_lines
            + [
                "",
                f"{color}[{bar}]{COLOR_RESET}  {int(progress * 100)}%",
                "",
                f"{COLOR_MUTED}Press Ctrl+C to quit{COLOR_RESET}",
            ]
        )

        total_content_height = len(content_lines)
        top_padding = max(0, (term_rows - total_content_height) // 2)

        frame = ["\033[H\033[J"]
        frame.extend([""] * top_padding)

        for line in content_lines:
            frame.append(center_line(line, term_cols))

        sys.stdout.write("\n".join(frame) + "\n")
        sys.stdout.flush()

        if elapsed < total_seconds:
            next_tick = start_time + elapsed + 1
            sleep_time = max(0, next_tick - time.time())
            time.sleep(sleep_time)

    play_sound()

    if is_focus:
        set_dnd(False)
        notify(
            "Pomodoro Complete!",
            "Great job! Time to take a break.",
            urgency="critical",
            icon="trophy",
        )
    else:
        notify(
            "Break Ended!",
            "Time to get back into focus mode.",
            urgency="critical",
            icon="alarm",
        )


def main():
    parser = argparse.ArgumentParser(description="Centered Big ASCII Pomodoro Timer")
    parser.add_argument(
        "-w",
        "--work",
        type=float,
        default=25,
        help="Work duration in minutes (default: 25)",
    )
    parser.add_argument(
        "-b",
        "--break-time",
        type=float,
        default=5,
        help="Short break in minutes (default: 5)",
    )
    parser.add_argument(
        "-l",
        "--long-break",
        type=float,
        default=15,
        help="Long break in minutes (default: 15)",
    )
    parser.add_argument(
        "-r",
        "--rounds",
        type=int,
        default=4,
        help="Rounds before long break (default: 4)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single focus session and exit",
    )

    # Prompt user interactively if no arguments were passed in terminal
    if len(sys.argv) == 1:
        args = prompt_for_args(parser)
    else:
        args = parser.parse_args()

    if args.once:
        run_timer(args.work, "FOCUS SESSION", is_focus=True)
        return

    round_count = 1
    while True:
        run_timer(args.work, f"FOCUS #ROUND {round_count}", is_focus=True)

        if round_count % args.rounds == 0:
            run_timer(args.long_break, "LONG BREAK", is_focus=False)
        else:
            run_timer(args.break_time, "SHORT BREAK", is_focus=False)

        round_count += 1


if __name__ == "__main__":
    main()