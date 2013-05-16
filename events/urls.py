from django.conf.urls.defaults import *
from django.views.generic import ListView
from events.models import Calendar
from events.feeds import UpcomingEventsFeed
from events.feeds import CalendarICalendar
from events.periods import Year, Month, Week, Day


urlpatterns = patterns('',

# urls for Calendars
url(r'^calendar/$',
    ListView.as_view(queryset=Calendar.objects.all(), template_name='events/calendar_list.html'),
    name="events"),

url(r'^calendar/year/(?P<calendar_slug>[-\w]+)/$',
    'events.views.calendar_by_periods',
    name="year_calendar",
    kwargs={'periods': [Year], 'template_name': 'events/calendar_year.html'}),

url(r'^calendar/tri_month/(?P<calendar_slug>[-\w]+)/$',
    'events.views.calendar_by_periods',
    name="tri_month_calendar",
    kwargs={'periods': [Month], 'template_name': 'events/calendar_tri_month.html'}),

url(r'^calendar/compact_month/(?P<calendar_slug>[-\w]+)/$',
    'events.views.calendar_by_periods',
    name="compact_calendar",
    kwargs={'periods': [Month], 'template_name': 'events/calendar_compact_month.html'}),

url(r'^calendar/month/(?P<calendar_slug>[-\w]+)/$',
    'events.views.calendar_by_periods',
    name="month_calendar",
    kwargs={'periods': [Month], 'template_name': 'events/calendar_month.html'}),

url(r'^calendar/week/(?P<calendar_slug>[-\w]+)/$',
    'events.views.calendar_by_periods',
    name="week_calendar",
    kwargs={'periods': [Week], 'template_name': 'events/calendar_week.html'}),

url(r'^calendar/daily/(?P<calendar_slug>[-\w]+)/$',
    'events.views.calendar_by_periods',
    name="day_calendar",
    kwargs={'periods': [Day], 'template_name': 'events/calendar_day.html'}),

url(r'^calendar/(?P<calendar_slug>[-\w]+)/$',
    'events.views.calendar',
    name="calendar_home",
    ),

url(r'^calendar/(?P<calendar_slug>[-\w]+)/events/$',
    'events.views.calendar_events',
    name="calendar_events",
    ),

#Event Urls
url(r'^event/create/(?P<calendar_slug>[-\w]+)/$',
    'events.views.create_or_edit_event',
    name='calendar_create_event'),
url(r'^event/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$',
    'events.views.create_or_edit_event',
    name='edit_event'),
url(r'^event/(?P<event_id>\d+)/$',
    'events.views.event',
    name="event"),
url(r'^event/delete/(?P<event_id>\d+)/$',
    'events.views.delete_event',
    name="delete_event"),

#urls for already persisted occurrences
url(r'^occurrence/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$',
    'events.views.occurrence',
    name="occurrence"),
url(r'^occurrence/cancel/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$',
    'events.views.cancel_occurrence',
    name="cancel_occurrence"),
url(r'^occurrence/edit/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$',
    'events.views.edit_occurrence',
    name="edit_occurrence"),

#urls for unpersisted occurrences
url(r'^occurrence/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
    'events.views.occurrence',
    name="occurrence_by_date"),
url(r'^occurrence/cancel/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
    'events.views.cancel_occurrence',
    name="cancel_occurrence_by_date"),
url(r'^occurrence/edit/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
    'events.views.edit_occurrence',
    name="edit_occurrence_by_date"),

#feed urls
url(r'^feed/calendar/(.*)/$', UpcomingEventsFeed(), name="upcoming_events_feed"),

(r'^ical/calendar/(.*)/$', CalendarICalendar()),

# AJAX API

#url for occurrences by encoded data
url(r'^ajax/occurrence/edit_by_code/$',
    'events.views.ajax_edit_occurrence_by_code',
    name="ajax_edit_occurrence_by_code"),

url(r'^ajax/calendar/week/json/(?P<calendar_slug>[-\w]+)/$',
    'events.views.calendar_by_periods_json',
    name="week_calendar_json",
    kwargs={'periods': [Week]}),

url(r'^ajax/edit_event/(?P<calendar_slug>[-\w]+)/$',
    'events.views.ajax_edit_event',
    name="ajax_edit_event"),

url(r'^event_json/$',
    'events.views.event_json',
    name="event_json"),

 url(r'^$', ListView.as_view(queryset=Calendar.objects.all()), name='events'),

)
