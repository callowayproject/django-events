from django.conf.urls import url
from django.views.generic import ListView

from events.feeds import UpcomingEventsFeed
from events.feeds import CalendarICalendar
from events.models import Calendar
from events.periods import Year, Month, Week, Day
from events.views import (
    ajax_edit_event, ajax_edit_occurrence_by_code, calendar,
    calendar_by_periods, calendar_by_periods_json, calendar_events,
    calendars_for_content, calendar_list, cancel_occurrence,
    contenttype_content, contenttype_list, create_event_for_content,
    create_or_edit_event, delete_event, edit_occurrence, event, event_json,
    get_content_hover, occurrence)


urlpatterns = [
    # urls for Calendars
    url(r'^calendar/$', ListView.as_view(
        queryset=Calendar.objects.all(),
        template_name='events/calendar_list.html'), name="events"),
    url(r'^calendar/year/(?P<calendar_slug>[-\w]+)/$', calendar_by_periods,
        name="year_calendar",
        kwargs={'periods': [Year],
                'template_name': 'events/calendar_year.html'}),
    url(r'^calendar/tri_month/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods, name="tri_month_calendar",
        kwargs={'periods': [Month],
                'template_name': 'events/calendar_tri_month.html'}),
    url(r'^calendar/compact_month/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods, name="compact_calendar",
        kwargs={'periods': [Month],
                'template_name': 'events/calendar_compact_month.html'}),
    url(r'^calendar/month/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods, name="month_calendar",
        kwargs={'periods': [Month],
                'template_name': 'events/calendar_month.html'}),
    url(r'^calendar/week/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods, name="week_calendar",
        kwargs={'periods': [Week],
                'template_name': 'events/calendar_week.html'}),
    url(r'^calendar/daily/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods, name="day_calendar",
        kwargs={'periods': [Day],
                'template_name': 'events/calendar_day.html'}),
    url(r'^calendar/(?P<calendar_slug>[-\w]+)/$',
        calendar, name="calendar_home",),
    url(r'^calendar/(?P<calendar_slug>[-\w]+)/events/$', calendar_events,
        name="calendar_events"),

    # Event Urls
    url(r'^event/create/(?P<calendar_slug>[-\w]+)/$', create_or_edit_event,
        name='calendar_create_event'),
    url(r'^event/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$',
        create_or_edit_event, name='edit_event'),
    url(r'^event/(?P<event_id>\d+)/$', event, name="event"),
    url(r'^event/delete/(?P<event_id>\d+)/$', delete_event,
        name="delete_event"),

    # urls for already persisted occurrences
    url(r'^occurrence/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$', occurrence,
        name="occurrence"),
    url(r'^occurrence/cancel/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$',
        cancel_occurrence, name="cancel_occurrence"),
    url(r'^occurrence/edit/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$',
        edit_occurrence, name="edit_occurrence"),

    # urls for unpersisted occurrences
    url(r'^occurrence/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
        occurrence, name="occurrence_by_date"),
    url(r'^occurrence/cancel/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
        cancel_occurrence, name="cancel_occurrence_by_date"),
    url(r'^occurrence/edit/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
        edit_occurrence, name="edit_occurrence_by_date"),

    # feed urls
    url(r'^feed/calendar/(.*)/$', UpcomingEventsFeed(),
        name="upcoming_events_feed"),
    url(r'^ical/calendar/(.*)/$', CalendarICalendar()),
    url(r'^$', ListView.as_view(queryset=Calendar.objects.all()),
        name='events'),

    # AJAX API

    # url for occurrences by encoded data
    url(r'^ajax/occurrence/edit_by_code/$', ajax_edit_occurrence_by_code,
        name="ajax_edit_occurrence_by_code"),
    url(r'^ajax/calendar/week/json/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods_json, name="week_calendar_json",
        kwargs={'periods': [Week]}),
    url(r'^ajax/edit_event/(?P<calendar_slug>[-\w]+)/$',
        ajax_edit_event, name="ajax_edit_event"),
    url(r'^event_json/$', event_json, name="event_json"),
    url(r'^ajax/calendars/$', calendar_list, name="ajax_calendar_list"),
    url(r'^ajax/contenttypes/$', contenttype_list,
        name="ajax_contenttype_list"),
    url(r'^ajax/contenttypes/(?P<contenttype_id>[\d_-]+)/calendars/$',
        calendars_for_content, name="ajax_contenttype_calendars"),
    url(r'^ajax/contenttypes/(?P<contenttype_id>[\d_-]+)/content/$',
        contenttype_content, name="ajax_contenttype_content"),
    url(r'^ajax/contenttypes/(?P<contenttype_id>[\d_-]+)/content/(?P<object_id>\d+)/$',
        get_content_hover, name="ajax_content_hover"),
    url(r'^ajax/event_from_content/$', create_event_for_content,
        name="ajax_event_from_content"),
    ]
