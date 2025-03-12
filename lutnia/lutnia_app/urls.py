from django.urls import path
from . import views
from django.conf.urls.static import static
from .views import DayView, MonthView, YearView

urlpatterns = [
    path('', views.homepage, name=""),
    #user management
    path('register', views.register, name="register"),
    path('my_login', views.my_login, name="my_login"),
    path('user_logout', views.user_logout, name="user_logout"),
    path('profile', views.profile, name="profile"),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    #tables, excersises and stats
    path('default_table', views.default_table, name="default_table"),
    path('excersises', views.excersises, name="excersises"),
    path('stats', views.stats, name="stats"),
    #youtube vids
    path('youtube', views.youtube, name="youtube"),
    #booking system
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('event/new/', views.event, name='event_new'),
    path("event/<int:event_id>/delete/", views.delete_event, name="delete_event"),
    path('event/edit/<int:event_id>/', views.event, name='event_edit'),
    path('calendar/<int:year>/<int:month>/', MonthView.as_view(), name='month_view'),
    #path('calendar/<int:year>/<int:month>/<int:day>/', DayView.as_view(), name='day_view'),
    path('calendar/<int:year>/<int:month>/<int:day>/', views.day_view, name='day_view'),
    path("calendar/<int:year>/", YearView.as_view(), name="year_view"),
    #path("day_view2", views.day_view, name="day_view2"),
    #path("day_view2/<int:year>/<int:month>/<int:day>/", views.day_view2, name="day_view2"),
]