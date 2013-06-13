from django.contrib import admin

from quotes.models import Quote


class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_abbr', )
    ordering = ('quote', )

    def quote_abbr(self, obj):
        return obj.quote[:20] + u"..."

admin.site.register(Quote, QuoteAdmin)
