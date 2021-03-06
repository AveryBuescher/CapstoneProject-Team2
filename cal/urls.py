
from django.conf.urls import url
from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views


app_name = 'cal'
urlpatterns = [
    url(r'^$', login_required(views.CalendarView.as_view()), name='home'),
    url(r'^index/$', views.index, name='index'),
    url(r'^calendar/$', login_required(views.CalendarView.as_view()), name='calendar'),
    url(r'^tasks/$', login_required(views.TaskView.as_view()), name='tasks'),
    url(r'^event/new/$', views.event, name='event_new'),
    url(r'^event/edit/(?P<event_id>\d+)/$', views.event, name='event_edit'),

    path('register/', views.registerPage, name='registerPage'),

    path('settings/', views.settingsPage, name='settingsPage'),

    path('sync/', views.sync_menu, name='sync_menu'),

    path('sync/sync_to_google', views.sync_to_google,
         name='sync_to_google')

    #path('base/', views.dummy_action, name='dummy_action')

]

