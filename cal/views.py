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
from .utils import Calendar, Tasks
from .forms import EventForm, CreateUserForm

from cal.gcal_sync.format_datetime import format_datetime
from googleapiclient.discovery import build
import os.path
from os.path import dirname, join
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from cal.models import Token
import json


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
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month



class TaskView(generic.ListView):
    model = Event
    template_name = 'cal/taskview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date_tasks(self.request.GET.get('date', None))
        tasks = Tasks(d.year, d.month, d.day, self.request.user.id)
        html_tasks = tasks.formatweek()
        context['task_list'] = mark_safe(html_tasks)
        context['prev_week'] = prev_week(d)
        context['next_week'] = next_week(d)
        return context

def get_date_tasks(req_day):
    if req_day:
        year, month, day = (int(x) for x in req_day.split('-'))
        return date(year, month, day)
    return datetime.today()


def prev_week(d):
    current = d
    prev_week = current - timedelta(days=7)
    date = 'date=' + str(prev_week.year) + '-' + str(prev_week.month) + '-' + str(prev_week.day)
    return date


def next_week(d):
    current = d
    next_week = current + timedelta(days=7)
    date = 'date=' + str(next_week.year) + '-' + str(next_week.month) + '-' + str(next_week.day)
    return date



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
            messages.success(request,'Account was created for ' + username)
            return redirect('login')

    context = {'form':form}
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

# Adds an event from ProCal to google calendar and records the google
# calendar event's gcal_id
def add_new_event_to_google(service, event):
    _event = service.events().insert(calendarId='primary',
                                     body=event.to_gcal_body).execute()
    event.gcal_id = service.events().get(calendarId='primary',
                                         eventId=_event[
                                             'id']).execute()['id']
    event.save()
    return

def update_google_event(service, event):
    _event = service.events().update(calendarId='primary',
                                     eventId=event.gcal_id)
    return


# Adds events that fall within a date-range specified by the user from
# the app to google calendar and updates existing ones.
def sync_to_google(request):
    creds = get_credentials(request.user.id)
    service = build('calendar', 'v3', credentials=creds)
    event_list = filter_events_by_date(date.fromisoformat(
        request.POST['start_date']),
        date.fromisoformat(request.POST['end_date']), request.user.id)

    print(len(event_list))

    for i in event_list:
        print('AAAAAAAABBBBBBBCCCCCCC')
        print(i.start_time)
        print(type(i.start_time))
        print(i.end_time)
        print(i.description)
        # If this event has already been synced to Google Calendar,
        # the event gets updated. If it hasn't been synced already,
        # it gets synced and its gcal_id gets recorded



        # Add event to google calendar
        add_new_event_to_google(service=service, event=i)


    return redirect('cal:sync_menu')


def sync_menu(request):
    print(f'USER ID:{request.user.id}')
    print(f'USER NAME:{request.user.username}')
    return render(request, 'sync/sync_menu.html')

def get_credentials(user_id):
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    existing_creds = None
    try:
        existing_creds = Token.objects.get(the_user_id=user_id)
    except:
        existing_creds = None

    if existing_creds:
        # Load creds if there are any for this user (add later)
        foo = existing_creds.to_dict
        del foo["the_user"]
        creds = Credentials.from_authorized_user_info(
            foo, SCOPES)

    # Let the user log in if there aren't any valid credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                join(dirname(__file__), "credentials.json"), SCOPES)
            creds = flow.run_local_server(port=0)
            print(type(json.loads(creds.to_json())))

        # Save credentials for next run
        cred_dict = json.loads(creds.to_json())
        # Create new entry in Token table if there isn't one for this
        # user, or just make a new one for this user if there isn't one
        # already. (part of saving creds for next run)
        if not existing_creds:
            new_entry = Token(token=cred_dict['token'],
                              refresh_token=cred_dict['refresh_token'],
                              token_uri=cred_dict['token_uri'],
                              client_id=cred_dict['client_id'],
                              client_secret=cred_dict['client_secret'],
                              scopes=cred_dict['scopes'],
                              expiry=cred_dict['expiry'],
                              the_user_id=user_id)
            new_entry.save()
        else:
            updated_entry = Token.objects.get(the_user_id=user_id)
            updated_entry.token = cred_dict['token']
            updated_entry.refresh_token = cred_dict['refresh_token']
            updated_entry.token_uri = cred_dict['token_uri']
            updated_entry.client_id = cred_dict['client_id']
            updated_entry.client_secret = cred_dict['client_secret']
            updated_entry.scopes = cred_dict['scopes']
            updated_entry.expiry = cred_dict['expiry']
            updated_entry.save()

    return creds
