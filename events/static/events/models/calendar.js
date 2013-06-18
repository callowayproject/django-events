var app = app || {};

app.Calendar = Backbone.Model.extend({
    initialize: function() {
        var _this = this;
        _.bindAll(this);
        this.eventsurl = '/events/calendar/' + this.get('slug') + '/events/';
        this.events = new app.Events([], {url: this.eventsurl});
    },
    defaults: {
        checked: true
    },
    toggle: function() {
        this.set('checked', !this.get('checked'));
    },
    loadEvents: function(start, end) {
        var _this = this;

        if (this.get('checked')) {
            var data = {
                start: start.valueOf() / 1000,
                end: end.valueOf() / 1000
            };
            this.events.fetch({reset: true, data: data}).done(
                function() {
                    _this.eventSource = {
                        events: _this.events.toJSON(),
                        // borderColor: _this.get('color')[0],
                        // backgroundColor: _this.get('color')[1]
                        className: _this.get('className')
                    };
                    _this.trigger('eventsLoaded', _this.get('slug'), _this.eventSource);
                }
            );
        }
    },
    toEventSource: function() {
        return this.eventSource;
    }
});

app.CalendarList = Backbone.Collection.extend({
    model: app.Calendar,
    url: '/events/ajax/calendars/',
    getChecked: function(){
        return this.where({checked:true});
    }
});

app.Calendars = new app.CalendarList();
