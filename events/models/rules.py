from django.db import models
from django.utils.translation import ugettext_lazy as _
from dateutil import rrule

RRULE_WEEKDAYS = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}

freqs = (
    ("YEARLY", _("Yearly")),
    ("MONTHLY", _("Monthly")),
    ("WEEKLY", _("Weekly")),
    ("DAILY", _("Daily")),
    ("HOURLY", _("Hourly")),
    ("MINUTELY", _("Minutely")),
    ("SECONDLY", _("Secondly"))
)
freq_params = (
    'interval',
    'count',
    'bysetpos',
    'bymonth',
    'bymonthday',
    'byyearday',
    'byweekno',
    'byweekday',
    'byhour',
    'byminute',
    'bysecond',
    'byeaster'
)


def parse_single_int(param, value):
    try:
        return param, int(value)
    except ValueError:
        raise ValueError('%s parameter requires a single integer value' % param)


def parse_oneormore_int(param, value):
    try:
        values = value.split(',')
        return param, map(int, values)
    except ValueError:
        raise ValueError('%s parameter requires one or more integer values' % param)


def parse_count(param, value):
    return parse_single_int(param, value)


def parse_interval(param, value):
    return parse_single_int(param, value)


def parse_bysetpos(param, value):
    return parse_oneormore_int(param, value)


def parse_bymonth(param, value):
    return parse_oneormore_int(param, value)


def parse_bymonthday(param, value):
    return parse_oneormore_int(param, value)


def parse_byyearday(param, value):
    return parse_oneormore_int(param, value)


def parse_byweekno(param, value):
    return parse_oneormore_int(param, value)


def parse_byweekday(param, value):
    values = []
    for val in value.split(','):
        if val in RRULE_WEEKDAYS:
            try:
                values.append(rrule.__dict__[val])
            except ValueError:
                raise ValueError('byweekday parameter improperly formatted. Error on: %s' % val)
        else:
            try:
                values.append(int(val))
            except ValueError:
                raise ValueError('byweekday parameter should be integer or weekday constant (e.g. MO, TU, etc.). Error on: %s' % val)
    return param, values


def parse_byhour(param, value):
    return parse_oneormore_int(param, value)


def parse_byminute(param, value):
    return parse_oneormore_int(param, value)


def parse_bysecond(param, value):
    return parse_oneormore_int(param, value)


def parse_byeaster(param, value):
    return parse_oneormore_int(param, value)


def parse_params(paramstring):
    """
    Returns a dictionary parsed from a semicolon-delimited set of rrules

    "count:1;bysecond:1;byminute:1,2,4,5" returns
    {'count': 1, 'byminute': [1, 2, 4, 5], 'bysecond': 1}
    """
    if paramstring.strip() == "":
        return {}
    params = paramstring.split(';')
    param_dict = []
    for param in params:
        if param.strip() == "":
            continue  # skip blanks
        paramval = [i.strip() for i in param.split(':')]
        funcname = "parse_%s" % paramval[0]
        if funcname in globals():
            try:
                param_dict.append(globals()[funcname](*paramval))
            except (TypeError, ValueError):
                continue
    return dict(param_dict)


class Rule(models.Model):
    """
    This defines a rule by which an event will recur.  This is defined by the
    rrule in the dateutil documentation.

    * name - the human friendly name of this kind of recursion.
    * description - a short description describing this type of recursion.
    * frequency - the base recurrence period
    * param - extra params required to define this type of recursion. The params
      should follow this format:

        param = [rruleparam:value;]*
        rruleparam = see list below
        value = int[,int]*

      The options are: (documentation for these can be found at
      http://labix.org/python-dateutil#head-470fa22b2db72000d7abe698a5783a46b0731b57)
        ** interval
        ** count
        ** bysetpos
        ** bymonth
        ** bymonthday
        ** byyearday
        ** byweekno
        ** byweekday
        ** byhour
        ** byminute
        ** bysecond
        ** byeaster
    """

    name = models.CharField(_("name"), max_length=32)
    description = models.TextField(_("description"))
    frequency = models.CharField(_("frequency"), choices=freqs, max_length=10)
    params = models.TextField(_("params"), null=True, blank=True)

    class Meta:
        verbose_name = _('rule')
        verbose_name_plural = _('rules')
        app_label = 'events'

    def get_params(self):
        """
        >>> rule = Rule(params = "count:1;bysecond:1;byminute:1,2,4,5")
        >>> rule.get_params()
        {'count': 1, 'byminute': [1, 2, 4, 5], 'bysecond': 1}
        """
        if self.params is None:
            return {}
        return parse_params(self.params)

    def __unicode__(self):
        """Human readable string for Rule"""
        return self.name
