from __future__ import print_function

from datetime import datetime, timedelta, date

from django.db.models import Model
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.utils.safestring import mark_safe
import calendar
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from .models import *
from .utils import Calendar
from .forms import EventForm, CreateUserForm

from cal.gcal_sync.format_datetime import format_datetime
from googleapiclient.discovery import build
import os.path
from os.path import dirname, join
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def index(request):
    return HttpResponse('hello')


class CalendarView(generic.ListView):
    model = Event
    template_name = 'cal/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month, self.request.user.id)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(
        prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(
        next_month.month)
    return month


@login_required(login_url='login')
def event(request, event_id=None):
    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
    else:
        instance = Event()
    instance.the_user = get_object_or_404(User, pk=request.user.id)
    form = EventForm(request.POST or None, instance=instance)

    if request.POST and form.is_valid():
        # if '_edit' in request.POST:
        if '_delete' in request.POST:
            instance.delete()
        else:
            form.save()

        return HttpResponseRedirect(reverse('cal:calendar'))

    return render(request, 'cal/event.html', {'form': form})


def registerPage(request):
    form = CreateUserForm

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,
                             'Account was created for ' + username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'registration/register.html', context)


def settingsPage(request):
    return render(request, 'cal/settings.html')


"""Stuff needed for syncing"""
# Returns a list of events that start on or after start_date and end
# on or before end_date
def filter_events_by_date(start_date, end_date, user_id):
    start_datetime = datetime(start_date.year, start_date.month,
                              start_date.day)
    maxtime = datetime.max
    end_datetime = datetime(end_date.year, end_date.month,
                            end_date.day, maxtime.hour,
                            maxtime.minute, maxtime.second,
                            maxtime.microsecond)
    event_list = Event.objects.filter(start_time__range=(
        start_datetime, end_datetime)).filter(end_time__range=(
        start_datetime, end_datetime)).filter(the_user_id=user_id)

    return event_list


# Adds events that fall within a date-range specified by the user from
# the app to google calendar.
def add_events_to_google(request):
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    event_list = filter_events_by_date(date.fromisoformat(
        request.POST['start_date']),
        date.fromisoformat(request.POST['end_date']), request.user.id)

    print(len(event_list))

    for i in event_list:
        print('AAAAAAAABBBBBBBCCCCCCC')
        print(i.start_time)
        print(i.end_time)
        print(i.description)
        event_body = {
            "kind": "calendar#event",
            "start": {"dateTime": format_datetime(
                i.start_time)},
            "end": {
                "dateTime": format_datetime(i.end_time)},
            "summary": i.title,
            "description": i.description
        }
        # Delete event from google calendar if it has already been
        # added to google calendar (add later)

        # Add event to google calendar
        event = service.events().insert(calendarId='primary',
                                        body=event_body).execute()

        # Record event's google calendar event id (add later)

    return redirect('cal:sync_menu')


def sync_menu(request):
    # add_event_to_google(2)
    print(f'USER ID:{request.user.id}')
    print(f'USER NAME:{request.user.username}')
    return render(request, 'sync/sync_menu.html')


def get_credentials():
    print(dirname(__file__))
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    # cred_filepath = join(dirname(__file__), "credentials.json")
    # token_filepath = join(dirname(__file__), "token.json")
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json",
                                                      SCOPES)
    # If there are no (valid) credentials available, let the user log
    # in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                join(dirname(__file__), "credentials.json"), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run (re-enable later)
        #with open("token.json", 'w') as token:
            #token.write(creds.to_json())
    return creds
