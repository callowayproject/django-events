from events.utils import serialize_occurrences
from urllib import quote
from django.utils import timezone as tz
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.edit import DeleteView
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from events.settings import GET_EVENTS_FUNC, OCCURRENCE_CANCEL_REDIRECT
from events.forms import EventForm, OccurrenceForm
from events.forms import EventBackendForm, OccurrenceBackendForm
from events.models import Event, Occurrence, Calendar
from events.periods import weekday_names, Period
from events.utils import check_event_permissions, coerce_date_dict
from events.utils import encode_occurrence, decode_occurrence
import datetime
import json
from dateutil.tz import tzutc


def calendar(request, calendar_slug, template='events/calendar.html'):
    """
    This view returns a calendar.  This view should be used if you are
    interested in the meta data of a calendar, not if you want to display a
    calendar.  It is suggested that you use calendar_by_periods if you would
    like to display a calendar.

    Context Variables:

    ``calendar``
        The Calendar object designated by the ``calendar_slug``.
    """
    calendar = get_object_or_404(Calendar, slug=calendar_slug)
    return render_to_response(template, {
        "calendar": calendar,
    }, context_instance=RequestContext(request))


def calendar_by_periods(request, calendar_slug, periods=None,
    template_name="events/calendar_by_period.html"):
    """
    This view is for getting a calendar, but also getting periods with that
    calendar.  Which periods you get, is designated with the list periods. You
    can designate which date you the periods to be initialized to by passing
    a date in request.GET. See the template tag ``query_string_for_date``

    Context Variables:

    ``date``
        This was the date that was generated from the query string.

    ``periods``
        this is a dictionary that returns the periods from the list you passed
        in.  If you passed in Month and Day, then your dictionary would look
        like this

        ::

            {
                'month': <events.periods.Month object>
                'day':   <events.periods.Day object>
            }

        So in the template to access the Day period in the context you simply
        use ``periods.day``.

    ``calendar``
        This is the Calendar that is designated by the ``calendar_slug``.

    ``weekday_names``
        This is for convenience. It returns the local names of weekedays for
        internationalization.

    """
    calendar = get_object_or_404(Calendar, slug=calendar_slug)
    date = coerce_date_dict(request.GET)
    if date:
        try:
            date = datetime.datetime(**date)
        except ValueError:
            raise Http404
    else:
        date = tz.now()
    event_list = GET_EVENTS_FUNC(request, calendar)
    period_objects = dict([(period.__name__.lower(), period(event_list, date)) for period in periods])

    return render_to_response(template_name, {
            'date': date,
            'periods': period_objects,
            'calendar': calendar,
            'weekday_names': weekday_names,
            'here': quote(request.get_full_path()),
        }, context_instance=RequestContext(request),)


def event(request, event_id, template_name="events/event.html"):
    """
    This view is for showing an event. It is important to remember that an
    event is not an occurrence.  Events define a set of reccurring occurrences.
    If you would like to display an occurrence (a single instance of a
    recurring event) use occurrence.

    Context Variables:

    event
        This is the event designated by the event_id

    back_url
        this is the url that referred to this view.
    """
    event = get_object_or_404(Event, id=event_id)
    back_url = request.META.get('HTTP_REFERER', None)
    try:
        cal = event.calendar_set.get()
    except:
        cal = None
    return render_to_response(template_name, {
        "event": event,
        "back_url": back_url,
    }, context_instance=RequestContext(request))


def occurrence(request, event_id,
    template_name="events/occurrence.html", *args, **kwargs):
    """
    This view is used to display an occurrence.

    Context Variables:

    ``event``
        the event that produces the occurrence

    ``occurrence``
        the occurrence to be displayed

    ``back_url``
        the url from which this request was refered
    """
    event, occurrence = get_occurrence(event_id, *args, **kwargs)
    back_url = request.META.get('HTTP_REFERER', None)
    return render_to_response(template_name, {
        'event': event,
        'occurrence': occurrence,
        'back_url': back_url,
    }, context_instance=RequestContext(request))


@check_event_permissions
def edit_occurrence(request, event_id,
    template_name="events/edit_occurrence.html", *args, **kwargs):
    event, occurrence = get_occurrence(event_id, *args, **kwargs)
    next = kwargs.get('next', None)
    form = OccurrenceForm(data=request.POST or None, instance=occurrence)
    if form.is_valid():
        occurrence = form.save(commit=False)
        occurrence.event = event
        occurrence.save()
        next = next or get_next_url(request, occurrence.get_absolute_url())
        return HttpResponseRedirect(next)
    next = next or get_next_url(request, occurrence.get_absolute_url())
    return render_to_response(template_name, {
        'form': form,
        'occurrence': occurrence,
        'next': next,
    }, context_instance=RequestContext(request))


@check_event_permissions
def cancel_occurrence(request, event_id,
    template_name='events/cancel_occurrence.html', *args, **kwargs):
    """
    This view is used to cancel an occurrence. If it is called with a POST it
    will cancel the view. If it is called with a GET it will ask for
    conformation to cancel.
    """
    event, occurrence = get_occurrence(event_id, *args, **kwargs)
    next = kwargs.get('next', None) or get_next_url(request, event.get_absolute_url())
    if request.method != "POST":
        return render_to_response(template_name, {
            "occurrence": occurrence,
            "next": next,
        }, context_instance=RequestContext(request))
    occurrence.cancel()
    return HttpResponseRedirect(next)


def get_occurrence(event_id, occurrence_id=None, year=None, month=None,
    day=None, hour=None, minute=None, second=None):
    """
    Because occurrences don't have to be persisted, there must be two ways to
    retrieve them. both need an event, but if its persisted the occurrence can
    be retrieved with an id. If it is not persisted it takes a date to
    retrieve it.  This function returns an event and occurrence regardless of
    which method is used.
    """
    if(occurrence_id):
        occurrence = get_object_or_404(Occurrence, id=occurrence_id)
        event = occurrence.event
    elif not [x for x in (year, month, day, hour, minute, second) if x is None]:
        event = get_object_or_404(Event, id=event_id)
        occurrence = event.get_occurrence(
            datetime.datetime(int(year), int(month), int(day), int(hour),
                int(minute), int(second), tzinfo=tz.utc))
        if occurrence is None:
            raise Http404
    else:
        raise Http404
    return event, occurrence


@check_event_permissions
def create_or_edit_event(request, calendar_slug, event_id=None, next=None,
    template_name='events/create_event.html', form_class=EventForm):
    """
    This function, if it receives a GET request or if given an invalid form in a
    POST request it will generate the following response

    Template:
        events/create_event.html

    Context Variables:

    form:
        an instance of EventForm

    calendar:
        a Calendar with id=calendar_id

    if this function gets a GET request with ``year``, ``month``, ``day``,
    ``hour``, ``minute``, and ``second`` it will auto fill the form, with
    the date specifed in the GET being the start and 30 minutes from that
    being the end.

    If this form receives an event_id it will edit the event with that id, if it
    recieves a calendar_id and it is creating a new event it will add that event
    to the calendar with the id calendar_id

    If it is given a valid form in a POST request it will redirect with one of
    three options, in this order

    # Try to find a 'next' GET variable
    # If the key word argument redirect is set
    # Lastly redirect to the event detail of the recently create event
    """
    from .forms import EventRelationFormSet

    date = coerce_date_dict(request.GET)
    initial_data = None
    if date:
        try:
            start = datetime.datetime(**date)
            initial_data = {
                "start": start,
                "end": start + datetime.timedelta(minutes=30)
            }
        except TypeError:
            raise Http404
        except ValueError:
            raise Http404

    instance = None
    if event_id is not None:
        instance = get_object_or_404(Event, id=event_id)

    calendar = get_object_or_404(Calendar, slug=calendar_slug)

    form = form_class(data=request.POST or None, instance=instance,
        hour24=True, initial=initial_data)
    eventrelation_formset = None
    if form.is_valid():
        event = form.save(commit=False)
        if instance is None:
            event.creator = request.user
            event.calendar = calendar
        eventrelation_formset = EventRelationFormSet(request.POST, instance=event)
        if eventrelation_formset.is_valid():
            event.save()
            eventrelation_formset.save()
            next = next or reverse('event', args=[event.id])
            next = get_next_url(request, next)
            return HttpResponseRedirect(next)

    next = get_next_url(request, next)
    return render_to_response(template_name, {
        "form": form,
        "calendar": calendar,
        "relation_formset": eventrelation_formset or EventRelationFormSet(instance=instance),
        "next": next
    }, context_instance=RequestContext(request))


class DeleteEvent(DeleteView):

    model = Event
    slug_url_kwarg = 'event_id'
    slug_field = 'id'
    template_name = "events/delete_event.html"

    def get_success_url(self):
        self.success_url = get_next_url(self.request, reverse('day_calendar', args=[self.object.calendar.slug]))
        self.success_url = super(DeleteEvent, self).get_success_url()
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super(DeleteEvent, self).get_context_data(**kwargs)
        next = get_next_url(self.request, self.kwargs.get('next', reverse('day_calendar', args=[context['object'].calendar.slug])))
        context.update({'next': next, 'calendar_id': context['object'].calendar.id})
        return context

delete_event = check_event_permissions(DeleteEvent.as_view())


def check_next_url(next):
    """
    Checks to make sure the next url is not redirecting to another page.
    Basically it is a minimal security check.
    """
    if not next or '://' in next:
        return None
    return next


def get_next_url(request, default):
    next = default
    if OCCURRENCE_CANCEL_REDIRECT:
        next = OCCURRENCE_CANCEL_REDIRECT
    if 'next' in request.REQUEST and check_next_url(request.REQUEST['next']) is not None:
        next = request.REQUEST['next']
    return next


class JSONError(HttpResponse):

    def __init__(self, error):
        s = "{error:'%s'}" % error
        HttpResponse.__init__(self, s)
        # TODO strip html tags from form errors


def calendar_by_periods_json(request, calendar_slug, periods):
    # XXX is this function name good?
    # it conforms with the standard API structure but in this case it is rather cryptic
    user = request.user
    calendar = get_object_or_404(Calendar, slug=calendar_slug)
    date = coerce_date_dict(request.GET)
    if date:
        try:
            date = datetime.datetime(**date)
        except ValueError:
            raise Http404
    else:
        date = datetime.datetime.now()
    event_list = GET_EVENTS_FUNC(request, calendar)
    period_object = periods[0](event_list, date)
    occurrences = []
    for o in period_object.occurrences:
        if period_object.classify_occurrence(o):
            occurrences.append(o)
    resp = serialize_occurrences(occurrences, user)
    return HttpResponse(resp)


# TODO permissions check
def ajax_edit_occurrence_by_code(request):
    try:
        id = request.REQUEST.get('id')
        kwargs = decode_occurrence(id)
        event_id = kwargs.pop('event_id')
        event, occurrence = get_occurrence(event_id, **kwargs)
        if request.REQUEST.get('action') == 'cancel':
            occurrence.cancel()
            return HttpResponse(serialize_occurrences([occurrence], request.user))
        form = OccurrenceBackendForm(data=request.POST or None, instance=occurrence)
        if form.is_valid():
            occurrence = form.save(commit=False)
            occurrence.event = event
            occurrence.save()
            return HttpResponse(serialize_occurrences([occurrence], request.user))
        return JSONError(form.errors)
    except Exception, e:
        import traceback
        traceback.print_exc()
        return JSONError(e)


#TODO permission control
@csrf_exempt
def ajax_edit_event(request, calendar_slug):
    try:
        id = request.REQUEST.get('id')  # we got occurrence's encoded id or event id
        if id:
            kwargs = decode_occurrence(id)
            if kwargs:
                event_id = kwargs['event_id']
            else:
                event_id = id
            event = Event.objects.get(pk=event_id)
            # deleting an event
            if request.REQUEST.get('action') == 'cancel':
                # cancellation of a non-recurring event means deleting the event
                event.delete()
                # there is nothing more - we return empty json
                return HttpResponse(serialize_occurrences([], request.user))
            else:
                form = EventBackendForm(data=request.POST, instance=event)
                if form.is_valid():
                    event = form.save()
                    return HttpResponse(serialize_occurrences(event.get_occurrences(event.start, event.end), request.user))
                return JSONError(form.errors)
        else:
            calendar = get_object_or_404(Calendar, slug=calendar_slug)
            # creation of an event
            form = EventBackendForm(data=request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.creator = request.user
                event.calendar = calendar
                event.save()
                return HttpResponse(serialize_occurrences(event.get_occurrences(event.start, event.end), request.user))
            return JSONError(form.errors)
    except Exception, e:
        import traceback
        traceback.print_exc()
        return JSONError(e)


#TODO permission control
def event_json(request):
    event_id = request.REQUEST.get('event_id')
    event = get_object_or_404(Event, pk=event_id)
    event.rule_id = event.rule_id or "false"
    rnd = loader.get_template('events/event_json.html')
    resp = rnd.render(Context({'event': event}))
    return HttpResponse(resp)


def calendar_list(request):
    cals = Calendar.objects.values()
    calendars = json.dumps(list(cals), ensure_ascii=False)
    response = HttpResponse(calendars)
    response['Content-Type'] = 'application/json'

    return response


def admin_calendar_view(request):
    return render_to_response('admin/events/calendar.html', {
            'title': 'Calendar View',
            'calendars': Calendar.objects.all(),
            'add': False,
        }, context_instance=RequestContext(request))


def calendar_events(request, calendar_slug):
    """
    JSON events feed class conforming to the JQuery FullCalendar and
    jquery-week-calendar CalEvent standard.

    [1]: http://code.google.com/p/jquery-week-calendar/
    [2]: http://arshaw.com/fullcalendar
    Corresponds to: http://arshaw.com/fullcalendar/docs/#calevent-objects
    """
    calendar = get_object_or_404(Calendar, slug=calendar_slug)

    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    start = start and datetime.datetime.fromtimestamp(int(start), tzutc())
    end = end and datetime.datetime.fromtimestamp(int(end), tzutc())

    events = GET_EVENTS_FUNC(request, calendar)
    period = Period(events, start, end)
    cal_events = []
    for o in period.get_occurrences():
        start = o.start.isoformat()
        end = o.end.isoformat()
        cal_event = {
            'id': encode_occurrence(o),
            'allDay': o.event.all_day,
            'event_id': o.event.pk,
            'start': start,
            'end': end,
            'title': o.title,
            'description': o.description,
            'edit_url': reverse('admin:events_event_change', args=(o.event.pk, )),
            'update_url': reverse('ajax_edit_event', kwargs={'calendar_slug': calendar_slug}),
            'update_occurrence_url': reverse('ajax_edit_occurrence_by_code'),
            'repeating_id': o.event.rule_id,
            'repeating_name': getattr(o.event.rule, "name", ""),
            'repeats': o.event.rule != None,
        }
        cal_events.append(cal_event)
    json_cal_events = json.dumps(cal_events, ensure_ascii=False)
    response = HttpResponse(json_cal_events)
    response['Content-Type'] = 'application/json'

    return response
