var app = app || {};

app.Event = Backbone.Model.extend({
    defaults: {
        start: function(){ return new Date(); },
        title: "New Event",
        description: "",
        daterange: function(){ return this.dateRange(); }
    },
    initialize: function(attributes, options) {
        var _this = this;
        _.bindAll(this);
        var end = attributes.end,
            start= attributes.start;
        if ((typeof end === 'undefined') || (end === null)){
            var d = new Date();
            if (typeof start !== 'undefined') {
                d = new Date(start);
            }
            d.setHours(d.getHours() + 1);
            this.set("end", d.toISOString());
        }
        if ((this.get('daterange') === "") || (typeof this.daterange === 'undefined')) {
            this.set("daterange", this.dateRange());
        }
    },
    dateRange: function() {
        var start, end, out, allDay;
        if (typeof this.attributes !== 'undefined'){
            start = new Date(this.attributes.start);
            end = new Date(this.attributes.end);
            out = "";
            allDay = false;
        } else {
            start = new Date(this.start);
            end = new Date(this.end);
            out = "";
            allDay = this.allDay;
        }
        if (this.attributes.allDay) {
            out = $.fullCalendar.formatDates(start, end, "ddd, MMM d{[ - ddd, MMM d]}");
        } else {
            out = $.fullCalendar.formatDates(start, end, "ddd, MMM d h:mm[ tt] - {[ddd, MMM d ]h:mm tt }");
        }
        return out;
    }
});

app.Events = Backbone.Collection.extend({
    model: app.Event
});
