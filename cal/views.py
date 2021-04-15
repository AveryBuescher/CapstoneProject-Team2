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
            messages.success(request, 'Account was created for ' + username)
            return redirect('login')

    context = {'form':form}
    return render(request, 'registration/register.html', context)

def settingsPage(request):

    return render(request, 'cal/settings.html')


