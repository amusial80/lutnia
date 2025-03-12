# cal/utils.py

import locale
from calendar import HTMLCalendar
from .models import Event
from django.urls import reverse

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = int(year)
		self.month = int(month)
		super(Calendar, self).__init__()
		locale.setlocale(locale.LC_TIME, "pl_PL.UTF-8")

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		events_per_day = events.filter(start_time__day=day)
		d = ''
		for event in events_per_day:
			d += f'<li class="list-group-item"> {event.get_html_url} </li>'

    
		if day != 0:
			day_url = reverse('day_view', args=[self.year, self.month, day])
			return f"<td><a class='btn btn-success btn-sm' href='{day_url}'><span class='date'>{day}</span></a><ul class='list-group'> {d} </ul></td>"
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
		events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal