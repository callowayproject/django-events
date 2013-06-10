from django.contrib import admin

from .genericcollection import GenericCollectionTabularInline
from .models import Calendar, Event, CalendarRelation, EventRelation, Rule
from .forms import RuleForm, EventAdminForm


class CalendarRelationInline(GenericCollectionTabularInline):
    model = CalendarRelation


class CalendarAdminOptions(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']
    inlines = [CalendarRelationInline]


class EventRelationInline(GenericCollectionTabularInline):
    model = EventRelation


class EventAdmin(admin.ModelAdmin):
    search_fields = ('title', )
    list_display = ('title', 'start', 'end', 'all_day', 'rule')
    list_filter = ('start', 'end', 'all_day', 'rule')
    fieldsets = (
        (None, {
            'fields': ('calendar', 'title', 'description')
        }),
        ('Schedule', {
            'fields': (('start', 'end', 'all_day'), ('rule', 'end_recurring_period'))
        }),
        ('Creator Info', {
            'fields': ('creator', 'created_on'),
            'classes': ('collapse', )
        })
    )
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


class RuleAdmin(admin.ModelAdmin):
    form = RuleForm


admin.site.register(Rule, RuleAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Calendar, CalendarAdminOptions)
