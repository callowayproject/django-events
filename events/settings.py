from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q

DEFAULT_SETTINGS = {
    # whether to display cancelled occurrences
    # (if they are displayed then they have a css class "cancelled")
    # this controls behaviour of Period.classify_occurrence method
    'SHOW_CANCELLED_OCCURRENCES': False,

    # Callable used to check if a user has edit permissions to event
    # (and occurrence). Used by check_edit_permission decorator
    # if ob==None we check permission to add occurrence
    'CHECK_PERMISSION_FUNC': lambda ob, user: user.is_authenticated(),
    'CHECK_EVENT_PERM_FUNC': lambda ob, user: user.is_authenticated(),
    'CHECK_CALENDAR_PERM_FUNC': lambda ob, user: user.is_authenticated(),

    # Callable used to customize the event list given for a calendar and user
    # (e.g. all events on that calendar, those events plus another calendar's events,
    # or the events filtered based on user permissions)
    # Imports have to be placed within the function body to avoid circular imports
    'GET_EVENTS_FUNC': lambda request, calendar: calendar.events.all(),

    # URL to redirect to to after an occurrence is canceled
    'OCCURRENCE_CANCEL_REDIRECT': None,

    'EVENT_RELATION_MODELS': [],
    'CALENDAR_RELATION_MODELS': [],
    'DEFAULT_RULE_ID': 1,
    'BASE_CLASSES': None,
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(settings, 'EVENTS_SETTINGS', {}))

RELATIONS = [Q(app_label=al, model=m) for al, m in [x.split('.') for x in USER_SETTINGS['EVENT_RELATION_MODELS']]]
CALENDAR_RELATIONS = [Q(app_label=al, model=m) for al, m in [x.split('.') for x in USER_SETTINGS['CALENDAR_RELATION_MODELS']]]

if hasattr(settings, 'FIRST_DAY_OF_WEEK'):
    try:
        FIRST_DAY_OF_WEEK = int(settings.FIRST_DAY_OF_WEEK)
    except ValueError:
        raise ImproperlyConfigured("FIRST_DAY_OF_WEEK must be an integer between 0 and 6")

if hasattr(settings, 'SHOW_CANCELLED_OCCURRENCES'):
    USER_SETTINGS['SHOW_CANCELLED_OCCURRENCES'] = settings.SHOW_CANCELLED_OCCURRENCES

if hasattr(settings, 'CHECK_PERMISSION_FUNC'):
    USER_SETTINGS['CHECK_PERMISSION_FUNC'] = settings.CHECK_PERMISSION_FUNC

if hasattr(settings, 'GET_EVENTS_FUNC'):
    USER_SETTINGS['GET_EVENTS_FUNC'] = settings.GET_EVENTS_FUNC

if hasattr(settings, 'OCCURRENCE_CANCEL_REDIRECT'):
    USER_SETTINGS['OCCURRENCE_CANCEL_REDIRECT'] = settings.OCCURRENCE_CANCEL_REDIRECT

globals().update(USER_SETTINGS)
