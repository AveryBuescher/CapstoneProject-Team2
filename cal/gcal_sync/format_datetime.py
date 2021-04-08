from datetime import date, time, datetime
"""Takes a datetime object and returns a string equivalent that can
be used with Google Calendar"""
def format_datetime(dt):
    # Just to make things easy, utc offset will always be 00:00. It can
    # be changed later.
    return f"{dt.date()}T{dt.time()}+00:00"




