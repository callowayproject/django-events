import datetime
from collections import defaultdict
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from events.jsonresponse import JSONResponse
from events.models import Calendar, Event, CalendarRelation, EventRelation
from django.contrib.contenttypes.models import ContentType
from events.periods import Period
from events.settings import GET_EVENTS_FUNC
from events.utils import encode_occurrence
from dateutil.tz import tzutc

from events.utils import model_to_dict


def calendar_list(request):
    calendars = Calendar.objects.all()  # prefetch_related('calendarrelation')
    cals = []
    for cal in calendars:
        caldict = model_to_dict(cal)
        caldict['relations'] = defaultdict(list)
        for rel in cal.calendarrelation.all():
            caldict['relations'][rel.distinction or 'None'] = model_to_dict(rel)
        cals.append(caldict)
    return JSONResponse(list(cals))


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
    if settings.USE_TZ:
        start = start and datetime.datetime.fromtimestamp(int(start), tzutc())
        end = end and datetime.datetime.fromtimestamp(int(end), tzutc())
    else:
        start = start and datetime.datetime.fromtimestamp(int(start))
        end = end and datetime.datetime.fromtimestamp(int(end))

    events = GET_EVENTS_FUNC(request, calendar)
    period = Period(events, start, end)
    cal_events = []
    for o in period.get_occurrences():
        audiences = [x[0] for x in o.event.appropriate_for.get_set_flags()]
        if o.event.all_day:
            start = o.start.date().isoformat()
            diff = o.end - o.start
            end = o.start.date() + datetime.timedelta(days=diff.days)
            end = end.isoformat()
        else:
            start = o.start.isoformat()
            end = o.end.isoformat()
        cal_event = {
            'id': encode_occurrence(o),
            'allDay': o.event.all_day,
            'event_id': o.event.pk,
            'start': start,
            'end': end,
            'title': "%s %s" % ("".join(audiences), o.title),
            'description': o.description,
            'edit_url': reverse('admin:events_event_change', args=(o.event.pk, )),
            'update_url': reverse('ajax_edit_event', kwargs={'calendar_slug': calendar_slug}),
            'update_occurrence_url': reverse('ajax_edit_occurrence_by_code'),
            'repeating_id': o.event.rule_id,
            'repeating_name': getattr(o.event.rule, "name", ""),
            'repeats': o.event.rule != None,
            'audiences': audiences,
        }
        cal_events.append(cal_event)

    return JSONResponse(cal_events)


def contenttype_list(request):
    """
    Get all content types that are attached to a calendar
    """
    ctype = ContentType.objects.get_for_model(ContentType)
    valid_types = CalendarRelation.objects.filter(content_type=ctype).values_list('object_id', flat=True)
    return JSONResponse(ContentType.objects.filter(id__in=list(valid_types)).values())


def contenttype_content(request, contenttype_id):
    """
    Return all the content for the contenttype_id
    """
    from django.contrib.admin import site
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    ctype = ContentType.objects.get_for_id(contenttype_id)
    modeladmin = site._registry[ctype.model_class()]
    new_GET = request.GET.copy()
    page = new_GET.pop('page', 1)
    per_page = new_GET.pop('perPage', 5)
    if isinstance(page, (list, tuple)):
        page = page[0]
    if isinstance(per_page, (list, tuple)):
        per_page = per_page[0]
    request.GET = new_GET
    response = modeladmin.changelist_view(request)
    qset = response.context_data['cl'].get_query_set(request).all()
    paginator = Paginator(qset, per_page)
    try:
        # page = request.GET.get('page')
        objects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects = paginator.page(paginator.num_pages)

    object_list = []
    for item in objects.object_list:
        record = {
            'id': item.id,
            'description': item.__unicode__(),
            'contenttype': contenttype_id
        }
        if modeladmin.search_fields:
            for field in modeladmin.search_fields:
                try:
                    record[field] = getattr(item, field)
                except AttributeError:
                    continue
        object_list.append(record)
    return JSONResponse({
        'models': object_list,
        'page': objects.number,
        'perPage': per_page,
        'total': objects.paginator.count
    })


def get_content_hover(request, contenttype_id, object_id):
    """
    Return the information for the specified object for the hover tooltip
    """
    ctype = ContentType.objects.get_for_id(contenttype_id)
    obj = ctype.get_object_for_this_type(id=object_id)
    events = EventRelation.objects.get_events_for_object(obj)
    dates = "<br/>".join([e.start.strftime('%x') for e in events]) or "Not Scheduled"
    return JSONResponse(dates)


def calendars_for_content(request, contenttype_id):
    """
    Return which calendars this content could go on
    """
    ctype = ContentType.objects.get_for_id(contenttype_id)
    calendars = Calendar.objects.get_calendars_for_object(ctype)
    return JSONResponse(list(calendars.values()))


@csrf_exempt
def create_event_for_content(request):
    """
    Create an event for the content submitted
    """
    from events.forms import ContentEventForm
    cal_event = {}
    if request.method == 'POST':
        form = ContentEventForm(request.POST)
        if form.is_valid():
            ctype = ContentType.objects.get_for_id(form.cleaned_data['content_type_id'])
            obj = ctype.get_object_for_this_type(id=form.cleaned_data['object_id'])
            if form.cleaned_data['calendar_id']:
                calendar = Calendar.objects.get(id=form.cleaned_data['calendar_id'])
            else:
                calendar = Calendar.objects.get_calendar_for_object(ctype)
            start = form.cleaned_data['start']
            event = Event.objects.create(
                start=start,
                end=start,
                all_day=True,
                calendar=calendar,
                title=unicode(obj)[:30] + "...",
                description=unicode(obj),
                creator=request.user
            )
            event.save()
            EventRelation.objects.create_relation(event, obj)
        cal_event = {
            'id': encode_occurrence(event._create_occurrence(start)),
            'allDay': True,
            'event_id': event.pk,
            'start': event.start.isoformat(),
            'end': event.end.isoformat(),
            'title': event.title,
            'description': event.description,
            'edit_url': reverse('admin:events_event_change', args=(event.pk, )),
            'update_url': reverse('ajax_edit_event', kwargs={'calendar_slug': event.calendar.slug}),
            'update_occurrence_url': reverse('ajax_edit_occurrence_by_code'),
            'repeating_id': event.rule_id,
            'repeating_name': getattr(event.rule, "name", ""),
            'repeats': event.rule != None,
            'calendar_slug': calendar.slug,
        }

    return JSONResponse(cal_event)
