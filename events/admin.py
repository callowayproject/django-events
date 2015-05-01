from django.contrib import admin
from admin_views.admin import AdminViews

from audience.widgets import AdminBitFieldWidget
from bitfield import BitField

from .genericcollection import GenericCollectionTabularInline
from .models import Calendar, Event, CalendarRelation, EventRelation, Rule
from .forms import RuleForm, EventAdminForm


class CalendarRelationInline(GenericCollectionTabularInline):
    model = CalendarRelation

    class Media:
        js = ('events/genericcollections.js', )


class CalendarAdminOptions(AdminViews):
    admin_views = (('Calendar View', '/admin/events/calendarview/'), )
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']
    inlines = [CalendarRelationInline]


class EventRelationInline(GenericCollectionTabularInline):
    model = EventRelation


class EventAdmin(admin.ModelAdmin):
    search_fields = ('title', )
    list_display = ('title', 'start', 'end', 'all_day', 'rule')
    list_filter = ('start', 'end', 'all_day', 'rule')
    date_hierarchy = 'start'
    fieldsets = (
        (None, {
            'fields': ('calendar', 'appropriate_for', 'title', 'description')
        }),
        ('Schedule', {
            'fields': (('start', 'end', 'all_day'), ('rule', 'end_recurring_period'))
        }),
        ('Creator Info', {
            'fields': ('creator', 'created_on'),
            'classes': ('collapse', )
        })
    )
    readonly_fields = ('created_on', )
    inlines = [EventRelationInline]
    form = EventAdminForm

    def response_change(self, request, obj):
        from django.utils.html import escape
        from django.http import HttpResponse
        pk_value = obj._get_pk_val()
        if "_popup" in request.POST:
            return HttpResponse(
                '<!DOCTYPE html><html><head><title></title></head><body>'
                '<script type="text/javascript">opener.application.editEventCallback(window, "%s", "%s");</script></body></html>' % \
                # escape() calls force_unicode.
                (escape(pk_value), escape(obj.calendar.slug)))
        return super(EventAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change, *args, **kwargs):
        if getattr(obj, 'creator', None) is None:
            obj.creator = request.user
        super(EventAdmin, self).save_model(request, obj, form, change, *args, **kwargs)

    formfield_overrides = {
        BitField: {
            'initial': 1,
            'widget': AdminBitFieldWidget()
        }
    }

    class Media:
        js = ('events/genericcollections.js', )


class RuleAdmin(admin.ModelAdmin):
    form = RuleForm


admin.site.register(Rule, RuleAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Calendar, CalendarAdminOptions)
