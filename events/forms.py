from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from events.models import Event, EventRelation, Occurrence

EventRelationFormSet = inlineformset_factory(Event, EventRelation)


class SpanForm(forms.ModelForm):

    start = forms.DateTimeField(widget=forms.SplitDateTimeWidget)
    end = forms.DateTimeField(widget=forms.SplitDateTimeWidget, help_text=_("The end time must be later than start time."))

    def clean(self):
        if not self.cleaned_data['all_day'] and self.cleaned_data['end'] <= self.cleaned_data['start']:
            self._errors["end"] = self.error_class(["The end time must be later than start time."])
        return self.cleaned_data


class EventForm(SpanForm):
    def __init__(self, hour24=False, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

    end_recurring_period = forms.DateTimeField(label='Ends on', help_text=_("This date is ignored for one time only events."), required=False)

    class Meta:
        model = Event
        exclude = ('creator', 'created_on', 'calendar')


class OccurrenceForm(SpanForm):

    class Meta:
        model = Occurrence
        exclude = ('original_start', 'original_end', 'event', 'cancelled')


class OccurrenceBackendForm(SpanForm):
    """
    used only for processing data (for ajax methods)
    """

    start = forms.DateTimeField()
    end = forms.DateTimeField()

    class Meta:
        model = Occurrence
        exclude = ('original_start', 'original_end', 'event', 'cancelled')


class EventBackendForm(SpanForm):

    start = forms.DateTimeField()
    end = forms.DateTimeField()
    end_recurring_period = forms.DateTimeField(required=False)

    class Meta:
        model = Event
        exclude = ('creator', 'created_on', 'calendar')
