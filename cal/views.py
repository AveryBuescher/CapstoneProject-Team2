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

from datetime import datetime, timedelta
from cal.gcal_sync.format_datetime import format_datetime
from cal.gcal_sync.get_credentials import get_credentials
from googleapiclient.discovery import build


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
            messages.success(request, 'Account was created for ' + username)
            return redirect('login')

    context = {'form':form}
    return render(request, 'registration/register.html', context)

def settingsPage(request):

    return render(request, 'cal/settings.html')


"""Stuff needed for syncing"""
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


def sync_menu(request):
    #add_event_to_google(2)
    return render(request, 'sync/sync_menu.html')


