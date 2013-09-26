import datetime
import re
from django import template
from django.contrib.contenttypes.models import ContentType

from ..models import Event, EventRelation

register = template.Library()


class ScheduledContentNode(template.Node):
    def __init__(self, content_type, sched_date, context_var):
        if content_type[0] in ("'", '"'):
            self.app_label, self.model = content_type.replace("'", "").replace('"', '').split(".")
            self.content_type = None
        else:
            self.content_type = template.Variable(content_type)
        if isinstance(sched_date, (datetime.datetime, datetime.date)):
            self.sched_date = sched_date
        else:
            self.sched_date = template.Variable(sched_date)
        self.context_var = context_var

    def render(self, context):
        if self.content_type is not None:
            content_type = self.content_type.resolve(context)
            self.app_label, self.model = content_type.split(".")
        if not isinstance(self.sched_date, (datetime.datetime, datetime.date)):
            self.sched_date = self.sched_date.resolve(context)
        ctype = ContentType.objects.get_by_natural_key(self.app_label, self.model)
        # Get all Events for a specific day and their relations
        # if any relations is of the appropriate type, return it
        end_date = self.sched_date + datetime.timdelta(days=1)
        qset = Event.objects.filter(start__gte=self.sched_date).filter(start_lt=end_date)
        event_ids = qset.values_list('id', flat=True)
        event_rels = EventRelation.objects.filter(event__id__in=event_ids).filter(content_type=ctype)
        context[self.context_var] = [x.content_object for x in event_rels]
        return ''


def get_scheduled_content(parser, token):
    """
    {% get_scheduled_content 'app_name.model' [for <'YYYY-MM-DD' or date_variable>] as variable_name %}

    """
    contents = token.split_contents()
    if len(contents) == 4:  # No date specified. Use now()
        tag_name, content_type, _as, context_var = contents
        sched_date = datetime.date.today()
    elif len(contents) == 6:
        tag_name, content_type, _for, sched_date, _as, context_var = contents
        if re.match('\d{4}-\d{2}-\d{2}', sched_date):
            sched_date = datetime.datetime.strptime(sched_date, '%Y-%m-%d')
    else:
        raise template.TemplateSyntaxError, "%r usage: {%% %r 'app_name.model' [for <date>] as variable_name %%}" % (contents[0], contents[0])
    return ScheduledContentNode(content_type, sched_date, context_var)
