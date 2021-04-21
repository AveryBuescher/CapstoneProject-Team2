"Syncing done here so that the default database can be used"
import pytest
from cal.views import sync_to_google, update_google_event, \
    add_new_event_to_google, get_credentials
from cal.models import User, Event
from datetime import date, timedelta, time, datetime

def test_update_google_event():
    return


#Tests adding an event to Google Calendar. The event should get
# deleted from google calendar afterwards
def test_add_new_event_to_google():
    creds = get_credentials(5)


    return
