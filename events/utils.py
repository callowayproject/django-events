import datetime
import heapq
from six.moves.builtins import object
from functools import wraps
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.conf import settings
from django.template import Context, loader
from django.utils.module_loading import import_string
from .settings import CHECK_PERMISSION_FUNC, CHECK_EVENT_PERM_FUNC, CHECK_CALENDAR_PERM_FUNC


class EventListManager(object):
    """
    This class is responsible for doing functions on a list of events. It is
    used to when one has a list of events and wants to access the occurrences
    from these events in as a group
    """
    def __init__(self, events):
        self.events = events

    def occurrences_after(self, after=None):
        """
        It is often useful to know what the next occurrence is given a list of
        events.  This function produces a generator that yields the
        the most recent occurrence after the date ``after`` from any of the
        events in ``self.events``
        """
        from events.models import Occurrence
        if after is None:
            after = timezone.now()
        occ_replacer = OccurrenceReplacer(
            Occurrence.objects.filter(event__in=self.events))
        generators = [event._occurrences_after_generator(after) for event in self.events]
        occurrences = []

        for generator in generators:
            try:
                heapq.heappush(occurrences, (generator.next(), generator))
            except StopIteration:
                pass

        while True:
            if len(occurrences) == 0:
                raise StopIteration

            generator = occurrences[0][1]

            try:
                next_occurance = heapq.heapreplace(occurrences, (next(generator), generator))[0]
            except StopIteration:
                next_occurance = heapq.heappop(occurrences)[0]
            yield occ_replacer.get_occurrence(next_occurance)


class OccurrenceReplacer(object):
    """
    When getting a list of occurrences, the last thing that needs to be done
    before passing it forward is to make sure all of the occurrences that
    have been stored in the datebase replace, in the list you are returning,
    the generated ones that are equivalent.  This class makes this easier.
    """
    def __init__(self, persisted_occurrences):
        lookup = [((occ.event_id, occ.original_start, occ.original_end), occ) for
            occ in persisted_occurrences]
        self.lookup = dict(lookup)

    def get_occurrence(self, occ):
        """
        Return a persisted occurrences matching the occ and remove it from lookup since it
        has already been matched
        """
        return self.lookup.pop(
            (occ.event_id, occ.original_start, occ.original_end),
            occ)

    def has_occurrence(self, occ):
        return (occ.event_id, occ.original_start, occ.original_end) in self.lookup

    def get_additional_occurrences(self, start, end):
        """
        Return persisted occurrences which are now in the period
        """
        return [occ for key, occ in self.lookup.items() if (occ.start < end and occ.end >= start and not occ.cancelled)]


def check_event_permissions(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        from schedule.models import Event, Calendar
        user = request.user
        # check event permission
        try:
            event = Event.objects.get(pk=kwargs.get('event_id', None))
        except Event.DoesNotExist:
            event = None
        allowed = CHECK_EVENT_PERM_FUNC(event, user)
        if not allowed:
            return HttpResponseRedirect(settings.LOGIN_URL)

        # check calendar permissions
        calendar = None
        if event:
            calendar = event.calendar
        elif 'calendar_slug' in kwargs:
            calendar = Calendar.objects.get(slug=kwargs['calendar_slug'])
        allowed = CHECK_CALENDAR_PERM_FUNC(calendar, user)
        if not allowed:
            return HttpResponseRedirect(settings.LOGIN_URL)

        # all checks passed
        return function(request, *args, **kwargs)

    return decorator


def coerce_date_dict(date_dict):
    """
    given a dictionary (presumed to be from request.GET) it returns a tuple
    that represents a date. It will return from year down to seconds until one
    is not found.  ie if year, month, and seconds are in the dictionary, only
    year and month will be returned, the rest will be returned as min. If none
    of the parts are found return an empty tuple.
    """
    keys = ['year', 'month', 'day', 'hour', 'minute', 'second']
    ret_val = {
        'year': 1,
        'month': 1,
        'day': 1,
        'hour': 0,
        'minute': 0,
        'second': 0,
        'tzinfo': timezone.utc}
    modified = False
    for key in keys:
        try:
            ret_val[key] = int(date_dict[key])
            modified = True
        except KeyError:
            break
    return modified and ret_val or {}


occtimeformat = 'ST%Y%m%d%H%M%S'


def encode_occurrence(occ):
    """
        Create a temp id containing event id, encoded id if it is persisted,
        otherwise timestamp.
        Used by AJAX implementations so that JS can assemble a URL
        for calls to occurrence_edit
    """
    if occ.id:
        s = 'ID%d' % occ.id
    else:
        s = occ.start.strftime(occtimeformat)
    return 'E%d_%s' % (occ.event.id, s)


def decode_occurrence(id):
    """
        reverse of encode_occurrence - given an encoded string
        returns a dict containing event_id and occurrence data
        occurrence data contain either occurrence_id
        or year, month etc.
    """
    try:
        res = {}
        parts = id.split('_')
        res['event_id'] = parts[0][1:]
        occ = parts[1]
        if occ.startswith('ID'):
            res['occurrence_id'] = occ[2:]
        else:
            start = datetime.datetime.strptime(occ, occtimeformat)
            occ_data = dict(year=start.year, month=start.month, day=start.day,
                hour=start.hour, minute=start.minute, second=start.second)
            res.update(occ_data)
        return res
    except IndexError:
        return


def serialize_occurrences(occurrences, user):
    occ_list = []
    for occ in occurrences:
        original_id = occ.id
        occ.id = encode_occurrence(occ)
        occ.start = occ.start.ctime()
        occ.end = occ.end.ctime()
        occ.read_only = not CHECK_PERMISSION_FUNC(occ, user)
        occ.recurring = bool(occ.event.rule)
        occ.persisted = bool(original_id)
        # these attributes are very important from UI point of view
        # if occ is recurreing and not persisted then a user can edit either event or occurrence
        # once an occ has been edited it is persisted so he can edit only occurrence
        # if occ represents non-recurring event then he always edits the event
        occ.description = occ.description.replace('\n', '\\n')  # this can be multiline
        occ_list.append(occ)
    rnd = loader.get_template('events/occurrences_json.html')
    resp = rnd.render(Context({'occurrences': occ_list}))
    return resp


def model_to_dict(instance, fields=None, exclude=None):
    """
    Customized from Django's to do things recursively

    Returns a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    # avoid a circular import
    from django.db.models.fields.related import ManyToManyField
    opts = instance._meta
    data = {}
    for f in sorted(getattr(opts, 'concrete_fields', opts.fields) + opts.many_to_many):
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if isinstance(f, ManyToManyField):
            # If the object doesn't have a primary key yet, just use an empty
            # list for its m2m fields. Calling f.value_from_object will raise
            # an exception.
            if instance.pk is None:
                data[f.name] = []
            else:
                # MultipleChoiceWidget needs a list of pks, not object instances.
                data[f.name] = list(f.value_from_object(instance).values())
        else:
            data[f.name] = f.value_from_object(instance)
    return data


def get_model_bases():
    from .settings import BASE_CLASSES
    from django.db.models import Model

    if BASE_CLASSES is None:
        return [Model]
    else:
        return [import_string(x) for x in BASE_CLASSES]
