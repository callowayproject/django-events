var app = app || {};

app.Event = Backbone.Model.extend({
    defaults: {
        start: function(){ return new Date(); },
        end: function(){ var d = new Date(); return d.setHours(d.getHours() + 1); },
        title: "New Event",
        description: ""
    },
    initialize: function(attributes, options) {
        this.set("daterange", this.dateRange());
    },
    dateRange: function() {
        var start = new Date(this.attributes.start),
            end = new Date(this.attributes.end),
            out = "";
        if (this.attributes.allDay) {
            out = $.fullCalendar.formatDates(start, end, "ddd, MMM d{[ - ddd, MMM d]}");
        } else {
            out = $.fullCalendar.formatDates(start, end, "ddd, MMM d h:mm[ tt] - {[ddd, MMM d ]h:mm tt }");
        }
        return out;
    }
});
