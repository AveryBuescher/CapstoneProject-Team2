from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from .get_credentials import get_credentials
from .format_datetime import format_datetime
from ..models import Event


"""Adds an event to Google Calendar. Takes the ID of the event to add
and the ID of the Google Calendar to add it to. gcalendarid defaults 
to the user's primary calendar"""
def add_event_to_google(event_id, gcalendar_id="primary"):
    calendar_event = Event.objects.get(id=event_id)

    creds = get_credentials()
    print(creds)
    service = build('calendar', 'v3', credentials=creds)

    event_body = {
        "kind": "calendar#event",
        "start": {"dateTime": format_datetime(
            calendar_event.start_time)},
        "end": {"dateTime": format_datetime(calendar_event.end_time)},
        "summary": calendar_event.description
    }

    event = service.events().insert(calendarId=gcalendar_id,
                                    body=event_body).execute()

    return event
