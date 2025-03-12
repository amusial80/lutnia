import calendar
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, timedelta
from django.contrib import messages
from django.views import generic
from django.urls import reverse
from .models import *
from .utils import Calendar
from calendar import monthrange
from django.views.generic import TemplateView
from django.utils.timezone import make_naive
from . forms import *
from django.utils import timezone

def homepage(request):
    return render(request, 'lutnia_app/index.html')

def youtube(request):
    form = YTVideoForm()
    if request.method == "POST":
        form = YTVideoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Link dodany!')
            return redirect("youtube")
    full_list = YTVideo.objects.all()
    context = {'full_list': full_list, 'form': form,}
    return render(request, 'lutnia_app/youtube.html', context)
    

def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rejestracja zakonczona powodzeniem!')
            return redirect("my_login")
    context = {'registerform': form}
    return render(request, 'lutnia_app/register.html', context=context)

#login
def my_login(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print(user, request)
                return redirect('profile')
    context = {'loginform':form}
    return render(request, 'lutnia_app/my_login.html', context=context)

def user_logout(request):
    auth.logout(request)
    return redirect("")

@login_required(login_url="my_login")
def profile(request):
    return render(request, 'lutnia_app/profile.html')

@login_required(login_url="my_login")
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')  # Redirect to the profile page
        else:
            messages.warning(request, 'Cos poszlo nie tak!!!!!')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'u_form': u_form, 'p_form': p_form}
    return render(request, 'lutnia_app/edit_profile.html', context)

@login_required(login_url="my_login")
def default_table(request):
    return render(request, 'lutnia_app/tabele/default_table.html')

@login_required(login_url="my_login")
def excersises(request):
    return render(request, 'lutnia_app/excersises.html')

@login_required(login_url="my_login")
def stats(request):
    return render(request, 'lutnia_app/stats.html')

class CalendarView(generic.ListView):
    model = Event
    template_name = 'lutnia_app/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month'))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = html_cal
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

def get_date(req_month):
    print(f"Received month parameter: {req_month}")
    if req_month:
        try:
            year, month = (int(x) for x in req_month.split('-'))
            return date(year, month, 1)
        except ValueError:
            return datetime.today().date()  # Fallback if parsing fails
    return datetime.today().date()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    return f'month={prev_month.year}-{prev_month.month}'

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    return f'month={next_month.year}-{next_month.month}'

@login_required(login_url="my_login")
def event(request, event_id=None):
    if event_id:  # Editing an existing event
        instance = get_object_or_404(Event, pk=event_id)

        if instance.user != request.user:
            messages.error(request, "Nie mozesz edytowac tej rezerwacji. Nie jestes jej wlascicielem!")
            return redirect('month_view', month=instance.start_time.strftime("%m"), year=instance.start_time.strftime("%Y"))
    else:  # Creating a new event
        instance = Event()
        instance.user = request.user  # Assign the logged-in user as the event creator

    form = EventForm(request.POST or None, instance=instance)
    
    if request.POST and form.is_valid():
        event = form.save(commit=False)  # Don't save yet to modify datetimes
        
        # Ensure start_time and end_time are timezone-aware
        event.start_time = timezone.make_aware(event.start_time) if timezone.is_naive(event.start_time) else event.start_time
        event.end_time = timezone.make_aware(event.end_time) if timezone.is_naive(event.end_time) else event.end_time
        
        event.save()  # Save after ensuring timezone-awareness
        messages.success(request, "Rezerwacja zatwierdzona!")
        return redirect('month_view', month=request.POST['date_month'], year=request.POST['date_year'])

    # Use timezone-aware `now()` instead of `datetime.today()`
    rok = timezone.now().year
    miesiac = timezone.now().month

    return render(request, 'lutnia_app/event.html', {'form': form, 'today_year': rok, 'today_month': miesiac, 'instance': instance})

@login_required(login_url="my_login")
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    rok = datetime.today().strftime("%Y")
    miesiac = datetime.today().strftime("%m")
    if request.method == "POST":  # Confirm delete
        event.delete()
        messages.warning(request, "Rezerwacja zostala usunieta!")
        return redirect("month_view", year=rok, month=miesiac)

    return render(request, "lutnia_app/event_confirm_delete.html", {"event": event, 'year':rok, 'month':miesiac})


def day_view(request, year, month, day):  
    # Generate 24-hour list with 30-minute intervals
    hours = [(datetime(2023, 1, 1, 0, 0) + timedelta(minutes=30 * i)).strftime('%H:%M') for i in range(48)]

    today = datetime(year, month, day)
    prev_day = (today - timedelta(days=1)).strftime("%d")
    next_day = (today + timedelta(days=1)).strftime("%d")
    year = today.year
    month = today.month

    # Fetch events for the specific day
    events = Event.objects.filter(start_time__date=today).order_by('start_time')
    
    hourly_events = {hour: [] for hour in hours}
    for event in events:
        event_start_hour = make_naive(event.start_time).strftime("%H:%M")
        if event_start_hour in hourly_events:
            hourly_events[event_start_hour].append({
                'event': event,
                'duration': event.end_time - event.start_time,
                'edit_url': reverse('event_edit', args=[event.id])
            })
        else:
            print(f"Event start time {event_start_hour} not found in hourly_events keys!")

    context = {
        'year': year,
        'month': month,
        'godziny': hours,
        'events': events,
        'next_day': next_day,
        'prev_day': prev_day,
        'hourly_events': hourly_events,
        'today': today.strftime("%d %B %Y"),
    }
    
    return render(request, 'lutnia_app/day_view2.html', context)


class DayView(TemplateView):
    template_name = "lutnia_app/day_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get date from URL or use today
        selected_date = datetime(kwargs['year'], kwargs['month'], kwargs['day']).date()
        prev_day = selected_date - timedelta(days=1)
        next_day = selected_date + timedelta(days=1)
        # Generate list of hours (00:00 - 23:00) with naive datetime
        hours = [datetime(selected_date.year, selected_date.month, selected_date.day, h, 0) for h in range(24)]

        # Fetch events for the selected date
        events = Event.objects.filter(start_time__date=selected_date).order_by('start_time')

        # Ensure dictionary keys match event timestamps (naive datetime)
        hourly_events = {hour: [] for hour in hours}
        for event in events:
            event_start_hour = make_naive(event.start_time)
            if event_start_hour in hourly_events:
                hourly_events[event_start_hour].append({
                    'event': event,
                    'duration': event.end_time - event.start_time,
                    'edit_url': reverse('event_edit', args=[event.id])
                })
            else:
                print(f"Event start time {event_start_hour} not found in hourly_events keys!")

        context = {
            'selected_date':selected_date,
            'prev_day':prev_day,
            'next_day':next_day,
            'hourly_events':hourly_events,
        }
        return context

class MonthView(TemplateView):
    template_name = "lutnia_app/month_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_date_str = self.request.GET.get('date', None)
        if selected_date_str:
            selected_date = timezone.make_aware(
                datetime.strptime(selected_date_str, "%Y-%m-%d"),
                timezone.get_current_timezone()
            )
        else:
            selected_date = timezone.localtime(timezone.now())  # Ensure local timezone
        
        context['selected_date'] = selected_date
        context['month_name'] = selected_date.strftime('%B')
        context['year'] = selected_date.year

        # Get the year and month from URL, or use the current month
        year = int(kwargs.get('year', selected_date.year))
        month = int(kwargs.get('month', selected_date.month))

        # Get first and last day of the month
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])

        # Get all events for this month
        events = Event.objects.filter(start_time__date__year=year, start_time__date__month=month)

        # Group events by day
        days_with_events = {day: [] for day in range(1, last_day.day + 1)}
        for event in events:
            event_day = timezone.localtime(event.start_time).day
            days_with_events[event_day].append({
                'user': event.user,
                'place': event.get_place_display(),
                'table': event.get_table_display(),
                'start_time': timezone.localtime(event.start_time).strftime("%H:%M"),
                'end_time': timezone.localtime(event.end_time).strftime("%H:%M"),
                'edit_url': reverse('event_edit', args=[event.id])
            })

        # Generate calendar structure
        cal = calendar.Calendar()
        weeks = cal.monthdayscalendar(year, month)  # List of weeks, each with 7 days

        context.update({
            'year': year,
            'month': month,
            'weeks': weeks,
            'days_with_events': days_with_events,
            'month_name': first_day.strftime("%B"),
            'prev_month': (first_day - timedelta(days=1)).strftime("%Y-%m"),
            'next_month': (last_day + timedelta(days=1)).strftime("%Y-%m"),
            'selected_date': selected_date,
        })

        return context
    
class YearView(TemplateView):
    template_name = "lutnia_app/year_view.html"

    def get_context_data(self, **kwargs):
        year = int(self.kwargs.get("year", date.today().year))
        context = super().get_context_data(**kwargs)

        # Create a dictionary with months and their events
        months = []
        for month in range(1, 13):
            first_day = date(year, month, 1)
            last_day = date(year, month, monthrange(year, month)[1])

            # Get events for this month
            events = Event.objects.filter(start_time__year=year, start_time__month=month)

            # Organizing events by day
            days_with_events = {}
            for event in events:
                event_day = event.start_time.day
                if event_day not in days_with_events:
                    days_with_events[event_day] = []
                days_with_events[event_day].append(event)

            months.append({
                "month_number": month,
                "month_name": first_day.strftime("%B"),  # English month names
                "days_with_events": days_with_events
            })

        context["year"] = year
        context["months"] = months
        context['day'] = first_day
        context['selected_date'] = date(year, month, int(first_day.strftime("%d")))
        return context