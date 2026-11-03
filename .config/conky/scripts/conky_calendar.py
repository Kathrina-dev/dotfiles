#!/usr/bin/env python3

import calendar
import datetime

today = datetime.date.today()

# Set all color variables to pure white
PINK = "${color #c44582}"
WHITE = "${color #ffffff}"
RESET = "${color}"
CELL_WIDTH = 4

def day_cell(day):
    if day == 0:
        return " " * CELL_WIDTH
    number = f"{day:^{CELL_WIDTH}}"
    if day == today.day:
        return f"{PINK}{number}{RESET}"
    return f"{WHITE}{number}{RESET}"


month = today.strftime("%B %Y").upper()
print(
    f"${{alignc}}"
    f"{WHITE}"
    f"{month}"
    f"{RESET}"
)
print("${voffset 4}")


headers = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
header = "".join(
    f"{day:^{CELL_WIDTH}}"
    for day in headers
)
print(
    f"${{alignc}}"
    f"{WHITE}"
    f"{header}"
    f"{RESET}"
)
print("${voffset 2}")


for week in calendar.monthcalendar(
    today.year,
    today.month,
):
    row = "".join(
        day_cell(day)
        for day in week
    )

    print(
        f"${{alignc}}"
        f"{WHITE}"
        f"{row}"
        f"{RESET}"
    )

    print("${voffset 1}")