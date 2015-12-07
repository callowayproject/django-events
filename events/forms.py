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


class EventAdminForm(forms.ModelForm):
    def clean(self):
        if not self.cleaned_data['all_day'] and self.cleaned_data['end'] <= self.cleaned_data['start']:
            self._errors["end"] = self.error_class(["The end time must be later than start time."])
        return self.cleaned_data

    class Meta:
        model = Event


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


class RuleForm(forms.ModelForm):
    params = forms.CharField(widget=forms.Textarea, help_text=_("Python rrule.rrule parameters like bysetpos:1;byweekday=5"))

    def clean_params(self):
        params = self.cleaned_data["params"]
        try:
            params = params.split(';')
            for param in params:
                param = param.split(':')
                if len(param) == 2:
                    param = (str(param[0]), [int(p) for p in param[1].split(',')])
                    if len(param[1]) == 1:
                        param = (param[0], param[1][0])
        except ValueError:
            raise forms.ValidationError(_("Params format looks invalid"))
        return self.cleaned_data["params"]


class ContentEventForm(forms.Form):
    start = forms.DateTimeField()
    content_type_id = forms.CharField()
    object_id = forms.IntegerField()
    calendar_id = forms.IntegerField(required=False)
