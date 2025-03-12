from random import choices
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Event, YTVideo
from django import forms
from django.forms.widgets import PasswordInput, TextInput, SelectDateWidget
from .models import Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import make_aware, get_current_timezone
from django.core.exceptions import ValidationError
#Create / reg user

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    #email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name','username', 'email']
        labels = {'first_name': '', 'last_name': '','username': '', 'email':''}

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None

class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image', 'user_code', 'phone_number']
        labels = {'image':'', 'user_code':'KOD', 'phone_number':'Numer tel'}
    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", "Zapisz", css_class="btn btn-primary"))
        

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())

class DateInput(forms.DateTimeInput):
    input_type = 'datetime-local'

class LabeledSelectDateWidget(SelectDateWidget):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        lines = html.splitlines()

        # Ensure there are enough lines before accessing them
        if len(lines) < 3:
            return html  # Return unmodified if the structure isn't as expected

        return f"""
        <label for="{name}_day">Day:</label> {lines[0]}<br>
        <label for="{name}_month">Month:</label> {lines[1]}<br>
        <label for="{name}_year">Year:</label> {lines[2]}
        """

class EventForm(forms.ModelForm):
    # Generate time slots with 30-minute intervals (00:00, 00:30, ..., 23:30)
    HOURS = [(f"{hour:02d}:{minute:02d}", f"{hour:02d}:{minute:02d}") 
             for hour in range(24) for minute in (0, 30)]

    date = forms.DateField(widget=forms.SelectDateWidget(), label="Data rejestracji")
    start_time_hour = forms.ChoiceField(choices=HOURS, widget=forms.Select(), label="Czas rozpoczecia")
    end_time_hour = forms.ChoiceField(choices=HOURS, widget=forms.Select(), label="Czas zakonczenia")

    class Meta:
        model = Event
        fields = ['place', 'table', 'bookingtype', 'date', 'start_time_hour', 'end_time_hour','confirmed']
        labels = {'place': '', 'table': '', 'bookingtype': ''}

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['date'].initial = timezone.localdate()  # Use timezone-aware date
        self.fields['place'].widget.attrs.update({'class': 'form-control'})
        self.fields['table'].widget.attrs.update({'class': 'form-control'})
        self.fields['bookingtype'].widget.attrs.update({'class': 'form-control'})
        self.fields['date'].widget.attrs.update({'class': 'list-group list-group-item d-inline'})
        self.fields['start_time_hour'].widget.attrs.update({'class': 'form-control'})
        self.fields['end_time_hour'].widget.attrs.update({'class': 'form-control'})
        
        if self.fields['place'] == "Laska":
            self.fields['table'].choices=Event.TABLE_CHOICES_LUTNIA
            #self.fields['table'].initial(choices=Event.TABLE_CHOICES_LUTNIA)


        # Pre-fill the form fields if an existing instance is being edited
        if self.instance.pk:  # If editing an event
            self.fields['date'].initial = self.instance.start_time.date()
            self.fields['start_time_hour'].initial = timezone.localtime(self.instance.start_time).strftime("%H:%M")
            self.fields['end_time_hour'].initial = timezone.localtime(self.instance.end_time).strftime("%H:%M")

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_hour = cleaned_data.get('start_time_hour')
        end_hour = cleaned_data.get('end_time_hour')
        place = cleaned_data.get('place')
        table = cleaned_data.get('table')

        if date and start_hour and end_hour:
            # Convert to timezone-aware datetime objects
            start_time = make_aware(datetime.strptime(f"{date} {start_hour}", "%Y-%m-%d %H:%M"), get_current_timezone())
            end_time = make_aware(datetime.strptime(f"{date} {end_hour}", "%Y-%m-%d %H:%M"), get_current_timezone())

            if start_time >= end_time:
                raise ValidationError("Czas zakończenia musi być później niż czas rozpoczęcia.")

            # Check for overlapping bookings
            overlapping_events = Event.objects.filter(
                place=place,
                table=table,
                start_time__lt=end_time,  # Existing event starts before the new one ends
                end_time__gt=start_time    # Existing event ends after the new one starts
            )

            # Exclude the current event if editing
            if self.instance.pk:
                overlapping_events = overlapping_events.exclude(pk=self.instance.pk)

            if overlapping_events.exists():
                raise ValidationError("Istnieje już rezerwacja na ten stolik w wybranym przedziale czasowym.")

            cleaned_data['start_time'] = start_time
            cleaned_data['end_time'] = end_time

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        date = self.cleaned_data.get('date')
        start_hour = self.cleaned_data.get('start_time_hour')
        end_hour = self.cleaned_data.get('end_time_hour')

        if date and start_hour and end_hour:
            # Make the datetime aware in the current timezone
            instance.start_time = make_aware(datetime.strptime(f"{date} {start_hour}", "%Y-%m-%d %H:%M"), get_current_timezone())
            instance.end_time = make_aware(datetime.strptime(f"{date} {end_hour}", "%Y-%m-%d %H:%M"), get_current_timezone())

        if commit:
            instance.save()
        return instance

class YTVideoForm(forms.ModelForm):
    
    class Meta:
        model = YTVideo
        link = forms.URLField()
        fields = ['link',]