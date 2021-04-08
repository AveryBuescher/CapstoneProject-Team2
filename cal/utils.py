
from datetime import datetime, timedelta, date
from calendar import HTMLCalendar
from .models import Event

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None, userid = None):
		self.year = year
		self.month = month
		self.userid = userid
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		events_per_day = events.filter(start_time__day=day)
		d = ''
		for event in events_per_day:
			d += f'<li> {event.get_html_url} </li>'

		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr
	def formatweek(self, theweek, events):
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, withyear=True):
		events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month, the_user = self.userid)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal


class Tasks:
	def __init__(self, year=None, month=None, day=None, userid=None):
		self.year = year
		self.month = month
		self.day = day
		self.userid = userid
		super(Tasks, self).__init__()

	def formatday(self, day, events):
		events_per_day = events.filter(start_time__year=day.year, start_time__month=day.month,start_time__day=day.day)
		day_str = ''
		for event in events_per_day:
			event_date = str(event.start_time.month)+'/'+str(event.start_time.day)+'/'+str(event.start_time.year)
			day_str += f'<div class="task low"><div class="desc"><div class="title">{event.title}</div><div>{event.description}</div></div><div class="time"><div class="date">{event_date}</div></div></div>'
		return day_str

	# formats a week as a tr
	def formatweek(self):
		events = Event.objects.filter(the_user=self.userid)
		d = str(self.month) + '/' + str(self.day)
		week = f'<h1 style="text-align:center">Week starting at {d}</h1><div class="container page-todo bootstrap snippets bootdeys"><div class="col-sm-7 tasks"><div class="task-list">'
		current_date = date(self.year,self.month,self.day)
		for n in range(7):
			week += self.formatday(current_date+timedelta(days=n), events)
		week += '</div></div></div>'
		return week
