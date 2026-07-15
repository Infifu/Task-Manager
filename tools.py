from datetime import datetime


def format_date(date):
    day = date.day

    if 10 < day % 100 < 20:
        suffix = "th"
    elif day % 10 == 1:
        suffix = "st"
    elif day % 10 == 2:
        suffix = "nd"
    elif day % 10 == 3:
        suffix = "rd"
    else:
        suffix = "th"

    return date.strftime("%d") .lstrip("0") + suffix + date.strftime(" %B %Y")
