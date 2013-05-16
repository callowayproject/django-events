import datetime
from django.utils import timezone as tz
from django.conf import settings
from django.utils.dates import WEEKDAYS, WEEKDAYS_ABBR
from events.settings import FIRST_DAY_OF_WEEK, SHOW_CANCELLED_OCCURRENCES
from events.models import Occurrence

weekday_names = []
weekday_abbrs = []
if FIRST_DAY_OF_WEEK == 1:
    # The calendar week starts on Monday
    for i in range(7):
        weekday_names.append(WEEKDAYS[i])
        weekday_abbrs.append(WEEKDAYS_ABBR[i])
else:
    # The calendar week starts on Sunday, not Monday
    weekday_names.append(WEEKDAYS[6])
    weekday_abbrs.append(WEEKDAYS_ABBR[6])
    for i in range(6):
        weekday_names.append(WEEKDAYS[i])
        weekday_abbrs.append(WEEKDAYS_ABBR[i])


class Period(object):
    '''
    This class represents a period of time. It can return a set of occurrences
    based on its events, and its time period (start and end).
    '''
    def __init__(self, events, start, end, parent_persisted_occurrences=None,
        occurrence_pool=None):
        self.start = start
        self.end = end
        self.events = events
        self.occurrence_pool = occurrence_pool
        if parent_persisted_occurrences is not None:
            self._persisted_occurrences = parent_persisted_occurrences

    def __eq__(self, period):
        return self.start == period.start and self.end == period.end and self.events == period.events

    def __ne__(self, period):
        return self.start != period.start or self.end != period.end or self.events != period.events

    def _get_sorted_occurrences(self):
        occurrences = []
        if hasattr(self, "occurrence_pool") and self.occurrence_pool is not None:
            for occurrence in self.occurrence_pool:
                if occurrence.start < self.end and occurrence.end > self.start:
                    occurrences.append(occurrence)
            return occurrences

        if hasattr(self.events, 'prefetch_related'):
            self.events = self.events.select_related('calendar').prefetch_related('rule', 'occurrence_set')
        for event in self.events:
            event_occurrences = event.get_occurrences(self.start, self.end)
            occurrences += event_occurrences
        return sorted(occurrences)

    @property
    def occurrences(self):
        """Returns self._occurrences if it's been defined, otherwise it creates and returns self._occurrences"""
        if hasattr(self, '_occurrences'):
            return self._occurrences
        self._occurrences = self._get_sorted_occurrences()
        return self._occurrences

    def get_all_day_occurrences(self):
        occ_list = [o for o in self.occurrences if o.event.all_day == True and o.end < self.end]
        return occ_list

    def get_persisted_occurrences(self):
        if hasattr(self, '_persisted_occurrenes'):
            return self._persisted_occurrences
        else:
            self._persisted_occurrences = Occurrence.objects.filter(event__in=self.events)
            return self._persisted_occurrences

    def classify_occurrence(self, occurrence):
        """
        You use this method to determine how the occurrence relates to the
        period. This method returns a dictionary. The keys are ``class``,
        ``occurrence`` and ``all_day``. The ``all_day`` key is a boolean that
        is ``True`` if the occurrence is an all day event and is ``False`` if
        the occurrence is not an all day event.  The ``class`` key returns a
        number from 0 to 3 and the occurrence key returns the occurrence.

        Classes:

            | 0 - Only started during this period.
            | 1 - Started and ended during this period.
            | 2 - Didn't start or end in this period, but does exist during this period.
            | 3 - Only ended during this period.
        """

        if occurrence.cancelled and not SHOW_CANCELLED_OCCURRENCES:
            return
        if occurrence.start > self.end or occurrence.end < self.start:
            return

        all_day = False
        started = False
        ended = False
        rtn_dict = {
            'occurrence': occurrence,
            'class': 2,
            'all_day': all_day,
        }

        if occurrence.event.all_day == True:
            all_day = True
            rtn_dict.update({'all_day': True})

        # Don't return all day events if the occurrence end datetime is
        # greater than the day start datetime
        if all_day and occurrence.end > self.end:
            return

        if occurrence.start >= self.start and occurrence.start < self.end:
            started = True

        if occurrence.end >= self.start and occurrence.end < self.end:
            ended = True

        if started and ended:
            rtn_dict.update({'class': 1})
        elif started:
            rtn_dict.update({'class': 0})
        elif ended:
            rtn_dict.update({'class': 3})

        return rtn_dict

    def get_occurrence_partials(self):
        occurrence_dicts = []
        for occurrence in self.occurrences:
            occurrence = self.classify_occurrence(occurrence)
            if occurrence:
                occurrence_dicts.append(occurrence)
        return occurrence_dicts

    def get_occurrences(self):
        return self.occurrences

    def has_occurrences(self):
        for occurrence in self.occurrences:
            occurrence = self.classify_occurrence(occurrence)
            if occurrence:
                return True
        return False

    def get_time_slot(self, start, end, occurrence_pool=None):
        if start >= self.start and end <= self.end:
            return Period(self.events, start, end,
                parent_persisted_occurrences=self.get_persisted_occurrences(),
                occurrence_pool=self.occurrences)
        return None

    def create_sub_period(self, cls, start=None, occurrence_pool=None):
        start = start or self.start
        if occurrence_pool:
            occurrences = occurrence_pool
        else:
            occurrences = self.occurrences
        return cls(self.events, start, parent_persisted_occurrences=self.get_persisted_occurrences(), occurrence_pool=occurrences)

    def get_periods(self, cls, occurrence_pool=None):
        period = self.create_sub_period(cls, occurrence_pool=occurrence_pool)
        while period.start < self.end:
            yield self.create_sub_period(cls, period.start, occurrence_pool=occurrence_pool)
            period = period.next()


class Year(Period):
    def __init__(self, events, date=None, parent_persisted_occurrences=None):
        if date is None:
            date = tz.now()
        start, end = self._get_year_range(date)
        super(Year, self).__init__(events, start, end, parent_persisted_occurrences)

    def get_months(self):
        return self.get_periods(Month)

    def next_year(self):
        return Year(self.events, self.end)
    next = next_year

    def prev_year(self):
        start = datetime.datetime(self.start.year - 1, self.start.month, self.start.day, tzinfo=tz.utc)
        return Year(self.events, start)
    prev = prev_year

    def _get_year_range(self, year):
        start = datetime.datetime(year.year, datetime.datetime.min.month,
            datetime.datetime.min.day, tzinfo=tz.utc)
        end = datetime.datetime(year.year + 1, datetime.datetime.min.month,
            datetime.datetime.min.day, tzinfo=tz.utc)
        return start, end

    def __unicode__(self):
        return self.start.strftime('%Y')


class Month(Period):
    """
    The month period has functions for retrieving the week periods within this period
    and day periods within the date.
    """
    def __init__(self, events, date=None, parent_persisted_occurrences=None, occurrence_pool=None):

        if not date:
            date = tz.now()
        start, end = self._get_month_range(date)
        super(Month, self).__init__(events, start, end, parent_persisted_occurrences, occurrence_pool)

    def get_weeks(self):
        return self.get_periods(Week)

    def get_days(self):
        return self.get_periods(Day)

    def get_day(self, daynumber):
        date = self.start
        if daynumber > 1:
            date += datetime.timedelta(days=daynumber - 1)
        return self.create_sub_period(Day, date)

    def next_month(self):
        return Month(self.events, self.end)
    next = next_month

    def prev_month(self):
        start = (self.start - datetime.timedelta(days=1)).replace(day=1)
        return Month(self.events, start)
    prev = prev_month

    def current_year(self):
        return Year(self.events, self.start)

    def prev_year(self):
        start = datetime.datetime.min.replace(year=self.start.year - 1, tzinfo=tz.utc)
        return Year(self.events, start)

    def next_year(self):
        start = datetime.datetime.min.replace(year=self.start.year + 1, tzinfo=tz.utc)
        return Year(self.events, start)

    def _get_month_range(self, month):
        year = month.year
        month = month.month
        start = datetime.datetime.min.replace(year=year, month=month, tzinfo=tz.utc)
        if month == 12:
            end = start.replace(month=1, year=year + 1)
        else:
            end = start.replace(month=month + 1)
        return start, end

    def __unicode__(self):
        return "%s %s" % (self.name(), self.year())

    def name(self):
        return self.start.strftime('%B')

    def year(self):
        return self.start.strftime('%Y')


class Week(Period):
    """
    The Week period that has functions for retrieving Day periods within it
    """

    def __init__(self, events, date=None, parent_persisted_occurrences=None, occurrence_pool=None):

        if date is None:
            date = tz.now()
        start, end = self._get_week_range(date)
        super(Week, self).__init__(events, start, end, parent_persisted_occurrences, occurrence_pool)

    def prev_week(self):
        return Week(self.events, self.start - datetime.timedelta(days=7))
    prev = prev_week

    def next_week(self):
        return Week(self.events, self.end)
    next = next_week

    def current_month(self):
        return Month(self.events, self.start)

    def current_year(self):
        return Year(self.events, self.start)

    def get_days_array(self):
        days = []
        for day in self.get_days():
            days.append(day)
        return days

    def get_days(self):
        return self.get_periods(Day, self.occurrences)

    def _get_week_range(self, week):

        if isinstance(week, datetime.datetime):
            week = week.date()
        # Adjust the start datetime to midnight of the week datetime
        start = datetime.datetime.combine(week, datetime.time.min.replace(tzinfo=tz.utc))
        # Adjust the start datetime to Monday or Sunday of the current week
        sub_days = 0
        if FIRST_DAY_OF_WEEK == 1:
            # The week begins on Monday
            sub_days = start.isoweekday() - 1
        else:
            # The week begins on Sunday
            sub_days = start.isoweekday()
            if sub_days == 7:
                sub_days = 0
        if sub_days > 0:
            start = start - datetime.timedelta(days=sub_days)
        end = start + datetime.timedelta(days=7)
        return start, end

    def __unicode__(self):
        from django.template.defaultfilters import date
        return "%s - %s" % (date(self.start, settings.DATE_FORMAT), date(self.end, settings.DATE_FORMAT))


class Day(Period):

    def __init__(self, events, date=None, parent_persisted_occurrences=None, occurrence_pool=None):

        if date is None:
            date = tz.now()
        start, end = self._get_day_range(date)
        super(Day, self).__init__(events, start, end, parent_persisted_occurrences, occurrence_pool)

    def _get_day_range(self, date):
        if isinstance(date, datetime.datetime):
            date = date.date()
        start = datetime.datetime.combine(date, datetime.time.min.replace(tzinfo=tz.utc))
        end = start + datetime.timedelta(days=1)
        return start, end

    def is_today(self):
        if self.start.date() == datetime.date.today():
            return True
        else:
            return False

    def __unicode__(self):
        from django.template.defaultfilters import date
        return date(self.start, "l, %s" % settings.DATE_FORMAT)

    def is_past(self):
        date = datetime.datetime.now()
        start = datetime.datetime.combine(date.date(), datetime.time.min)
        return self.start < start

    def prev_day(self):
        return Day(self.events, self.start - datetime.timedelta(days=1))
    prev = prev_day

    def next_day(self):
        return Day(self.events, self.end)
    next = next_day

    def current_year(self):
        return Year(self.events, self.start)

    def current_month(self):
        return Month(self.events, self.start)

    def current_week(self):
        return Week(self.events, self.start)
