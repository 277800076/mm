def add_months(start_date, months):
    import calendar

    year = start_date.year + (months / 12)
    month = start_date.month + (months % 12)
    day = start_date.day

    if month > 12:
        month = month % 12
        year = year + 1

    days_next = calendar.monthrange(year, month)[1]
    if day > days_next:
        day = days_next

    return start_date.replace(year, month, day)