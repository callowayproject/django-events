import datetime
import json
from collections import defaultdict
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from dateutil.tz import tzutc
from events.jsonresponse import JSONResponse
from events.models import Calendar, Event, CalendarRelation, EventRelation, Rule
from events.periods import Period
from events.settings import GET_EVENTS_FUNC
from events.utils import encode_occurrence
from events.utils import model_to_dict
from audience.settings import VALID_AUDIENCES, AUDIENCE_TYPES

__all__ = ('calendar_list', 'calendar_events', 'contenttype_list',
           'contenttype_content', 'get_content_hover', 'calendars_for_content',
           'create_event_for_content', )


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
        audience_bits = [x for x in o.event.appropriate_for.get_set_bits() if x in VALID_AUDIENCES]
        audiences = [AUDIENCE_TYPES[x]['name'][0] for x in audience_bits]
        if o.event.all_day:
            start = o.start.date().isoformat()
            diff = o.end - o.start
            end = o.start.date() + datetime.timedelta(days=diff.days)
            end = end.isoformat()
        else:
            start = o.start.isoformat()
            end = o.end.isoformat()
        occurrence_id = encode_occurrence(o)
        cal_event = {
            'id': occurrence_id,
            'allDay': o.event.all_day,
            'event_id': o.event.pk,
            'start': start,
            'end': end,
            'title': "%s %s" % ("".join(audiences), o.title),
            'description': o.description,
            'delete_url': "%s?id=%s&amp;action=cancel" % (reverse('ajax_edit_event', kwargs={'calendar_slug': calendar_slug}), o.event.pk),
            'delete_occurrence_url': "%s?id=%s&amp;action=cancel" % (reverse('ajax_edit_event', kwargs={'calendar_slug': calendar_slug}), occurrence_id),
            'edit_url': reverse('admin:events_event_change', args=(o.event.pk, )),
            'update_url': reverse('ajax_edit_event', kwargs={'calendar_slug': calendar_slug}),
            'update_occurrence_url': "%s?id=%s" % (reverse('ajax_edit_event', kwargs={'calendar_slug': calendar_slug}), occurrence_id),
            'repeating_id': o.event.rule_id,
            'repeating_name': getattr(o.event.rule, "name", ""),
            'repeats': o.event.rule is not None,
            'audiences': audiences,
        }
        cal_events.append(cal_event)

    return JSONResponse(cal_events)


def contenttype_list(request):
    """
    Get all content types that are attached to a calendar
    """
    ctype = ContentType.objects.get_for_model(ContentType)
    valid_types = CalendarRelation.objects.filter(content_type=ctype).select_related()
    ctype_list = []
    seen_ctypes = []
    for t in valid_types:
        try:
            limits = json.loads(t.limit_choices_to)
        except Exception:
            limits = False
        if limits:  # A calendar with valid limits, means we need a custom name and id
            ctype_id = '%s_%s' % (t.content_object.id, t.id)
            ctype_name = '%s for %s' % (t.content_object.name, t.calendar.name)
        else:
            ctype_id = t.content_object.id
            ctype_name = t.content_object.name
        if ctype_id in seen_ctypes:
            continue
        seen_ctypes.append(ctype_id)
        ctype_list.append({
            'model': t.content_object.model,
            'app_label': t.content_object.app_label,
            'name': ctype_name,
            'id': ctype_id,
        })

    return JSONResponse(ctype_list)


def contenttype_content(request, contenttype_id):
    """
    Return all the content for the contenttype_id
    """
    from django.contrib.admin import site
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    if '_' in contenttype_id:
        ctype_id, calrelation_id = map(int, contenttype_id.split('_'))
        calrelation = get_object_or_404(CalendarRelation, id=calrelation_id)
        limit_choices_to = json.loads(calrelation.limit_choices_to)
    else:
        ctype_id = int(contenttype_id)
        cal_id = None
        limit_choices_to = False
    ctype = ContentType.objects.get_for_id(ctype_id)
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
    if limit_choices_to:
        qset = qset.filter(**limit_choices_to)
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
    if '_' in contenttype_id:
        ctype_id, calrelation_id = map(int, contenttype_id.split('_'))
    else:
        ctype_id = int(contenttype_id)
    ctype = ContentType.objects.get_for_id(ctype_id)
    obj = ctype.get_object_for_this_type(id=object_id)
    events = EventRelation.objects.get_events_for_object(obj)
    dates = "<br/>".join([e.start.strftime('%x') for e in events]) or "Not Scheduled"
    return JSONResponse(dates)


def calendars_for_content(request, contenttype_id):
    """
    Return which calendars this content could go on
    """
    if '_' in contenttype_id:
        ctype_id, calrelation_id = map(int, contenttype_id.split('_'))
        calrelation = get_object_or_404(CalendarRelation, id=calrelation_id)
        cal_dict = dict([(k, v) for k, v in calrelation.calendar.__dict__.items() if k[0] != '_'])
        return JSONResponse([cal_dict])
    else:
        ctype_id = int(contenttype_id)
        ctype = ContentType.objects.get_for_id(ctype_id)
        calendars = Calendar.objects.get_calendars_for_object(ctype)
        return JSONResponse(list(calendars.values()))


@csrf_exempt
def create_event_for_content(request):
    """
    Create an event for the content submitted
    """
    from events.settings import DEFAULT_RULE_ID
    try:
        rule = Rule.objects.get(id=DEFAULT_RULE_ID)
    except:
        rule = None

    from events.forms import ContentEventForm
    cal_event = {}
    if request.method == 'POST':
        form = ContentEventForm(request.POST)
        if form.is_valid():
            if '_' in form.cleaned_data['content_type_id']:
                ctype_id, calrelation_id = map(int, form.cleaned_data['content_type_id'].split('_'))
            else:
                ctype_id = int(form.cleaned_data['content_type_id'])
            ctype = ContentType.objects.get_for_id(ctype_id)
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
                creator=request.user,
                rule=rule
            )
            event.save()
            EventRelation.objects.create_relation(event, obj)
        o = event._create_occurrence(start)
        occurrence_id = encode_occurrence(o)
        cal_event = {
            'id': occurrence_id,
            'allDay': True,
            'event_id': event.pk,
            'start': event.start.isoformat(),
            'end': event.end.isoformat(),
            'title': event.title,
            'description': event.description,
            'delete_url': "%s?id=%s&amp;action=cancel" % (reverse('ajax_edit_event', kwargs={'calendar_slug': calendar.slug}), o.event.pk),
            'delete_occurrence_url': "%s?id=%s&amp;action=cancel" % (reverse('ajax_edit_event', kwargs={'calendar_slug': calendar.slug}), occurrence_id),
            'edit_url': reverse('admin:events_event_change', args=(o.event.pk, )),
            'update_url': reverse('ajax_edit_event', kwargs={'calendar_slug': calendar.slug}),
            'update_occurrence_url': "%s?id=%s" % (reverse('ajax_edit_event', kwargs={'calendar_slug': calendar.slug}), occurrence_id),
            'repeating_id': event.rule_id,
            'repeating_name': getattr(event.rule, "name", ""),
            'repeats': event.rule is not None,
            'calendar_slug': calendar.slug,
        }

    return JSONResponse(cal_event)
