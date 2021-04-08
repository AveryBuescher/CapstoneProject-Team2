from datetime import datetime, timedelta
from .format_datetime import format_datetime
from .get_credentials import get_credentials
from googleapiclient.discovery import build
from ..models import Event


"""Gets a list of events from one of the user's Google Calendars
Args:
gcalendarId: The Google Calendar to get events from. Uses the user's 
primary google calendar if none is specified.
gtimeMin: Exclusive lower bound for an event's end time to filter by.
Defaults to 8 days before today. Accepts a datetime object.
gtimeMax: Exclusive upper bound for an event's start time to 
filter by. Defaults to 32 days after today. Accepts a datetime object.
"""

def get_events(gcalendarId='primary', gtimeMin=(datetime.now() -
            timedelta(days=8)), gtimeMax=(datetime.now()) + timedelta(
    days=32)):
    print(gtimeMin)
    print(gtimeMax)
    credentials = get_credentials()
    service = build('calendar', 'v3', credentials=credentials)

    gcal_events = service.events().list(
        calendarId=gcalendarId, timeMin=format_datetime(gtimeMin),
        timeMax=format_datetime(gtimeMax)).execute()

    return gcal_events
