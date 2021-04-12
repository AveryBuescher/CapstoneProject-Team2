
from django.conf.urls import url
from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views


app_name = 'cal'
urlpatterns = [
    url(r'^$', login_required(views.CalendarView.as_view()), name='home'),
    url(r'^index/$', views.index, name='index'),
    url(r'^calendar/$', login_required(views.CalendarView.as_view()), name='calendar'),
    url(r'^event/new/$', views.event, name='event_new'),
    url(r'^event/edit/(?P<event_id>\d+)/$', views.event, name='event_edit'),

    path('register/', views.registerPage, name='registerPage'),

    path('settings/', views.settingsPage, name='settingsPage'),

    path('sync/', views.sync)






]

